from typing import List

from app.models.chunk_result import ChunkResult


class PostgresChunkRepository:

    def __init__(self, conn):
        self.conn = conn

    def search(self, embedding: list[float], top_k: int) -> List[ChunkResult]:
        # <=> is cosine distance in [0, 2]; convert to similarity score in [0, 1].
        # GREATEST guards against negative values from near-opposite vectors.
        query = """
        SELECT
            c.id        AS chunk_id,
            d.id        AS document_id,
            d.name      AS document_name,
            c.content,
            GREATEST(0, 1 - (e.embedding <=> %s::vector)) AS score
        FROM embeddings e
        JOIN chunks     c ON c.id = e.chunk_id
        JOIN documents  d ON d.id = c.document_id
        ORDER BY e.embedding <=> %s::vector
        LIMIT %s;
        """

        with self.conn.cursor() as cur:
            cur.execute(query, (embedding, embedding, top_k))
            rows = cur.fetchall()

        return [
            ChunkResult(
                chunk_id=str(row[0]),
                document_id=str(row[1]),
                document_name=row[2],
                content=row[3],
                score=float(row[4]),
            )
            for row in rows
        ]
