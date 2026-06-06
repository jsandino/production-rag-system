# 0006 — Shared telemetry library across services

**Status**: Accepted
**Date**: 2026-04-17

## Context

Both services need identical OTel instrumentation: a `@traced` decorator for pipeline nodes, `init_telemetry()` for collector configuration, and `instrument_app()` for FastAPI middleware. Duplicating this code across services creates a maintenance surface where one service's telemetry diverges from the other over time. Tests across the monorepo also need a reliable way to disable telemetry export without modifying production code.

## Decision

Extract all telemetry code into a `shared/` package distributed as `rag_shared`. Both services declare it as a local dependency. Telemetry is disabled by setting `TELEMETRY_ENABLED=false`; the root `conftest.py` sets this for all tests automatically.

## Alternatives considered

- **Copy-paste telemetry into each service** — simplest initially. Rejected because divergence is inevitable as each service evolves its instrumentation independently.
- **Per-service telemetry packages** — each service owns a `telemetry.py` that imports from a common base. Rejected as the same divergence risk with added indirection.

## Consequences

- **Positive**: single source of truth for all OTel configuration; a change to the `@traced` decorator propagates to both services.
- **Positive**: `TELEMETRY_ENABLED=false` in `conftest.py` cleanly disables export without any mocking.
- **Negative**: introduces a cross-service dependency; a breaking change to `rag_shared` must be coordinated across both services.
- **Neutral**: the shared package must be installed in each service's venv; the Makefiles handle this via `pip install -e ../../shared`.

## References

- Shared telemetry: [`shared/shared/telemetry.py`](../../shared/shared/telemetry.py)
- Root test config: [`conftest.py`](../../conftest.py)
