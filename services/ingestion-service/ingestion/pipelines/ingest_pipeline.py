import logging
from typing import Callable

from ingestion.core.chunker import Chunker
from ingestion.core.embedder import Embedder
from ingestion.db.unit_of_work import UnitOfWork
from shared.telemetry import traced

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        chunker: Chunker,
        embedder: Embedder,
        uow_factory: Callable,
    ):
        self.chunker = chunker
        self.embedder = embedder
        self.uow_factory = uow_factory

    @traced("ingestion.run")
    def run(self, text: str, name: str, metadata: dict) -> int:
        logger.info("Ingestion started", extra={"document_name": name})
        with self.uow_factory() as uow:
            document_id = self._create_document(uow, name, metadata)
            chunks = self._chunk_text(text)
            chunk_ids = self._persist_chunks(uow, document_id, chunks)
            embeddings = self._generate_embeddings(chunks)
            self._persist_embeddings(uow, chunk_ids, embeddings)

        logger.info("Ingestion complete", extra={"document_name": name, "chunks": len(embeddings)})
        return len(embeddings)

    @traced("ingestion.create_document")
    def _create_document(self, uow, name: str, metadata: dict) -> str:
        return uow.documents.create(name=name, metadata=metadata)

    @traced("ingestion.chunk_text")
    def _chunk_text(self, text: str) -> list:
        return self.chunker.split(text)

    @traced("ingestion.persist_chunks")
    def _persist_chunks(self, uow, document_id: str, chunks: list) -> list:
        return uow.chunks.create_many(document_id, chunks)

    @traced("ingestion.generate_embeddings")
    def _generate_embeddings(self, chunks: list) -> list:
        return self.embedder.embed(chunks)

    @traced("ingestion.persist_embeddings")
    def _persist_embeddings(self, uow, chunk_ids: list, embeddings: list) -> None:
        uow.embeddings.create_many(chunk_ids, embeddings)


def make_pipeline(chunker: Chunker, embedder: Embedder, dsn: str) -> "IngestionPipeline":
    return IngestionPipeline(
        chunker=chunker,
        embedder=embedder,
        uow_factory=lambda: UnitOfWork(dsn),
    )
