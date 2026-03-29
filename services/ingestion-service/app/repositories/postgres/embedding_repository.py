from typing import List


class PostgresEmbeddingRepository:

    def __init__(self, conn):
        self.conn = conn

    def create_many(self, chunk_ids: List[str], embeddings: List[list[float]]):
        if len(chunk_ids) != len(embeddings):
            raise ValueError("chunk_ids and embeddings must match in length")

        query = """
        INSERT INTO embeddings (chunk_id, embedding)
        VALUES (%s, %s);
        """

        with self.conn.cursor() as cur:
            cur.executemany(
                query,
                list(zip(chunk_ids, embeddings)),
            )
