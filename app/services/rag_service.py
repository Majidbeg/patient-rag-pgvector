"""
RAG pipeline: retrieve relevant patient record chunks from pgvector,
then feed them as context into an OpenRouter chat model (DeepSeek) to
produce a natural-language answer grounded in the retrieved records.

Uses OpenRouter for the generation step only. Embeddings (retrieval)
still run locally via sentence-transformers -- OpenRouter has no
embeddings endpoint, so this split is required.
"""
from openai import OpenAI

from app.config import settings
from app.services.search_service import search

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

SYSTEM_PROMPT = (
    "You are a clinical assistant that answers questions using ONLY the "
    "patient record excerpts provided below. If the excerpts don't contain "
    "enough information to answer, say so clearly instead of guessing. "
    "Be concise and factual. Always mention which patient (name/MRN) each "
    "piece of information comes from."
)


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(
            f"[Record {i}] Patient: {c['patient_name']} (MRN: {c['mrn']})\n"
            f"{c['chunk_text']}"
        )
    return "\n\n".join(parts)


def answer_question(question: str, top_k: int = 5) -> dict:
    retrieved = search(question, top_k=top_k)

    if not retrieved:
        return {
            "answer": "No matching patient records were found for this question.",
            "sources": [],
        }

    context = _build_context(retrieved)

    response = _client.chat.completions.create(
        model=settings.openrouter_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Patient record excerpts:\n\n{context}\n\nQuestion: {question}",
            },
        ],
        max_tokens=500,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": [
            {"patient_name": c["patient_name"], "mrn": c["mrn"], "distance": c["distance"]}
            for c in retrieved
        ],
    }
