from typing import List

from app.db.connection import get_connection


class PostgresEmbeddingRepository:
    def create_many(self, chunk_ids: List[str], embeddings: List[list[float]]):
        if len(chunk_ids) != len(embeddings):
            raise ValueError("chunk_ids and embeddings must match in length")

        query = """
        INSERT INTO embeddings (chunk_id, embedding)
        VALUES (%s, %s);
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(
                    query,
                    list(zip(chunk_ids, embeddings)),
                )
