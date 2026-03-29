from app.core.chunker import Chunker
from app.core.embedder import Embedder
from app.db.unit_of_work import UnitOfWork


class IngestionPipeline:
    def __init__(
        self,
        chunker: Chunker,
        embedder: Embedder,
        dsn: str,
    ):
        self.chunker = chunker
        self.embedder = embedder
        self.dsn = dsn

    def run(self, text: str, metadata: dict) -> int:

        with UnitOfWork(self.dsn) as uow:
            # 1. Create document
            document_id = uow.documents.create(metadata)

            # 2. Chunk text
            chunks = self.chunker.split(text)

            # 3. Persist chunks
            chunk_ids = uow.chunks.create_many(document_id, chunks)

            # 4. Generate embeddings
            embeddings = self.embedder.embed(chunks)

            # 5. Persist embeddings
            uow.embeddings.create_many(chunk_ids, embeddings)

        return len(embeddings)
