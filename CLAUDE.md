# CLAUDE.md — Production RAG Reference Implementation

## Project Status

| Phase | Focus | Status |
|---|---|---|
| 1 | Foundation — monorepo structure, architecture | Done |
| 2 | Ingestion Pipeline — chunking, embeddings, pgvector | Done |
| 3 | Query Pipeline — LangGraph RAG workflow, `/query` endpoint | Done |
| 4 | Observability — OTel tracing, Prometheus, Grafana, Tempo, Loki | Done |
| 5 | Testing & Evaluation — unit tests, integration tests, RAG eval | Done |
| **6** | **CI/CD — GitHub Actions (lint, test, build, evaluation)** | **Planned** |
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
├── eval/                     # RAG evaluation framework
│   ├── corpus.json           # Documents to ingest before each eval run
│   ├── eval_set.json         # (question, key_point) pairs — independent from corpus
│   ├── run_eval.py           # Orchestrates ingest → query → judge → report
│   └── reports/              # Timestamped HTML reports (gitignored)
├── infra/                    # OTel collector, Prometheus, Loki, Tempo, Grafana configs
├── docker-compose.yml        # Full local stack
├── docker-compose.eval.yml   # Isolated eval stack (ephemeral DB, separate ports)
├── Makefile                  # Root-level make targets
├── pytest.ini                # Root pytest config (testpaths = shared)
└── conftest.py               # Sets TELEMETRY_ENABLED=false for all tests
```

### Key source paths

| Path | What it is |
|---|---|
| `services/ingestion-service/ingestion/pipelines/ingest_pipeline.py` | Core ingestion logic |
| `services/ingestion-service/ingestion/repositories/in_memory/` | Fake repos used in tests |
| `services/query-service/query/pipelines/query_pipeline.py` | LangGraph RAG graph |
| `services/query-service/query/pipelines/state.py` | `QueryState` TypedDict |
| `services/query-service/query/models/chunk_result.py` | `ChunkResult` dataclass |
| `services/query-service/query/core/embedder.py` | `Embedder` Protocol |
| `services/query-service/query/core/generator.py` | `Generator` Protocol |
| `services/query-service/query/repositories/base.py` | `ChunkRepository` Protocol |
| `shared/shared/telemetry.py` | `@traced`, `init_telemetry`, `instrument_app` |

---

## Architecture Decisions

### Layered architecture (both services)
`API → Pipeline → Repositories / Core → External (DB, OpenAI)`

### Protocol-based abstractions
All external dependencies (`Embedder`, `Generator`, `ChunkRepository`) are defined as `Protocol` classes. Concrete implementations live in `query/core/providers/` and `query/repositories/postgres/`. Tests substitute fakes via constructor injection.

### Package naming
Each service's Python package is named after the service (`ingestion/`, `query/`) rather than a generic `app/`. This avoids namespace collisions when running tests across the monorepo and makes imports unambiguous.

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
- **`ChunkResult.content` field:** Currently named `content`. Do not rename unless explicitly asked.

---

## Testing

### Running tests

```bash
# Unit tests across all services + shared (from repo root)
make test-all

# Integration tests — spins up real Postgres via testcontainers (per-service venvs)
make test-int

# RAG evaluation — builds isolated Docker stack, runs eval, tears down
make eval

# Per-service unit tests
cd services/ingestion-service && make test
cd services/query-service && make test

# Per-service integration tests
cd services/ingestion-service && make test-int
cd services/query-service && make test-int
```

### Test philosophy

- **Unit tests**: exercise one class/function with injected fakes, no I/O
- **Integration tests**: hit real Postgres+pgvector via testcontainers; marked `@pytest.mark.integration` and excluded from the default `make test` target
- **RAG evaluation**: end-to-end quality check against a fixed corpus using LLM-as-judge scoring; exits non-zero if pass rate falls below 80%

### Test files

| File | Covers |
|---|---|
| `services/ingestion-service/tests/test_chunker.py` | `Chunker.split` |
| `services/ingestion-service/tests/test_ingest_pipeline.py` | `IngestionPipeline.run` with fakes |
| `services/ingestion-service/tests/test_integration.py` | Ingestion pipeline end-to-end against real Postgres |
| `services/query-service/tests/test_query_pipeline.py` | `QueryPipeline` nodes, ranking threshold, state transitions with fakes |
| `services/query-service/tests/test_integration.py` | Query pipeline end-to-end against real Postgres |
| `shared/shared/tests/test_telemetry.py` | `@traced` decorator |

### Integration test design notes

- A session-scoped `pg_dsn` fixture starts the testcontainer once per test run; a function-scoped `clean_tables` fixture truncates tables between tests.
- The query-service integration tests seed data via raw SQL — not through the ingestion pipeline — to keep the test boundary tight.
- Integration tests are excluded from unit test runs via `--ignore=tests/test_integration.py` in each service's `make test` target.
- Each service runs integration tests in its own venv (`.venv/bin/pytest`). The root `make test-int` delegates via `$(MAKE) -C`.

### RAG evaluation design notes

- `docker-compose.eval.yml` uses `name: rag-eval` for project isolation, `tmpfs` for an ephemeral Postgres (fresh on every run), and separate ports (8002/8003) to avoid conflicts with the dev stack.
- `eval/corpus.json` and `eval/eval_set.json` are intentionally independent — there is no positional alignment between them.
- The eval script uses only stdlib + `openai` (no service venv); `openai` is listed in the root `requirements.txt`.
- HTML reports are written to `eval/reports/` (gitignored); the directory is tracked via `.gitkeep`.

---

## Development Workflow

### Local (no Docker)

```bash
make install      # install root requirements
make test-all     # unit tests across all services + shared
make test-int     # integration tests (requires Docker for testcontainers)
make lint         # pylint services
make format       # black .
make eval         # end-to-end RAG evaluation (requires Docker + OPENAI_API_KEY)
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

### Phase 6 — CI/CD

GitHub Actions workflows needed:
- **lint-and-test**: `black --check`, `pylint`, `pytest` (unit only, no integration)
- **integration**: spin up Postgres service container, run integration tests
- **build**: `docker build` both service images
- **evaluation**: run RAG eval (`make eval`), fail if quality drops below threshold

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
