# Production RAG System — Project Knowledge

This is the table of contents for all project knowledge. For agent engagement rules, see [CLAUDE.md](../CLAUDE.md).

---

## What is this project?

Production-grade RAG system showcasing ingestion & query pipelines, observability, and cloud deployment. Built as a reference implementation demonstrating how to structure, test, observe, and deploy a multi-service Python system.

---

## Monorepo layout

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

---

## Key source paths

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

## Architecture decisions

| # | Decision | Status |
|---|---|---|
| 0001 | [Layered architecture](decisions/0001-layered-architecture.md) | Accepted |
| 0002 | [Protocol-based abstractions](decisions/0002-protocol-based-abstractions.md) | Accepted |
| 0003 | [Package naming by service](decisions/0003-package-naming.md) | Accepted |
| 0004 | [Unit of Work for ingestion](decisions/0004-unit-of-work.md) | Accepted |
| 0005 | [LangGraph query pipeline](decisions/0005-langgraph-query-pipeline.md) | Accepted |
| 0006 | [Shared telemetry library](decisions/0006-shared-telemetry.md) | Accepted |

---

## More docs

- [Milestones](milestones.md) — milestone status and implementation notes for upcoming work
- [Testing](testing.md) — test philosophy, commands, file map, and design notes
- [Development](development.md) — local and Docker development workflow
