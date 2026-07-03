"""
Pydantic request/response models used by the API routes.
"""
from pydantic import BaseModel
from typing import List


class IngestResponse(BaseModel):
    status: str
    file: str
    patient_id: int
    mrn: str | None = None
    chunks_created: int


class SearchResult(BaseModel):
    patient_name: str | None
    mrn: str | None
    chunk_text: str
    distance: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]


class RagSource(BaseModel):
    patient_name: str | None
    mrn: str | None
    distance: float


class RagResponse(BaseModel):
    question: str
    answer: str
    sources: List[RagSource]
