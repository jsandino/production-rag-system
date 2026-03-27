from fastapi import FastAPI
from app.api.ingest import router as ingest_router
from app.bootstrap import create_ingestion_pipeline


app = FastAPI(title="Ingestion Service")

app.include_router(ingest_router)

app.state.ingestion_pipeline = create_ingestion_pipeline()


@app.get("/health")
def health():
    return {"status": "ok"}
