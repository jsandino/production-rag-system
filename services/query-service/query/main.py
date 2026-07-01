from fastapi import FastAPI

from shared.telemetry import init_telemetry, instrument_app

from query.api.query import router as query_router

init_telemetry()

app = FastAPI(title="Query Service")

app.include_router(query_router)

instrument_app(app)
