# 0002 — Protocol-based abstractions for external dependencies

**Status**: Accepted
**Date**: 2026-03-27

## Context

Both services depend on external I/O: OpenAI for embeddings and generation, Postgres via pgvector for storage and retrieval. Tests should not hit real external services. The abstraction mechanism needs to support injecting test doubles without requiring inheritance or test-specific conditional logic in production code.

## Decision

Define `Embedder`, `Generator`, and `ChunkRepository` as `Protocol` classes (structural subtyping). Concrete implementations live in `query/core/providers/` and `query/repositories/postgres/`. Tests pass `FakeEmbedder`, `FakeGenerator`, and `FakeChunkRepository` as constructor arguments to the pipeline — no monkeypatching required.

## Alternatives considered

- **Abstract base classes (ABCs)** — heavier; requires concrete classes to explicitly inherit and register. Rejected because Python's structural typing (`Protocol`) achieves the same guarantee without coupling test doubles to the production class hierarchy.
- **Monkeypatching** — replacing module-level names at test time. Rejected because it ties tests to internal implementation details and breaks when imports are reorganised.
- **Dependency injection framework** — a DI container (e.g. `injector`). Rejected as over-engineering for a two-service system where manual constructor injection is sufficient and obvious.

## Consequences

- **Positive**: test doubles are plain classes with no inheritance; the Protocol type-checks them at static analysis time.
- **Positive**: swapping LLM providers or database backends is a single constructor argument change.
- **Negative**: Protocol structural typing only catches mismatches at static analysis time (mypy/pyright), not at runtime, unless explicitly checked.

## References

- `Embedder` Protocol: [`services/query-service/query/core/embedder.py`](../../services/query-service/query/core/embedder.py)
- `Generator` Protocol: [`services/query-service/query/core/generator.py`](../../services/query-service/query/core/generator.py)
- `ChunkRepository` Protocol: [`services/query-service/query/repositories/base.py`](../../services/query-service/query/repositories/base.py)
