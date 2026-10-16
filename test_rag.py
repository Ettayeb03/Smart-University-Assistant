
from backend.services.rag.rag_service import RAGService


def main():
    print("Initialisation du RAG...")
    rag = RAGService()

    document_text = """
    Guide des inscriptions universitaires 2026.

    Les inscriptions universitaires commencent le 7 septembre 2026.
    Les étudiants doivent présenter une copie de leur carte nationale
    d'identité et leur attestation de réussite.
    Le dépôt du dossier se fait au service de scolarité.
    Les examens du premier semestre commencent le 12 janvier 2027.
    """

    print("Indexation du document de test...")
    chunks = rag.index_document(
        document_id=999999,
        filename="guide_inscriptions_test.txt",
        text=document_text,
    )

    print(f"Passages indexés : {chunks}")

    question = "Quand commencent les inscriptions universitaires ?"

    print(f"\nQuestion : {question}")
    print("Génération de la réponse...")

    result = rag.answer(question)

    print("\nRéponse :")
    print(result["answer"])

    print("\nSources récupérées :")
    for source in result["sources"]:
        print(
            f"- {source['source']} | "
            f"passage {source['chunk_index']} | "
            f"distance {source['distance']}"
        )


if __name__ == "__main__":
    main()
