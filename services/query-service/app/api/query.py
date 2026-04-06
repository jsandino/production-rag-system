from functools import lru_cache
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.providers.openai_embedder import OpenAIEmbedder
from app.core.providers.openai_generator import OpenAIGenerator
from app.db.connection import get_connection
from app.pipelines.query_pipeline import QueryPipeline
from app.repositories.postgres.chunk_repository import PostgresChunkRepository

router = APIRouter()


@lru_cache
def query_pipeline() -> QueryPipeline:
    # lru_cache means this connection is created once and reused for the
    # lifetime of the process. This is acceptable for a single-worker dev
    # server, but should be replaced with a connection pool (e.g. psycopg_pool)
    # for production multi-worker deployments.
    conn = get_connection()
    return QueryPipeline(
        embedder=OpenAIEmbedder(),
        chunk_repository=PostgresChunkRepository(conn),
        generator=OpenAIGenerator(),
    )


# --- request / response models ---

class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    filters: Dict[str, Any] = {}
    debug: bool = False


class SourceItem(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    text: str
    score: float


class DebugInfo(BaseModel):
    embedding_ms: int
    retrieval_ms: int
    generation_ms: int
    retrieved_chunks: List[SourceItem]
    ranked_chunks: List[SourceItem]


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    debug: Optional[DebugInfo] = None


# --- endpoint ---

@router.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    pipeline: QueryPipeline = Depends(query_pipeline),
):
    state = pipeline.run(
        query=request.query,
        top_k=request.top_k,
        filters=request.filters,
        debug=request.debug,
    )

    sources = [
        SourceItem(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            document_name=c.document_name,
            text=c.content,
            score=c.score,
        )
        for c in state["ranked_chunks"]
    ]

    debug_info = None
    if request.debug:
        timings = state["timings"]
        debug_info = DebugInfo(
            embedding_ms=timings.get("embedding_ms", 0),
            retrieval_ms=timings.get("retrieval_ms", 0),
            generation_ms=timings.get("generation_ms", 0),
            retrieved_chunks=[
                SourceItem(
                    chunk_id=c.chunk_id,
                    document_id=c.document_id,
                    document_name=c.document_name,
                    text=c.content,
                    score=c.score,
                )
                for c in state["retrieved_chunks"]
            ],
            ranked_chunks=sources,
        )

    return QueryResponse(
        answer=state["answer"],
        sources=sources,
        debug=debug_info,
    )
