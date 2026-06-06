# 0004 — Unit of Work pattern for ingestion writes

**Status**: Accepted
**Date**: 2026-03-29

## Context

The ingestion pipeline writes to multiple tables (document chunks and embedding vectors) in a single logical operation. These writes must be atomic — a partial write leaves the database in an inconsistent state where chunks exist without embeddings or vice versa. The pipeline also needs to be testable without a real database.

## Decision

Introduce a `UnitOfWork` class as the transactional boundary for all ingestion writes. The pipeline receives a `uow_factory: Callable` as a constructor argument, opens the unit of work as a context manager, and commits or rolls back as a unit. Tests supply a `FakeUnitOfWork` that records calls without touching a database.

## Alternatives considered

- **Explicit transaction management in the pipeline** — open a connection, begin a transaction, call repositories, commit. Rejected because it mixes transaction management with orchestration logic and makes testing require a real database connection.
- **Repository-level transactions** — each repository manages its own transaction. Rejected because writes across two repositories would require a shared connection object threaded through both, or two separate transactions with no atomicity guarantee.

## Consequences

- **Positive**: atomic writes across tables; a failure mid-pipeline rolls back cleanly.
- **Positive**: `FakeUnitOfWork` keeps unit tests free of database I/O.
- **Negative**: adds an abstraction layer that is unfamiliar to developers who expect repositories to manage their own connections.

## References

- Pipeline: [`services/ingestion-service/ingestion/pipelines/ingest_pipeline.py`](../../services/ingestion-service/ingestion/pipelines/ingest_pipeline.py)
- In-memory fakes: [`services/ingestion-service/ingestion/repositories/in_memory/`](../../services/ingestion-service/ingestion/repositories/in_memory/)
