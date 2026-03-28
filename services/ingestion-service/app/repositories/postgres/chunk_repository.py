from typing import List
from psycopg.types.json import Jsonb

from app.db.connection import get_connection
from app.repositories.base import ChunkRepository


class PostgresChunkRepository(ChunkRepository):
    def create_many(self, document_id: str, chunks: List[str]) -> List[str]:
        query = """
        INSERT INTO chunks (document_id, content, chunk_index)
        VALUES (%s, %s, %s)
        RETURNING id;
        """

        chunk_ids = []

        with get_connection() as conn:
            with conn.cursor() as cur:
                for idx, chunk in enumerate(chunks):
                    cur.execute(query, (document_id, chunk, idx))
                    chunk_ids.append(str(cur.fetchone()[0]))

        return chunk_ids
