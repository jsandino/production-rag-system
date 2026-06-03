from fastapi import FastAPI

from ingestion.api.ingest import router as ingest_router
from shared.telemetry import init_telemetry, instrument_app

init_telemetry()

app = FastAPI(title="Ingestion Service")

app.include_router(ingest_router)

instrument_app(app)
