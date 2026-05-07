# CLAUDE.md — Production RAG Reference Implementation

## Project Status

| Phase | Focus | Status |
|---|---|---|
| 1 | Foundation — monorepo structure, architecture | Done |
| 2 | Ingestion Pipeline — chunking, embeddings, pgvector | Done |
| 3 | Query Pipeline — LangGraph RAG workflow, `/query` endpoint | Done |
| 4 | Observability — OTel tracing, Prometheus, Grafana, Tempo, Loki | Done |
| **5** | **Testing & Evaluation — unit tests, integration tests, RAG eval** | **In Progress** |
| 6 | CI/CD — GitHub Actions (lint, test, build, evaluation) | Planned |
| 7 | Deployment — Terraform on Azure + AWS, managed Postgres | Planned |
| 8 | Documentation & Polish — final diagrams, onboarding docs | Planned |

---

## Monorepo Layout

```
production-rag-system/
├── services/
│   ├── ingestion-service/    # FastAPI + ingestion pipeline
│   └── query-service/        # FastAPI + LangGraph query pipeline
├── shared/                   # Shared OTel telemetry library
├── infra/                    # OTel collector, Prometheus, Loki, Tempo, Grafana configs
├── docker-compose.yml        # Full local stack
├── Makefile                  # Root-level make targets
├── pytest.ini                # Root pytest config (testpaths = services shared)
└── conftest.py               # Sets TELEMETRY_ENABLED=false for all tests
```

### Key source paths

| Path | What it is |
|---|---|
| `services/ingestion-service/app/pipelines/ingest_pipeline.py` | Core ingestion logic |
| `services/ingestion-service/app/repositories/in_memory/` | Fake repos used in tests |
| `services/query-service/app/pipelines/query_pipeline.py` | LangGraph RAG graph |
| `services/query-service/app/pipelines/state.py` | `QueryState` TypedDict |
| `services/query-service/app/models/chunk_result.py` | `ChunkResult` dataclass |
| `services/query-service/app/core/embedder.py` | `Embedder` Protocol |
| `services/query-service/app/core/generator.py` | `Generator` Protocol |
| `services/query-service/app/repositories/base.py` | `ChunkRepository` Protocol |
| `shared/shared/telemetry.py` | `@traced`, `init_telemetry`, `instrument_app` |

---

## Architecture Decisions

### Layered architecture (both services)
`API → Pipeline → Repositories / Core → External (DB, OpenAI)`

### Protocol-based abstractions
All external dependencies (`Embedder`, `Generator`, `ChunkRepository`) are defined as `Protocol` classes. Concrete implementations live in `app/core/providers/` and `app/repositories/postgres/`. Tests substitute fakes via constructor injection.

### Unit of Work (ingestion-service only)
Transactional boundary for all DB writes. `UnitOfWork` is passed to the pipeline as a `uow_factory: Callable` so tests can supply `FakeUnitOfWork` directly.

### LangGraph (query-service)
The query pipeline is a compiled `StateGraph`. Node order: `embed → retrieve → rank → generate`. Each node receives the full `QueryState` and returns a partial dict that LangGraph merges.

### Shared telemetry
`shared/shared/telemetry.py` exports `@traced`, `init_telemetry()`, and `instrument_app()`. Both services import from `rag_shared`. Disabled in tests via `TELEMETRY_ENABLED=false` (set in root `conftest.py`).

---

## Coding Conventions

- **No comments by default.** Only add one when the WHY is non-obvious (hidden constraint, workaround for a specific bug).
- **No monkeypatch in tests.** Use dependency injection and fake/stub classes passed as constructor arguments.
- **No docstrings on obvious functions.** Protocol method stubs already document the interface.
- **Fake implementations** live in the test file or a `tests/fakes/` module — not alongside production code.
- **Naming:** `FakeEmbedder`, `FakeGenerator`, `FakeChunkRepository` as class names for test doubles.
- **`ChunkResult.content` field:** This field is named `content` in the current codebase but is planned to be renamed to `text` in Phase 5. When writing query-service tests, use whichever name is in the current code — do not rename until explicitly asked.

---

## Testing

### Running tests

```bash
# From repo root — runs all services and shared
pytest

# With coverage (ingestion-service only has its own pytest.ini for html coverage)
cd services/ingestion-service && pytest
```

