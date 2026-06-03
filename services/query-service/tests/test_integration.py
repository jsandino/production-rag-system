from pathlib import Path

import pytest
from psycopg import connect
from psycopg.types.json import Jsonb
from testcontainers.postgres import PostgresContainer

from query.pipelines.query_pipeline import QueryPipeline
from query.repositories.postgres.chunk_repository import PostgresChunkRepository


pytestmark = pytest.mark.integration

_SCHEMA = Path(__file__).parent.parent.parent.parent / "services" / "ingestion-service" / "db" / "schema.sql"
_VECTOR = [1.0] + [0.0] * 1535


class FakeEmbedder:
    def embed(self, text: str) -> list[float]:
        return _VECTOR


class FakeGenerator:
    def generate(self, query: str, context: str) -> str:
        return f"answer: {query}"


@pytest.fixture(scope="session")
def pg_dsn():
    with PostgresContainer("pgvector/pgvector:pg16") as pg:
        dsn = (
            f"postgresql://{pg.username}:{pg.password}"
            f"@{pg.get_container_host_ip()}:{pg.get_exposed_port(5432)}/{pg.dbname}"
        )
        with connect(dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(_SCHEMA.read_text())
        yield dsn


@pytest.fixture(autouse=True)
def clean_tables(pg_dsn):
    with connect(pg_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM embeddings")
            cur.execute("DELETE FROM chunks")
            cur.execute("DELETE FROM documents")
    yield


def _seed(dsn: str, content: str = "RAG stands for retrieval-augmented generation.") -> None:
    with connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (name, metadata) VALUES (%s, %s) RETURNING id",
                ("seed.txt", Jsonb({})),
            )
            doc_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO chunks (document_id, content, chunk_index) VALUES (%s, %s, %s) RETURNING id",
                (doc_id, content, 0),
            )
            chunk_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO embeddings (chunk_id, embedding) VALUES (%s, %s::vector)",
                (chunk_id, _VECTOR),
            )


@pytest.fixture
def pipeline(pg_dsn):
    conn = connect(pg_dsn)
    yield QueryPipeline(
        embedder=FakeEmbedder(),
        chunk_repository=PostgresChunkRepository(conn),
        generator=FakeGenerator(),
    )
    conn.close()


def test_query_returns_answer(pg_dsn, pipeline):
    _seed(pg_dsn)
    result = pipeline.run(query="What is RAG?", top_k=1, filters={}, debug=False)
    assert result["answer"] == "answer: What is RAG?"


def test_query_retrieves_seeded_content(pg_dsn, pipeline):
    _seed(pg_dsn, content="pgvector stores embeddings in Postgres.")
    result = pipeline.run(query="embeddings", top_k=1, filters={}, debug=False)
    assert len(result["ranked_chunks"]) == 1
    assert result["ranked_chunks"][0].content == "pgvector stores embeddings in Postgres."


def test_query_score_above_threshold(pg_dsn, pipeline):
    _seed(pg_dsn)
    result = pipeline.run(query="RAG", top_k=1, filters={}, debug=False)
    assert result["ranked_chunks"][0].score >= 0.5


def test_query_empty_db_returns_no_ranked_chunks(pipeline):
    result = pipeline.run(query="anything", top_k=5, filters={}, debug=False)
    assert result["ranked_chunks"] == []
    assert result["answer"] == "answer: anything"
