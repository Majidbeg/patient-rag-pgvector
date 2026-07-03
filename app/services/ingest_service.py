"""
Orchestrates the full ingest pipeline for a single PDF:
extract text -> extract fields -> chunk -> embed (batched) -> store in Postgres.
"""
from psycopg2.extras import execute_values

from app.database import get_connection, release_connection
from app.services.pdf_extractor import extract_text, extract_fields
from app.services.chunker import chunk_text
from app.services.embeddings import get_embeddings_batch


def ingest_pdf(pdf_path: str) -> dict:
    text = extract_text(pdf_path)
    fields = extract_fields(text)
    chunks = chunk_text(text)
    embeddings = get_embeddings_batch(chunks)

    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO patients (mrn, patient_name, department, diagnosis, source_file)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (mrn) DO UPDATE SET
                patient_name = EXCLUDED.patient_name,
                department = EXCLUDED.department,
                diagnosis = EXCLUDED.diagnosis,
                source_file = EXCLUDED.source_file
            RETURNING id
            """,
            (
                fields["mrn"],
                fields["patient_name"],
                fields["department"],
                fields["diagnosis"],
                pdf_path,
            ),
        )
        patient_id = cur.fetchone()[0]

        # Clear old chunks for this patient before inserting fresh ones
        # (handles re-ingestion of an updated record cleanly)
        cur.execute("DELETE FROM document_chunks WHERE patient_id = %s", (patient_id,))

        rows = [(patient_id, chunk, emb) for chunk, emb in zip(chunks, embeddings)]
        execute_values(
            cur,
            "INSERT INTO document_chunks (patient_id, chunk_text, embedding) VALUES %s",
            rows,
        )

        conn.commit()
        cur.close()

        return {
            "patient_id": patient_id,
            "mrn": fields["mrn"],
            "chunks_created": len(chunks),
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)
