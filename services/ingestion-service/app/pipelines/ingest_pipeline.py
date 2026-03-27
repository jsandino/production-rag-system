from app.core.chunker import Chunker
from app.core.embedder import Embedder
from app.repositories.base import (
    DocumentRepository,
    ChunkRepository,
    EmbeddingRepository,
)


class IngestionPipeline:
    def __init__(
        self,
        chunker: Chunker,
        embedder: Embedder,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        embedding_repository: EmbeddingRepository,
    ):
        self.chunker = chunker
        self.embedder = embedder
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.embedding_repository = embedding_repository

    def run(self, text: str, metadata: dict) -> int:
        # 1. Create document
        document_id = self.document_repository.create(metadata)

        # 2. Chunk text
        chunks = self.chunker.split(text)

        # 3. Persist chunks
        chunk_ids = self.chunk_repository.create_many(document_id, chunks)

        # 4. Generate embeddings
        embeddings = self.embedder.embed(chunks)

        # 5. Persist embeddings
        self.embedding_repository.create_many(chunk_ids, embeddings)

        return len(embeddings)