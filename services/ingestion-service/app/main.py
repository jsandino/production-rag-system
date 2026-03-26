from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.core.providers.openai_text_tools import OpenAITextTools


app = FastAPI(title="Ingestion Service")

app.include_router(ingest_router)

app.state.text_tools = OpenAITextTools.create()


@app.get("/health")
def health():
    return {"status": "ok"}
