from typing import Optional

from psycopg import Connection, connect
from psycopg.rows import TupleRow

from app.repositories.postgres.chunk_repository import PostgresChunkRepository
from app.repositories.postgres.document_repository import PostgresDocumentRepository
from app.repositories.postgres.embedding_repository import PostgresEmbeddingRepository


class UnitOfWork:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn: Optional[Connection[TupleRow]]
        self.documents = None
        self.chunks = None
        self.embeddings = None

    def __enter__(self):
        self.conn = connect(self.dsn)
        # bind repositories to SAME connection
        self.documents = PostgresDocumentRepository(self.conn)
        self.chunks = PostgresChunkRepository(self.conn)
        self.embeddings = PostgresEmbeddingRepository(self.conn)
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.rollback()
        else:
            self.commit()

        self.close()

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()

    def close(self):
        if self.conn:
            self.conn.close()
