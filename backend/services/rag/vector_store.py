
from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHROMA_PATH = PROJECT_ROOT / "storage" / "rag" / "chroma"


class VectorStore:
    def __init__(self, collection_name: str = "university_documents"):
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None = None,
    ) -> None:
        if not ids:
            return

        if not (len(ids) == len(texts) == len(embeddings)):
            raise ValueError(
                "Les listes ids, texts et embeddings "
                "doivent avoir la même longueur."
            )

        if metadatas is None:
            metadatas = [{} for _ in texts]

        if len(metadatas) != len(texts):
            raise ValueError(
                "La liste metadatas doit avoir la même longueur."
            )

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[dict]:
        if top_k < 1:
            raise ValueError("top_k doit être supérieur ou égal à 1.")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, max(1, self.collection.count())),
            include=["documents", "metadatas", "distances"],
        )

        matches = []

        for i, document in enumerate(results["documents"][0]):
            matches.append({
                "text": document,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

        return matches

    def count(self) -> int:
        return self.collection.count()
