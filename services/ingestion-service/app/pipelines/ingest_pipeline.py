from app.pipelines.chunking import chunk_text
from app.core.embedding import EmbeddingService


def run_ingestion(
    document_id: str,
    text: str,
    metadata: dict,
    embedding_service: EmbeddingService,
) -> int:
    """
    Placeholder ingestion pipeline.

    Returns:
        int: number of chunks created
    """
    chunks = chunk_text(text)

    embeddings = embedding_service.embed(chunks)

    return len(embeddings)
