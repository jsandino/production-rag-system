from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Simple character-based chunking (MVP )"""
    chunks = []
    start = 0
    text_len = len(text)
    print(f"text_len: {text_len}")
    while start < text_len:
        end = start + chunk_size
        new_chunk = text[start:end]
        chunks.append(new_chunk)
        start = end - overlap

    return chunks
