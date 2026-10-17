
import re
import requests

from backend.services.rag.embeddings import EmbeddingService
from backend.services.rag.vector_store import VectorStore


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

REQUEST_TIMEOUT = 180
MAX_TOP_K = 4


# ============================================================
# SERVICE RAG
# ============================================================

class RAGService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    # ========================================================
    # DÉCOUPAGE DES DOCUMENTS
    # ========================================================

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

    # ========================================================
    # INDEXATION D'UN DOCUMENT
    # ========================================================

    def index_document(
        self,
        document_id: int,
        filename: str,
        text: str,
    ) -> int:

        chunks = self.split_text(text)

        if not chunks:
            raise ValueError(
                "Le document ne contient aucun texte exploitable."
            )

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

        # Supprimer les anciens passages du document
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

    # ========================================================
    # GÉNÉRATION DE RÉPONSE AVEC LE RAG
    # ========================================================

    def answer(
        self,
        question: str,
        top_k: int = 4,
        history: list[dict] | None = None,
    ) -> dict:

        question = question.strip()

        if not question:
            raise ValueError(
                "La question ne peut pas être vide."
            )

        # Vérifier que des documents sont indexés.
        if self.vector_store.count() == 0:
            return {
                "answer": "Aucun document n'est encore indexé.",
                "sources": [],
            }

        # ----------------------------------------------------
        # 1. Préparer l'historique
        # ----------------------------------------------------

        history = history or []

        recent_history = [
            item
            for item in history[-4:]
            if isinstance(item, dict)
            and item.get("content")
            and item.get("role") in {"user", "assistant"}
        ]

        history_text = "\n".join(
            f"{item['role']}: {item['content']}"
            for item in recent_history
        )

        search_question = question

        # ----------------------------------------------------
        # 2. Détecter les questions de suivi
        # ----------------------------------------------------

        follow_up_patterns = [
            r"\b(et pour|et concernant|qu'en est-il)\b",
            r"\b(ce document|ce dernier|cette dernière)\b",
            r"\b(celui-ci|celle-ci|ceux-ci|celles-ci)\b",
            r"\b(et lui|et elle|et eux)\b",
            r"\b(plus précisément|et ensuite|pour ce cas)\b",
            r"\b(son montant|sa date|son nom|ses conditions)\b",
        ]

        needs_rewrite = (
            bool(
                re.search(
                    "|".join(
                        f"(?:{pattern})"
                        for pattern in follow_up_patterns
                    ),
                    question.lower(),
                )
            )
            and bool(history_text)
        )

        # ----------------------------------------------------
        # 3. Reformuler les questions de suivi si nécessaire
        # ----------------------------------------------------

        if needs_rewrite:

            rewrite_prompt = f"""
Reformule la dernière question en une question autonome.
Utilise l'historique pour comprendre les références.
N'ajoute aucun fait et ne réponds pas à la question.
Retourne uniquement la question reformulée.

HISTORIQUE :
{history_text}

DERNIÈRE QUESTION :
{question}

QUESTION AUTONOME :
""".strip()

            try:
                rewrite_response = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": rewrite_prompt,
                        "stream": False,
                        "keep_alive": "10m",
                        "options": {
                            "temperature": 0,
                            "num_predict": 64,
                            "num_ctx": 2048,
                        },
                    },
                    timeout=60,
                )

                rewrite_response.raise_for_status()

                rewritten = (
                    rewrite_response.json()
                    .get("response", "")
                    .strip()
                )

                if rewritten and len(rewritten) <= 500:
                    search_question = rewritten

            except requests.RequestException:
                # Continuer avec la question originale
                # si Ollama ne peut pas reformuler.
                search_question = question

        # ----------------------------------------------------
        # 4. Recherche vectorielle
        # ----------------------------------------------------

        effective_top_k = max(
            1,
            min(int(top_k), MAX_TOP_K),
        )

        query_embedding = (
            self.embedding_service.encode_query(
                search_question
            )
        )

        results = self.vector_store.search(
            query_embedding,
            top_k=effective_top_k,
        )

        if not results:
            return {
                "answer": (
                    "Je n'ai pas trouvé d'information pertinente "
                    "dans les documents disponibles."
                ),
                "sources": [],
            }

        # ----------------------------------------------------
        # 5. Construire le contexte et les sources
        # ----------------------------------------------------

        context_parts = []
        sources = []

        for result in results:
            metadata = result.get("metadata") or {}

            source = metadata.get(
                "source",
                "Source inconnue",
            )

            chunk_index = metadata.get(
                "chunk_index",
                -1,
            )

            text = result.get("text", "").strip()

            if not text:
                continue

            context_parts.append(
                f"[Document : {source} | "
                f"Passage : {chunk_index}]\n{text}"
            )

            # Garder le format des sources utilisé par le projet.
            source_info = {
                "source": source,
                "chunk_index": chunk_index,
            }

            if result.get("distance") is not None:
                source_info["distance"] = round(
                    result["distance"],
                    4,
                )

            sources.append(source_info)

        if not context_parts:
            return {
                "answer": (
                    "Je n'ai pas trouvé de texte exploitable "
                    "dans les passages récupérés."
                ),
                "sources": [],
            }

        context = "\n\n".join(context_parts)

        # ----------------------------------------------------
        # 6. Préparer le prompt final
        # ----------------------------------------------------

        prompt = f"""
Tu es Smart University Assistant,
un assistant universitaire intelligent.

Réponds en français à la question en utilisant
les informations du contexte documentaire.

L'historique sert uniquement à comprendre la question.
Les faits de ta réponse doivent être confirmés
par le contexte documentaire.

RÈGLES :
- N'invente aucune information.
- Si le contexte ne permet pas de répondre,
  dis-le clairement.
- Cite le nom du document utilisé lorsque c'est pertinent.
- Réponds directement et de manière concise.
- Si une information précise est absente du contexte,
  indique qu'elle n'est pas disponible.

HISTORIQUE :
{history_text or "Aucun historique précédent."}

CONTEXTE DOCUMENTAIRE :
{context}

QUESTION :
{question}

RÉPONSE :
""".strip()

        # ----------------------------------------------------
        # 7. Générer la réponse avec Ollama
        # ----------------------------------------------------

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "keep_alive": "10m",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 256,
                    "num_ctx": 4096,
                },
            },
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        answer_text = data.get(
            "response",
            "",
        ).strip()

        if not answer_text:
            answer_text = (
                "Le modèle n'a pas généré de réponse. "
                "Réessaie avec une question plus précise."
            )

        # ----------------------------------------------------
        # 8. Retourner la réponse et les sources
        # ----------------------------------------------------

        return {
            "answer": answer_text,
            "sources": sources,
        }
