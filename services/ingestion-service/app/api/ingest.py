from typing import Dict, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.pipelines.ingest_pipeline import run_ingestion

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
    tools = request.app.state.text_tools

    chunks_created = run_ingestion(
        document_id=inputs.document_id,
        text=inputs.text,
        metadata=inputs.metadata,
        chunker=tools.chunker,
        embedder=tools.embedder,
    )
    return IngestOutputs(status="success", chunks_created=chunks_created)
