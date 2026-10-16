
import requests

from backend.services.rag.embeddings import EmbeddingService
from backend.services.rag.vector_store import VectorStore


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    @staticmethod
    def split_text(text: str) -> list[str]:
        text = " ".join(text.split())

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(text):
                break

            start = end - CHUNK_OVERLAP

        return chunks

    def index_document(
        self,
        document_id: int,
        filename: str,
        text: str,
    ) -> int:
        chunks = self.split_text(text)

        if not chunks:
            raise ValueError("Le document ne contient aucun texte.")

        ids = [
            f"doc_{document_id}_chunk_{i}"
            for i in range(len(chunks))
        ]

        embeddings = self.embedding_service.encode_texts(chunks)

        metadatas = [
            {
                "document_id": document_id,
                "source": filename,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]

        # Supprimer les anciens passages de ce document
        # avant de réindexer sa nouvelle version.
        try:
            self.vector_store.collection.delete(
                where={"document_id": document_id}
            )
        except Exception:
            pass

        self.vector_store.add_chunks(
            ids=ids,
            texts=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def answer(
        self,
        question: str,
        top_k: int = 4,
        history: list[dict] | None = None,
    ) -> dict:
        question = question.strip()

        if not question:
            raise ValueError("La question ne peut pas ?tre vide.")

        if self.vector_store.count() == 0:
            return {
                "answer": "Aucun document n'est encore index?.",
                "sources": [],
            }

        history = history or []
        history_text = "\n".join(
            f"{item.get('role', 'user')}: {item.get('content', '')}"
            for item in history[-6:]
            if item.get("content")
            and item.get("role") in {"user", "assistant"}
        )

        search_question = question

        if history_text:
            rewrite_prompt = f"""
Tu aides un moteur de recherche universitaire.
Reformule la derni?re question en une seule question autonome,
en utilisant l'historique pour comprendre les r?f?rences.
N'apporte aucune r?ponse et n'ajoute aucun fait.

HISTORIQUE :
{history_text}

DERNI?RE QUESTION :
{question}

QUESTION AUTONOME :
""".strip()

            rewrite_response = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": rewrite_prompt,
                    "stream": False,
                    "options": {"temperature": 0.0},
                },
                timeout=180,
            )
            rewrite_response.raise_for_status()
            rewritten = rewrite_response.json().get("response", "").strip()

            if rewritten and len(rewritten) <= 500:
                search_question = rewritten

        query_embedding = self.embedding_service.encode_query(search_question)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        if not results:
            return {
                "answer": "Je n'ai pas trouv? d'information pertinente.",
                "sources": [],
            }

        context_parts = []
        sources = []

        for result in results:
            metadata = result["metadata"] or {}
            source = metadata.get("source", "Source inconnue")
            chunk_index = metadata.get("chunk_index", -1)

            context_parts.append(
                f"[Source : {source} | Passage : {chunk_index}]\n"
                f"{result['text']}"
            )

            sources.append({
                "source": source,
                "chunk_index": chunk_index,
                "distance": round(result["distance"], 4),
            })

        context = "\n\n".join(context_parts)

        prompt = f"""
Tu es Smart University Assistant, un assistant universitaire.
R?ponds en fran?ais ? la derni?re question en utilisant les informations
du CONTEXTE DOCUMENTAIRE. L'historique aide ? comprendre la question,
mais les faits doivent ?tre confirm?s par le contexte documentaire.

R?gles :
- Ne fabrique aucune information.
- Si le contexte ne permet pas de r?pondre, indique-le clairement.
- Cite le nom du document utilis?.

HISTORIQUE :
{history_text or "Aucun historique pr?c?dent."}

CONTEXTE DOCUMENTAIRE :
{context}

DERNI?RE QUESTION :
{question}

R?PONSE :
""".strip()

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=180,
        )
        response.raise_for_status()

        data = response.json()

        return {
            "answer": data["response"].strip(),
            "sources": sources,
        }