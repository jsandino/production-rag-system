from app.core.chunker import Chunker
from app.core.embedder import Embedder


def run_ingestion(
    document_id: str, text: str, metadata: dict, chunker: Chunker, embedder: Embedder
) -> int:
    """
    Placeholder ingestion pipeline.

    Returns:
        int: number of chunks created
    """
    chunks = chunker.split(text)

    embeddings = embedder.embed(chunks)

    return len(embeddings)
