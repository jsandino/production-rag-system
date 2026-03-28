from app.pipelines.ingest_pipeline import IngestionPipeline
from app.core.text_tools import TextTools
from app.core.providers.openai_text_tools import OpenAITextTools
from app.repositories.postgres.chunk_repository import PostgresChunkRepository
from app.repositories.postgres.document_repository import PostgresDocumentRepository
from app.repositories.postgres.embedding_repository import PostgresEmbeddingRepository


def create_ingestion_pipeline() -> IngestionPipeline:
    """
    Composition root for the ingestion pipeline.
    """

    # Cohesive domain tools (already aligned)
    text_tools: TextTools = OpenAITextTools.create()

    document_repository = PostgresDocumentRepository()
    chunk_repository = PostgresChunkRepository()
    embedding_repository = PostgresEmbeddingRepository()

    return IngestionPipeline(
        chunker=text_tools.chunker,
        embedder=text_tools.embedder,
        document_repository=document_repository,
        chunk_repository=chunk_repository,
        embedding_repository=embedding_repository,
    )
