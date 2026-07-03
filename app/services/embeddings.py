"""
Generates embeddings locally using sentence-transformers. No API key,
no billing, no network calls at request time -- runs entirely on your
machine.

Model: all-MiniLM-L6-v2 (384 dimensions, fast, good general quality).
The model downloads once (~80MB) on first run and is cached locally
afterward.

To switch back to OpenAI later, restore the OpenAI-based version and
set EMBEDDING_DIM=1536 in .env + init_db.sql.
"""
from sentence_transformers import SentenceTransformer

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [emb.tolist() for emb in embeddings]
