"""
FastAPI app entrypoint. Run with:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.routes import ingest, search, ask

app = FastAPI(title="Patient Vector Search API")

app.include_router(ingest.router, tags=["ingest"])
app.include_router(search.router, tags=["search"])
app.include_router(ask.router, tags=["rag"])


@app.get("/")
def root():
    return {"status": "ok", "service": "patient-vector-search"}
