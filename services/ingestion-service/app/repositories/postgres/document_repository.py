from app.repositories.base import DocumentRepository
from psycopg.types.json import Jsonb


class PostgresDocumentRepository(DocumentRepository):

    def __init__(self, conn):
        self.conn = conn

    def create(self, name: str, metadata: dict) -> str:
        query = """
        INSERT INTO documents (name, metadata)
        VALUES (%s, %s)
        RETURNING id;
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (name, Jsonb(metadata)))
            document_id = cur.fetchone()[0]

        return str(document_id)
