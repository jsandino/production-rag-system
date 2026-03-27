from typing import List
from uuid import uuid4

from app.repositories.base import (
    DocumentRepository,
    ChunkRepository,
    EmbeddingRepository,
)


class InMemoryDocumentRepository(DocumentRepository):
    def __init__(self):
        self.documents = {}

    def create(self, metadata: dict) -> str:
        document_id = str(uuid4())
        self.documents[document_id] = metadata
        return document_id


class InMemoryChunkRepository(ChunkRepository):
    def __init__(self):
        self.chunks = {}

    def create_many(self, document_id: str, chunks: List[str]) -> List[str]:
        chunk_ids = []

        for idx, content in enumerate(chunks):
            chunk_id = str(uuid4())
            self.chunks[chunk_id] = {
                "document_id": document_id,
                "content": content,
                "index": idx,
            }
            chunk_ids.append(chunk_id)

        return chunk_ids


class InMemoryEmbeddingRepository(EmbeddingRepository):
    def __init__(self):
        self.embeddings = {}

    def create_many(
        self, chunk_ids: List[str], embeddings: List[List[float]]
    ) -> None:
        for chunk_id, vector in zip(chunk_ids, embeddings):
            self.embeddings[chunk_id] = vector