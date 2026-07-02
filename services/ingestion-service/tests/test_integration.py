from pathlib import Path

import pytest
from psycopg import connect
from testcontainers.postgres import PostgresContainer

from ingestion.db.unit_of_work import UnitOfWork
from ingestion.pipelines.ingest_pipeline import IngestionPipeline


pytestmark = pytest.mark.integration

_SCHEMA = Path(__file__).parent.parent / "db" / "schema.sql"


class FakeChunker:
    def split(self, text: str) -> list[str]:
        return [text]


class FakeSplittingChunker:
    def __init__(self, chunks: list[str]):
        self._chunks = chunks

    def split(self, text: str) -> list[str]:
        return self._chunks


class FakeEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 1536 for _ in texts]


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


def make_pipeline(dsn: str, chunker=None) -> IngestionPipeline:
    return IngestionPipeline(
        chunker=chunker or FakeChunker(),
        embedder=FakeEmbedder(),
        uow_factory=lambda: UnitOfWork(dsn),
    )


def test_ingestion_persists_document(pg_dsn):
    make_pipeline(pg_dsn).run(text="hello world", name="doc.txt", metadata={})

    with connect(pg_dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT name FROM documents")
        rows = cur.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == "doc.txt"


def test_ingestion_persists_chunks(pg_dsn):
    make_pipeline(pg_dsn).run(text="hello world", name="doc.txt", metadata={})

    with connect(pg_dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT content FROM chunks")
        rows = cur.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == "hello world"


def test_ingestion_persists_embeddings(pg_dsn):
    make_pipeline(pg_dsn).run(text="hello world", name="doc.txt", metadata={})

    with connect(pg_dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM embeddings")
        count = cur.fetchone()[0]

    assert count == 1


def test_ingestion_returns_chunk_count(pg_dsn):
    chunker = FakeSplittingChunker(["one", "two", "three"])
    result = make_pipeline(pg_dsn, chunker=chunker).run(text="anything", name="doc.txt", metadata={})
    assert result == 3


def test_ingestion_stores_metadata(pg_dsn):
    make_pipeline(pg_dsn).run(text="hello", name="doc.txt", metadata={"author": "alice"})

    with connect(pg_dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT metadata FROM documents")
        row = cur.fetchone()

    assert row[0] == {"author": "alice"}


def test_ingestion_links_chunks_to_document(pg_dsn):
    make_pipeline(pg_dsn).run(text="hello world", name="doc.txt", metadata={})

    with connect(pg_dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM documents")
        doc_id = str(cur.fetchone()[0])
        cur.execute("SELECT document_id FROM chunks")
        chunk_doc_id = str(cur.fetchone()[0])

    assert chunk_doc_id == doc_id
