from typing import List
from uuid import uuid4

from app.repositories.base import ChunkRepository


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
