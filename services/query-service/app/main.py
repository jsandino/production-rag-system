from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.query import router as query_router
from shared.telemetry import init_telemetry

init_telemetry()

app = FastAPI(title="Query Service")

app.include_router(query_router)

FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}
