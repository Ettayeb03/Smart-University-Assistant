
from backend.services.rag.embeddings import EmbeddingService


def main():
    print("Chargement du modèle d'embeddings...")
    service = EmbeddingService()

    texts = [
        "Les inscriptions universitaires commencent en septembre.",
        "Le football est un sport collectif.",
        "Les examens ont lieu à la fin du semestre.",
    ]

    vectors = service.encode_texts(texts)
    query_vector = service.encode_query(
        "Quand commencent les inscriptions à l'université ?"
    )

    print(f"Nombre de vecteurs : {len(vectors)}")
    print(f"Dimension d'un vecteur : {len(vectors[0])}")
    print(f"Dimension de la question : {len(query_vector)}")
    print("Test des embeddings : OK")


if __name__ == "__main__":
    main()
