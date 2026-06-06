# 0003 — Name Python packages after their service

**Status**: Accepted
**Date**: 2026-03-24

## Context

The monorepo has two services sharing a single pytest run from the root. If both services used a generic package name (e.g. `app`), Python's import system would silently shadow one package with the other, causing difficult-to-diagnose test failures.

## Decision

Each service's top-level Python package is named after its service: `ingestion/` for the ingestion service, `query/` for the query service. The shared library uses `shared/` under the `rag_shared` distribution name.

## Alternatives considered

- **`app/` for all services** — conventional in single-service projects. Rejected because it causes namespace collisions when running tests across the monorepo from the root.
- **`src/` layout for all services** — using `src/ingestion/` and `src/query/`. Considered but rejected as it adds a layer of directory nesting without solving the naming problem and requires additional `pyproject.toml` configuration.

## Consequences

- **Positive**: imports are unambiguous across the monorepo; no namespace collisions when running `pytest` from root.
- **Positive**: the package name immediately signals which service owns the code.
- **Neutral**: slightly unconventional for developers expecting `app/` in a FastAPI project — but the reason is visible in this ADR.

## References

- Ingestion package: [`services/ingestion-service/ingestion/`](../../services/ingestion-service/ingestion/)
- Query package: [`services/query-service/query/`](../../services/query-service/query/)
- Shared package: [`shared/shared/`](../../shared/shared/)