### Test philosophy

- Unit tests: exercise one class/function with injected fakes, no I/O
- Integration tests (Phase 5): hit real Postgres with pgvector, real OpenAI embeddings
- RAG evaluation (Phase 5): measure answer quality using a test corpus

### Existing tests

| File | Covers |
|---|---|
| `services/ingestion-service/tests/test_chunker.py` | `Chunker.split` |
| `services/ingestion-service/tests/test_ingest_pipeline.py` | `IngestionPipeline.run` with fakes |
| `shared/shared/tests/test_telemetry.py` | `@traced` decorator |

### Query-service tests (Phase 5 — to be written)

`services/query-service/tests/` exists but contains only `__init__.py`. Tests needed for:
- `QueryPipeline` node behaviour (embed, retrieve, rank, generate) with fake implementations
- Ranking threshold logic (below 0.5 filtered; fallback to top-1 when none pass)
- `QueryState` transitions

Use the same pattern as ingestion tests: define `FakeEmbedder`, `FakeGenerator`, `FakeChunkRepository` as simple classes satisfying the Protocols, instantiate `QueryPipeline` directly, assert on the returned `QueryState`.

---

## Development Workflow

### Local (no Docker)

```bash
make install      # install root requirements
make test         # pytest across all services
make lint         # pylint services
make format       # black .
```

### Docker (full stack)

```bash
export OPENAI_API_KEY=your_key_here
make docker-up     # builds and starts everything
make docker-ingest # smoke-test ingestion
make docker-query  # smoke-test query
make docker-down
make docker-reset  # full wipe + rebuild
```

### Observability stack (when running Docker)

| Service | URL |
|---|---|
| Ingestion API | http://localhost:8000 |
| Query API | http://localhost:8001 |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090/targets |

Set `TELEMETRY_ENABLED=false` to disable OTel export in local Python runs without a collector.

---

## Remaining Phases — Implementation Notes

### Phase 5 — Testing & Evaluation

1. **Query-service unit tests** — write `tests/test_query_pipeline.py` using fake Protocol implementations.
2. **Integration tests** — requires a live Postgres instance. Use `pytest` marks (e.g. `@pytest.mark.integration`) to separate from unit tests. Gate on a `POSTGRES_DSN` env var.
3. **RAG evaluation framework** — small corpus of (question, expected_answer) pairs. Run the full `QueryPipeline` against real data and score with a metric (e.g. RAGAS, or a simple LLM-as-judge call).

### Phase 6 — CI/CD

GitHub Actions workflows needed:
- **lint-and-test**: `black --check`, `pylint`, `pytest` (unit only, no integration)
- **integration**: spin up Postgres service container, run integration tests
- **build**: `docker build` both service images
- **evaluation**: run RAG eval, fail if quality drops below threshold

### Phase 7 — Deployment

- Terraform modules for Azure (AKS or Container Apps) and/or AWS (ECS or EKS)
- Managed Postgres with pgvector extension enabled (Azure Flexible Server or RDS)
- Secrets: OpenAI API key via Key Vault / Secrets Manager
- OTel collector sidecar or managed APM

### Phase 8 — Documentation & Polish

- Architecture diagrams (Mermaid already exists in READMEs — may need updates)
- Onboarding walkthrough (end-to-end: ingest → query → observe in Grafana)
- Demo workflow script or Makefile targets

---

## Sub-Agents

Custom sub-agents live in `.claude/agents/`. Invoke them by typing `@<name>` in the Claude Code prompt.

| Agent | File | Purpose |
|---|---|---|
| `@coach` | `.claude/agents/coach.md` | Interactive technical coach — teaches concepts related to this project (observability, RAG, LangGraph, testing, Docker, Grafana, etc.) with step-by-step explanations and the "why" behind each step. Pauses after every explanation to invite questions. Has web search access. |

### Using `@coach`

```
@coach teach me how to read observability metrics in Grafana
@coach explain how LangGraph state transitions work in the query pipeline
@coach walk me through how pgvector similarity search works
```

The coach reads repo source files and searches the web to ground explanations in real code and up-to-date documentation. It never edits files — redirect code changes to the main assistant.
