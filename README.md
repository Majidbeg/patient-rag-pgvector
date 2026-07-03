Here's the full README, ready to paste directly into your project's `README.md`:

```markdown
# Patient RAG (pgvector)

A FastAPI + PostgreSQL (pgvector) system for ingesting patient medical
record PDFs, generating embeddings **locally** with `sentence-transformers`,
and answering natural-language questions about patients using
Retrieval-Augmented Generation (RAG) via OpenRouter.

No paid API keys are required for embeddings — only a free OpenRouter key
is needed, and only for the `/ask` (RAG answer) endpoint.

> **Note:** This project handles patient health data. Make sure your
> infrastructure (database, API keys, logging) meets your organization's
> compliance requirements (e.g. HIPAA) before using this with real records.

---

## Prerequisites

- Python 3.10+
- PostgreSQL (with ability to install extensions) — version 13+
- `pgvector` extension installed on your Postgres server
- A free [OpenRouter](https://openrouter.ai) account + API key (for `/ask` only)

---

## Step 1 — Clone / download the project

```bash
git clone https://github.com/yourusername/patient-rag-pgvector.git
cd patient-rag-pgvector
```

## Step 2 — Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

## Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

## Step 4 — Set up your `.env` file

```bash
cp .env.example .env
```

Open `.env` and fill in your database credentials:

```
DB_NAME=yourdb
DB_USER=postgres
DB_PASSWORD=yourpass
DB_HOST=localhost
DB_PORT=5432

EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIM=384

OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=openrouter/free
```

Get a free OpenRouter key at: https://openrouter.ai/keys

## Step 5 — Enable pgvector on your database

Make sure the `pgvector` extension is installed on your Postgres server
(see your OS-specific install docs if `CREATE EXTENSION vector;` fails
with "extension not available").

Run the schema setup script against your database — either via `psql`:

```bash
psql -U postgres -d yourdb -f app/db/init_db.sql
```

or by pasting the contents of `app/db/init_db.sql` into pgAdmin's Query Tool
and executing it.

This creates:
- the `vector` extension
- a `patients` table
- a `document_chunks` table (with a `VECTOR(384)` column)

## Step 6 — Bulk-ingest your PDFs

Place all your patient PDF files in one folder, then run:

```bash
python -m scripts.batch_ingest /path/to/your/pdf/folder
```

This will, for each PDF:
1. Extract text and key fields (MRN, patient name, department, diagnosis)
2. Chunk the text if needed
3. Generate embeddings locally (first run downloads the model, ~80MB)
4. Store everything in Postgres

You'll see output like:
```
[OK]   patient_01.pdf -> patient_id=1 mrn=P1000 chunks=1
...
Done in 12.4s — 30 succeeded, 0 failed.
```

## Step 7 — Build the vector index (after bulk loading)

In pgAdmin or `psql`, run:

```sql
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops);
```

Building this only after loading data (not before) is significantly faster.

## Step 8 — Start the API server

```bash
uvicorn app.main:app --reload
```

The API will be running at `http://localhost:8000`.

## Step 9 — Try it out

**Health check:**
```bash
curl http://localhost:8000/
```

**Ingest a new single PDF (after initial bulk load):**
```bash
curl -X POST "http://localhost:8000/ingest" -F "file=@patient_31.pdf"
```

**Raw vector similarity search:**
```bash
curl "http://localhost:8000/search?query=breast%20cancer%20follow-up%20stable&top_k=5"
```

**RAG question-answering (retrieval + LLM-generated answer):**
```bash
curl "http://localhost:8000/ask?question=Which%20patients%20have%20breast%20cancer%20and%20are%20stable?"
```

Example response from `/ask`:
```json
{
  "question": "Which patients have breast cancer and are stable?",
  "answer": "Clara Johnson (MRN: P1000) has a stable breast cancer follow-up...",
  "sources": [
    {"patient_name": "Clara Johnson", "mrn": "P1000", "distance": 0.12}
  ]
}
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/ingest` | POST | Upload and ingest a single PDF (multipart, field name `file`) |
| `/search?query=...&top_k=5` | GET | Raw vector similarity search over patient chunks |
| `/ask?question=...&top_k=5` | GET | RAG: retrieves context + generates a grounded answer via OpenRouter |

---

## Project structure

```
app/
  main.py              FastAPI app entrypoint
  config.py            Loads settings from .env
  database.py          Postgres connection pool
  models/schemas.py    Pydantic request/response models
  services/
    pdf_extractor.py    Extracts text + fields from PDFs
    chunker.py           Splits long text into overlapping chunks
    embeddings.py        Local embedding generation (sentence-transformers)
    ingest_service.py    Orchestrates PDF -> chunks -> embeddings -> DB
    search_service.py    Vector similarity search
    rag_service.py       Retrieval + OpenRouter answer generation
  routes/
    ingest.py            POST /ingest
    search.py            GET /search
    ask.py               GET /ask
  db/init_db.sql         Schema + pgvector extension setup
scripts/
  batch_ingest.py         One-time bulk loader for a folder of PDFs
```

---

## Troubleshooting

- **`extension "vector" is not available`** — pgvector isn't installed on
  your Postgres server yet; install it before running `init_db.sql`.
- **`ModuleNotFoundError: No module named 'app'`** — make sure you're
  running commands from the project root and that `venv` is activated.
- **Pydantic `Field required` errors on startup** — your `.env` file is
  missing or incomplete; re-check Step 4.
- **OpenRouter 401/404 errors** — verify your key and check that the
  model slug in `OPENROUTER_MODEL` is still marked `:free` on
  [openrouter.ai/models](https://openrouter.ai/models) (free model IDs
  rotate periodically — `openrouter/free` auto-routes around this).
```
