from app.repositories.base import DocumentRepository
from app.db.connection import get_connection
from psycopg.types.json import Jsonb


class PostgresDocumentRepository(DocumentRepository):
    def create(self, metadata: dict) -> str:
        query = """
        INSERT INTO documents (metadata)
        VALUES (%s)
        RETURNING id;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (Jsonb(metadata),))
                document_id = cur.fetchone()[0]

        return str(document_id)
