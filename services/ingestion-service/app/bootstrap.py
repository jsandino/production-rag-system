from app.pipelines.ingest_pipeline import IngestionPipeline
from app.core.text_tools import TextTools
from app.core.providers.openai_text_tools import OpenAITextTools

from app.repositories.in_memory import (
    InMemoryDocumentRepository,
    InMemoryChunkRepository,
    InMemoryEmbeddingRepository,
)


def create_ingestion_pipeline() -> IngestionPipeline:
    """
    Composition root for the ingestion pipeline.
    """

    # Cohesive domain tools (already aligned)
    text_tools: TextTools = OpenAITextTools.create()

    # Repositories (temporary in-memory)
    document_repository = InMemoryDocumentRepository()
    chunk_repository = InMemoryChunkRepository()
    embedding_repository = InMemoryEmbeddingRepository()

    return IngestionPipeline(
        chunker=text_tools.chunker,
        embedder=text_tools.embedder,
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
    )
