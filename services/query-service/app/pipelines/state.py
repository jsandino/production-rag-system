from typing import Optional
from typing_extensions import TypedDict

from app.models.chunk_result import ChunkResult


class QueryState(TypedDict):
    # --- inputs ---
    query: str
    top_k: int
    filters: dict
    debug: bool

    # --- pipeline state ---
    query_embedding: Optional[list[float]]
    retrieved_chunks: list[ChunkResult]
    ranked_chunks: list[ChunkResult]

    # --- output ---
    answer: Optional[str]

    # --- observability ---
    timings: dict
