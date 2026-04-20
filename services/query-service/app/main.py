from fastapi import FastAPI

from app.api.query import router as query_router
from shared.telemetry import init_telemetry, instrument_app

init_telemetry()

app = FastAPI(title="Query Service")

app.include_router(query_router)

instrument_app(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}
