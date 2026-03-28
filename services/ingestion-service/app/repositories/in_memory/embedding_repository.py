from typing import List

from app.repositories.base import EmbeddingRepository


class InMemoryEmbeddingRepository(EmbeddingRepository):
    def __init__(self):
        self.embeddings = {}

    def create_many(self, chunk_ids: List[str], embeddings: List[List[float]]) -> None:
        for chunk_id, vector in zip(chunk_ids, embeddings):
            self.embeddings[chunk_id] = vector
