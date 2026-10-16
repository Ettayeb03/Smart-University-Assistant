
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

    def encode_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embeddings.tolist()

    def encode_query(self, query: str) -> list[float]:
        return self.encode_texts([query])[0]
