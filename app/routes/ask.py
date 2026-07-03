"""
GET /ask — RAG endpoint. Retrieves relevant patient chunks from pgvector,
then asks an OpenRouter chat model to answer using only that context.
"""
from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import RagResponse, RagSource
from app.services.rag_service import answer_question

router = APIRouter()


@router.get("/ask", response_model=RagResponse)
def ask_endpoint(
    question: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
):
    try:
        result = answer_question(question, top_k=top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

    return RagResponse(
        question=question,
        answer=result["answer"],
        sources=[RagSource(**s) for s in result["sources"]],
    )
