from fastapi import FastAPI

from shared.telemetry import init_telemetry, instrument_app

from ingestion.api.ingest import router as ingest_router

init_telemetry()

app = FastAPI(title="Ingestion Service")

app.include_router(ingest_router)

instrument_app(app)
