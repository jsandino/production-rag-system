from app.pipelines.ingest_pipeline import IngestionPipeline
from app.repositories.in_memory.chunk_repository import InMemoryChunkRepository
from app.repositories.in_memory.document_repository import InMemoryDocumentRepository
from app.repositories.in_memory.embedding_repository import InMemoryEmbeddingRepository


class FakeTokenizer:
    def encode(self, text: str) -> list[int]:
        return [ord(c) for c in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(t) for t in tokens)


class FakeChunker:
    def split(self, text: str) -> list[str]:
        return [text]


class FakeEmbedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]


class FakeUnitOfWork:
    def __init__(self):
        self.documents = InMemoryDocumentRepository()
        self.chunks = InMemoryChunkRepository()
        self.embeddings = InMemoryEmbeddingRepository()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def make_pipeline() -> tuple[IngestionPipeline, FakeUnitOfWork]:
    uow = FakeUnitOfWork()
    pipeline = IngestionPipeline(
        chunker=FakeChunker(),
        embedder=FakeEmbedder(),
        uow_factory=lambda: uow,
    )
    return pipeline, uow


def test_run_returns_chunk_count():
    pipeline, _ = make_pipeline()
    result = pipeline.run(text="some text", name="doc.txt", metadata={})
    assert result == 1


def test_run_persists_document():
    pipeline, uow = make_pipeline()
    pipeline.run(text="some text", name="doc.txt", metadata={"source": "test"})
    assert len(uow.documents.documents) == 1


def test_run_persists_chunks():
    pipeline, uow = make_pipeline()
    pipeline.run(text="some text", name="doc.txt", metadata={})
    assert len(uow.chunks.chunks) == 1


def test_run_persists_embeddings():
    pipeline, uow = make_pipeline()
    pipeline.run(text="some text", name="doc.txt", metadata={})
    assert len(uow.embeddings.embeddings) == 1


def test_run_links_chunks_to_document():
    pipeline, uow = make_pipeline()
    pipeline.run(text="some text", name="doc.txt", metadata={})

    doc_id = next(iter(uow.documents.documents))
    chunk = next(iter(uow.chunks.chunks.values()))
    assert chunk["document_id"] == doc_id


def test_run_with_metadata():
    pipeline, uow = make_pipeline()
    pipeline.run(text="some text", name="doc.txt", metadata={"author": "alice"})

    doc = next(iter(uow.documents.documents.values()))
    assert doc["metadata"] == {"author": "alice"}
