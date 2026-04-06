from fastapi import FastAPI

from app.api.query import router as query_router

app = FastAPI(title="Query Service")

app.include_router(query_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
