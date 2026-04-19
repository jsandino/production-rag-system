from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.ingest import router as ingest_router
from shared.telemetry import init_telemetry

init_telemetry()

app = FastAPI(title="Ingestion Service")

app.include_router(ingest_router)

FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health():
    return {"status": "ok"}
