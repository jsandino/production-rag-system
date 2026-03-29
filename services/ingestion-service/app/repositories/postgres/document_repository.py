from app.repositories.base import DocumentRepository
from psycopg.types.json import Jsonb


class PostgresDocumentRepository(DocumentRepository):

    def __init__(self, conn):
        self.conn = conn

    def create(self, metadata: dict) -> str:
        query = """
        INSERT INTO documents (metadata)
        VALUES (%s)
        RETURNING id;
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (Jsonb(metadata),))
            document_id = cur.fetchone()[0]

        return str(document_id)
