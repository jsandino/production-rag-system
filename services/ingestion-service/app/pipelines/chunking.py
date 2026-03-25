from typing import List
import tiktoken


def chunk_text(
    text: str, chunk_size: int = 500, overlap: int = 100, model: str = "gpt-4o-mini"
) -> List[str]:
    """Token-based chunking using tiktoken"""

    encoding = tiktoken.encoding_for_model(model)

    tokens = encoding.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]

        chunk = encoding.decode(chunk_tokens)
        chunks.append(chunk)

        start = end - overlap

    return chunks
