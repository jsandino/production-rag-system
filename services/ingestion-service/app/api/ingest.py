from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from app.pipelines.ingest_pipeline import run_ingestion

router = APIRouter()


class IngestRequest(BaseModel):
    document_id: str
    text: str
    metadata: Dict[str, Any]


class IngestResponse(BaseModel):
    status: str
    chunks_created: int


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    chunks_created = run_ingestion(
        document_id=request.document_id, text=request.text, metadata=request.metadata
    )
    return IngestResponse(status="success", chunks_created=chunks_created)
