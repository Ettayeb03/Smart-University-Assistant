
from backend.services.rag.embeddings import EmbeddingService
from backend.services.rag.vector_store import VectorStore


def main():
    print("1. Chargement du modèle...")
    embedding_service = EmbeddingService()

    texts = [
        "Les inscriptions universitaires commencent en septembre.",
        "Le football est un sport collectif pratiqué avec un ballon.",
        "Les examens se déroulent à la fin de chaque semestre.",
    ]

    embeddings = embedding_service.encode_texts(texts)

    print("2. Indexation dans ChromaDB...")
    store = VectorStore(collection_name="test_documents")

    store.add_chunks(
        ids=["test_1", "test_2", "test_3"],
        texts=texts,
        embeddings=embeddings,
        metadatas=[
            {"source": "inscriptions.txt"},
            {"source": "sport.txt"},
            {"source": "examens.txt"},
        ],
    )

    print(f"Passages indexés : {store.count()}")

    questions = [
        "À quelle période les étudiants s'inscrivent-ils ?",
        "Quand commencent les inscriptions universitaires ?",
        "À quel moment ont lieu les examens ?",
    ]

    for question in questions:
        query_embedding = embedding_service.encode_query(question)
        results = store.search(query_embedding, top_k=3)

        print(f"\nQuestion : {question}")

        for rank, result in enumerate(results, start=1):
            print(
                f"{rank}. {result['text']}\n"
                f"   Source : {result['metadata'].get('source')}\n"
                f"   Distance : {result['distance']:.4f}"
            )

    print("\nTest des recherches : terminé")


if __name__ == "__main__":
    main()
