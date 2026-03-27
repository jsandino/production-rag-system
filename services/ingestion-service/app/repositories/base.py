from typing import Protocol, List


class DocumentRepository(Protocol):
    def create(self, metadata: dict) -> str:
        """Create a document and return its ID"""


class ChunkRepository(Protocol):
    def create_many(
        self,
        document_id: str,
        chunks: List[str],
    ) -> List[str]:
        """Persist chunks and return their IDs"""


class EmbeddingRepository(Protocol):
    def create_many(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
    ) -> None:
        """Persist embeddings for given chunks"""
