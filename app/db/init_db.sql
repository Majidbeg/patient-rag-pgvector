-- Run this once against your target database (via pgAdmin's Query Tool
-- or `psql -d yourdb -f app/db/init_db.sql`) before ingesting any PDFs.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    mrn TEXT UNIQUE,
    patient_name TEXT,
    department TEXT,
    diagnosis TEXT,
    source_file TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(id) ON DELETE CASCADE,
    chunk_text TEXT,
    embedding VECTOR(384)  -- matches local all-MiniLM-L6-v2 model dimension
);

-- Build the index AFTER bulk-loading your 50 PDFs, not before —
-- it's much faster to build once on a full table than to update
-- it on every single insert.
-- CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
--     ON document_chunks USING hnsw (embedding vector_cosine_ops);
