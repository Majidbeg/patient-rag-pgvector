"""
Runs semantic similarity search against document_chunks using pgvector's
cosine distance operator (<=>).
"""
from app.database import get_connection, release_connection
from app.services.embeddings import get_embeddings_batch


def search(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = get_embeddings_batch([query])[0]

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT p.patient_name, p.mrn, d.chunk_text,
                   d.embedding <=> %s::vector AS distance
            FROM document_chunks d
            JOIN patients p ON p.id = d.patient_id
            ORDER BY distance
            LIMIT %s
            """,
            (query_embedding, top_k),
        )
        rows = cur.fetchall()
        cur.close()
    finally:
        release_connection(conn)

    return [
        {
            "patient_name": r[0],
            "mrn": r[1],
            "chunk_text": r[2],
            "distance": float(r[3]),
        }
        for r in rows
    ]
