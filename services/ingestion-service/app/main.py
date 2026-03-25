from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.core.settings import get_settings
from app.core.providers.openai_embedding import OpenAIEmbeddingService

app = FastAPI(title="Ingestion Service")

app.include_router(ingest_router)

settings = get_settings()

embedding_service = OpenAIEmbeddingService(api_key=settings.openai_api_key)

# attach service to app state (simple DI container)
app.state.embedding_service = embedding_service


@app.get("/health")
def health():
    return {"status": "ok"}
