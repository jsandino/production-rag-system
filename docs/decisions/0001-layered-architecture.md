# 0001 — Layered architecture for all services

**Status**: Accepted
**Date**: 2026-03-17

## Context

The system spans two services (ingestion, query) each with multiple responsibilities: HTTP handling, business logic, external I/O (database, LLM API). Without an explicit layer boundary, business logic drifts into API handlers and tests start requiring live external dependencies to exercise any meaningful behaviour.

## Decision

All services follow a strict four-layer stack: `API → Pipeline → Repositories / Core → External (DB, OpenAI)`. Each layer depends only on the layer directly below it. The pipeline layer holds all orchestration logic; the API layer is thin (parse, call, serialize).

## Alternatives considered

- **Fat controllers** — put business logic directly in FastAPI route handlers. Rejected because it makes unit testing impossible without spinning up the full HTTP stack, and conflates input parsing with domain logic.
- **Service objects without explicit layering** — a flat module of functions with no enforced structure. Rejected because it drifts toward spaghetti as the codebase grows and makes the test-injection boundary ambiguous.

## Consequences

- **Positive**: each layer is independently testable; pipeline tests inject fakes without touching HTTP or the database.
- **Positive**: the boundary makes it obvious where new code belongs.
- **Negative**: adds boilerplate for thin operations where a single function would suffice.

## References

- Ingestion pipeline: [`services/ingestion-service/ingestion/pipelines/ingest_pipeline.py`](../../services/ingestion-service/ingestion/pipelines/ingest_pipeline.py)
- Query pipeline: [`services/query-service/query/pipelines/query_pipeline.py`](../../services/query-service/query/pipelines/query_pipeline.py)
