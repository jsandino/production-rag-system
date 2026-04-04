from functools import lru_cache
from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.providers.openai_text_tools import OpenAITextTools
from app.core.settings import get_settings
from app.core.text_tools import TextTools
from app.pipelines.ingest_pipeline import IngestionPipeline

router = APIRouter()


@lru_cache
def ingestion_pipeline() -> IngestionPipeline:
    text_tools: TextTools = OpenAITextTools.create()
    return IngestionPipeline(
        chunker=text_tools.chunker,
        embedder=text_tools.embedder,
        dsn=get_settings().database_url,
    )


class IngestInputs(BaseModel):
    document_name: str
    text: str
    metadata: Dict[str, Any] = {}


class IngestOutputs(BaseModel):
    status: str
    chunks_created: int


@router.post("/ingest", response_model=IngestOutputs)
def ingest(
    inputs: IngestInputs,
    pipeline: IngestionPipeline = Depends(ingestion_pipeline),
):
    chunks_created = pipeline.run(text=inputs.text, name=inputs.document_name, metadata=inputs.metadata)
    return IngestOutputs(status="success", chunks_created=chunks_created)
