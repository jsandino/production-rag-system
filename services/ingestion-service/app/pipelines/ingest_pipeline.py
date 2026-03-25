from app.pipelines.chunking import chunk_text


def run_ingestion(document_id: str, text: str, metadata: dict) -> int:
    """
    Placeholder ingestion pipeline.

    Returns:
        int: number of chunks created
    """
    chunks = chunk_text(text)
    return len(chunks)
