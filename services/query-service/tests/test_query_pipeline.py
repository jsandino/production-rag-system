from query.models.chunk_result import ChunkResult
from query.pipelines.query_pipeline import QueryPipeline


class FakeEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeGenerator:
    def generate(self, query: str, context: str) -> str:
        return f"answer to: {query}"


class FakeChunkRepository:
    def __init__(self, chunks: list[ChunkResult]):
        self._chunks = chunks

    def search(self, embedding: list[float], top_k: int) -> list[ChunkResult]:
        return self._chunks[:top_k]


def make_chunk(score: float, chunk_id: str = "c1") -> ChunkResult:
    return ChunkResult(
        chunk_id=chunk_id,
        document_id="doc1",
        document_name="doc.txt",
        content="some content",
        score=score,
    )


def make_pipeline(chunks: list[ChunkResult]) -> QueryPipeline:
    return QueryPipeline(
        embedder=FakeEmbedder(),
        chunk_repository=FakeChunkRepository(chunks),
        generator=FakeGenerator(),
    )


# --- embed node ---


def test_embed_sets_query_embedding():
    pipeline = make_pipeline([make_chunk(score=0.9)])
    result = pipeline.run(query="what is RAG?", top_k=1, filters={}, debug=False)
    assert result["query_embedding"] == [0.1, 0.2, 0.3]


# --- retrieve node ---


def test_retrieve_respects_top_k():
    chunks = [make_chunk(score=0.9, chunk_id=f"c{i}") for i in range(5)]
    pipeline = make_pipeline(chunks)
    result = pipeline.run(query="q", top_k=3, filters={}, debug=False)
    assert len(result["retrieved_chunks"]) == 3


# --- rank node ---


def test_rank_keeps_chunks_above_threshold():
    chunks = [make_chunk(score=0.8), make_chunk(score=0.6, chunk_id="c2")]
    pipeline = make_pipeline(chunks)
    result = pipeline.run(query="q", top_k=2, filters={}, debug=False)
    assert all(c.score >= 0.5 for c in result["ranked_chunks"])
    assert len(result["ranked_chunks"]) == 2


def test_rank_drops_chunks_below_threshold():
    chunks = [make_chunk(score=0.9), make_chunk(score=0.3, chunk_id="c2")]
    pipeline = make_pipeline(chunks)
    result = pipeline.run(query="q", top_k=2, filters={}, debug=False)
    assert len(result["ranked_chunks"]) == 1
    assert result["ranked_chunks"][0].score == 0.9


def test_rank_exactly_at_threshold_is_kept():
    pipeline = make_pipeline([make_chunk(score=0.5)])
    result = pipeline.run(query="q", top_k=1, filters={}, debug=False)
    assert len(result["ranked_chunks"]) == 1


def test_rank_fallback_to_top_one_when_all_below_threshold():
    chunks = [make_chunk(score=0.2), make_chunk(score=0.1, chunk_id="c2")]
    pipeline = make_pipeline(chunks)
    result = pipeline.run(query="q", top_k=2, filters={}, debug=False)
    assert len(result["ranked_chunks"]) == 1
    assert result["ranked_chunks"][0].chunk_id == "c1"


def test_rank_empty_retrieval_produces_no_ranked_chunks():
    pipeline = make_pipeline([])
    result = pipeline.run(query="q", top_k=5, filters={}, debug=False)
    assert result["ranked_chunks"] == []


# --- generate node ---


def test_generate_sets_answer():
    pipeline = make_pipeline([make_chunk(score=0.9)])
    result = pipeline.run(query="what is RAG?", top_k=1, filters={}, debug=False)
    assert result["answer"] == "answer to: what is RAG?"


# --- full pipeline state ---


def test_run_populates_timings():
    pipeline = make_pipeline([make_chunk(score=0.9)])
    result = pipeline.run(query="q", top_k=1, filters={}, debug=False)
    assert "embedding_ms" in result["timings"]
    assert "retrieval_ms" in result["timings"]
    assert "generation_ms" in result["timings"]


def test_run_preserves_query_in_state():
    pipeline = make_pipeline([make_chunk(score=0.9)])
    result = pipeline.run(query="original query", top_k=1, filters={}, debug=False)
    assert result["query"] == "original query"
