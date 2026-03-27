from typing import Dict, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class IngestInputs(BaseModel):
    document_id: str
    text: str
    metadata: Dict[str, Any] = {}


class IngestOutputs(BaseModel):
    status: str
    chunks_created: int


@router.post("/ingest", response_model=IngestOutputs)
def ingest(inputs: IngestInputs, request: Request):
    pipeline = request.app.state.ingestion_pipeline
    chunks_created = pipeline.run(text=inputs.text, metadata=inputs.metadata)
    return IngestOutputs(status="success", chunks_created=chunks_created)
