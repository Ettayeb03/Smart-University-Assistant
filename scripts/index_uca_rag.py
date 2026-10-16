import json
from pathlib import Path

from backend.services.rag.embeddings import EmbeddingService
from backend.services.rag.vector_store import VectorStore
from backend.services.rag.rag_service import RAGService

DATA_PATH = Path("data/uca/uca_rag_documents.jsonl")


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {DATA_PATH}")

    documents = []
    with DATA_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if line.strip():
                try:
                    documents.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"JSON invalide à la ligne {line_number}"
                    ) from exc

    print(f"Documents chargés : {len(documents)}")

    chunks_to_index = []

    for doc in documents:
        document_id = doc["document_id"]
        title = doc["title"]
        content = doc.get("content", "").strip()

        if not content:
            print(f"Document ignoré (contenu vide) : {document_id}")
            continue

        chunks = RAGService.split_text(content)

        for index, chunk in enumerate(chunks):
            chunks_to_index.append({
                "id": f"uca_{document_id}_chunk_{index}",
                "text": chunk,
                "metadata": {
                    "document_id": document_id,
                    "source": title,
                    "source_url": doc.get("source_url", ""),
                    "title": title,
                    "category": doc.get("category", "unknown"),
                    "language": doc.get("language", "fr"),
                    "validity": doc.get("validity", ""),
                    "chunk_index": index,
                },
            })

    if not chunks_to_index:
        raise ValueError("Aucun passage exploitable trouvé.")

    print(f"Passages à indexer : {len(chunks_to_index)}")
    print("Calcul des embeddings...")

    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    texts = [item["text"] for item in chunks_to_index]
    embeddings = embedding_service.encode_texts(texts)

    vector_store.add_chunks(
        ids=[item["id"] for item in chunks_to_index],
        texts=texts,
        embeddings=embeddings,
        metadatas=[item["metadata"] for item in chunks_to_index],
    )

    print("Indexation terminée.")
    print("Collection :", vector_store.collection.name)
    print("Total de passages dans ChromaDB :", vector_store.count())


if __name__ == "__main__":
    main()
