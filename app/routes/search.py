"""
GET /search — embed a natural-language query and return the closest
matching chunks by cosine distance.
"""
from fastapi import APIRouter, Query, HTTPException

from app.models.schemas import SearchResponse, SearchResult
from app.services.search_service import search

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
def search_endpoint(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=50),
):
    try:
        results = search(query, top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    return SearchResponse(
        query=query,
        results=[SearchResult(**r) for r in results],
    )
