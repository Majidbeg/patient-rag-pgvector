"""
POST /ingest — upload a single PDF, run it through the ingest pipeline.
"""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.models.schemas import IngestResponse
from app.services.ingest_service import ingest_pdf

router = APIRouter()

os.makedirs(settings.upload_dir, exist_ok=True)


@router.post("/ingest", response_model=IngestResponse)
async def ingest_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    dest_path = os.path.join(settings.upload_dir, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = ingest_pdf(dest_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return IngestResponse(
        status="ingested",
        file=file.filename,
        patient_id=result["patient_id"],
        mrn=result["mrn"],
        chunks_created=result["chunks_created"],
    )
