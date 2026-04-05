from dataclasses import dataclass


@dataclass
class ChunkResult:
    chunk_id: str
    document_id: str
    document_name: str
    content: str
    score: float
