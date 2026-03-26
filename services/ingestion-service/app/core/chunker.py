from typing import List
from app.core.tokenizer import Tokenizer


class Chunker:
    """
    Abstracts the chunking process using the supplied tokenizer
    """

    def __init__(self, tokenizer: Tokenizer, max_tokens: int, overlap: int):
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
        self.overlap = overlap

    def split(self, text: str) -> List[str]:
        """
        Split text into overlapping character-based chunks.
        """
        tokens = self.tokenizer.encode(text)

        chunks = []
        start = 0

        while start < len(tokens):
            end = min(start + self.max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]

            chunks.append(self.tokenizer.decode(chunk_tokens))

            start += self.max_tokens - self.overlap

        return chunks
