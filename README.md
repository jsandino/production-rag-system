# Production RAG Reference Implemenation

Production-grade RAG system showcasing ingestion & query pipelines, observability, and Azure deployment.

---

## Milestones

| Phase | Focus                                                                           | Status         |
| ----- | ------------------------------------------------------------------------------- | -------------- |
| **1** | Foundation — monorepo structure, architecture definition                        | 🟢 Done        |
| **2** | Ingestion Pipeline — chunking, embeddings, pgvector storage                     | 🟢 Done        |
| **3** | Query Pipeline — LangGraph RAG workflow, `/query` endpoint                      | 🟢 Done        |
| **4** | Observability — OpenTelemetry tracing, Prometheus metrics, Grafana, Tempo, Loki | 🟢 Done        |
| **5** | Testing & Evaluation — unit tests, integration tests, RAG evaluation framework  | 🟢 Done        |
| **6** | CI/CD — GitHub Actions (lint, test, build, evaluation)                          | 🟡 Planned     |
| **7** | Deployment — Terraform on Azure + AWS, managed Postgres                         | 🟡 Planned     |
| **8** | Documentation & Polish — final diagrams, onboarding docs, demo workflows        | 🟡 Planned     |

---

## Architecture Overview

This system is designed as a production-style Retrieval-Augmented Generation (RAG) architecture with clear separation of concerns across four layers:

- Application Layer (services)
- Data Layer (storage & retrieval)
- AI Layer (LLM & embeddings)
- Observability Layer (metrics, logs, traces)

### System Architecture Diagram

```mermaid
flowchart LR

User[User / Client]
IngestService["Ingestion Service<br/><small>API / Batch Worker</small>"]
QueryService["Query Service<br/><small>FastAPI + LangGraph</small>"]
LLM[Azure OpenAI / LLM API]
Postgres[(Postgres + pgvector)]
OTEL[OpenTelemetry Collector]

User --> QueryService
User --> IngestService
QueryService --> Postgres
IngestService -->|traces + logs| OTEL
IngestService --> Postgres
QueryService --> LLM
QueryService -->|traces + logs| OTEL

LLM ~~~ Postgres
```

---

## 1. Application Layer

This layer contains the core services responsible for interacting with users and processing data.

### Components

- **Query Service (FastAPI + LangGraph)**
  - Handles user queries
  - Orchestrates retrieval and generation workflow
  - Returns grounded responses with sources
  - See detailed design and usage: [`services/query-service/README.md`](services/query-service/README.md)

- **Ingestion Service (API → Batch Worker)**
  - Processes incoming documents
  - Performs chunking and embedding generation
  - Stores processed data in the data layer
  - See detailed design and usage: [`services/ingestion-service/README.md`](services/ingestion-service/README.md)

---

## 2. Data Layer

This layer stores all structured and unstructured RAG data.

### Components

- **Postgres + pgvector**
  - Stores document chunks
  - Stores embedding vectors
  - Stores metadata for filtering and retrieval

---

## 3. AI Layer

This layer provides all model capabilities required for retrieval and generation.

### Components

- **LLM API (Azure OpenAI / OpenAI)**
  - Generates final responses
  - Used in query service for answer synthesis

- **Embedding Model**
  - Converts text into vector representations
  - Used in both ingestion and query pipelines

---

## 4. Observability Layer

This layer provides full visibility into system behavior, performance, and failures across two separate data flows.

**Traces and logs** are pushed by both services to the OpenTelemetry Collector over OTLP/gRPC. The collector fans them out — traces to Tempo, logs to Loki.

**Metrics** bypass the collector entirely. Each service exposes a `GET /metrics` endpoint (via `prometheus-fastapi-instrumentator`), and Prometheus scrapes those endpoints directly on a 15-second interval.

Grafana sits in front of all three backends (Tempo, Loki, Prometheus) as a unified query and dashboard layer.

### Components

- **OpenTelemetry Collector** — receives and routes traces and logs only; does not handle metrics
- **Tempo** — distributed tracing backend; receives traces from the OTel Collector
- **Loki** — log aggregation backend; receives structured logs from the OTel Collector
- **Prometheus** — metrics backend; scrapes `/metrics` from each service directly
- **Grafana** — unified dashboard for all three signals

### Observability Components Diagram

```mermaid
flowchart LR

User[User / Client]
IngestService["Ingestion Service<br/><small>API / Batch Worker</small>"]
QueryService["Query Service<br/><small>FastAPI + LangGraph</small>"]
OTEL[OpenTelemetry Collector]
Tempo["Tempo<br/><small>(Traces)</small>"]
Loki["Loki<br/><small>(Logs)</small>"]
Prometheus["Prometheus<br/><small>(Metrics)</small>"]
Grafana[Grafana Dashboards]

User --> QueryService
User --> IngestService
QueryService -->|traces + logs| OTEL
IngestService -->|traces + logs| OTEL
OTEL --> Tempo
OTEL --> Loki
QueryService -->|scrapes /metrics| Prometheus
IngestService -->|scrapes /metrics| Prometheus
Tempo --> Grafana
Loki --> Grafana
Prometheus --> Grafana
```

_Arrows show data flow direction. Prometheus **scrapes** `/metrics` from each service on a 15-second interval (pull model). Grafana **queries** Tempo, Loki, and Prometheus to build dashboards (pull model)._

---

## 5. Testing & Evaluation

The project uses three distinct testing layers, each with a clear scope and isolation strategy.

### Unit Tests

Each service has its own test suite under `tests/` using injected fakes — no real database, no network calls.

- **Fakes over mocks**: `FakeEmbedder`, `FakeGenerator`, and `FakeChunkRepository` satisfy the Protocol interfaces and are passed as constructor arguments. No `monkeypatch`.
- **Coverage**: pipeline node behaviour, ranking threshold logic, state transitions.

```bash
make test-all          # runs unit tests across all services + shared
```

### Integration Tests

Integration tests spin up a real Postgres+pgvector instance via [testcontainers](https://testcontainers.com/) and exercise the full path from pipeline to database. They are isolated from unit tests and gated behind the `integration` pytest mark.

Each service manages its own integration test suite and venv:

```bash
make test-int          # runs integration tests for both services
# or per-service:
cd services/ingestion-service && make test-int
cd services/query-service && make test-int
```

Key design choices:

- A session-scoped `pg_dsn` fixture starts the container once per test run; a function-scoped `clean_tables` fixture truncates tables between tests.
- The query-service integration tests seed data via raw SQL — not through the ingestion pipeline — to keep the test boundary tight.

### RAG Evaluation

The eval framework measures answer quality end-to-end against a fixed corpus. It runs the full production stack (both services + Postgres) in Docker and scores each answer with an LLM-as-judge (GPT-4o-mini).

```
eval/
├── corpus.json       # documents to ingest before each eval run
├── eval_set.json     # (question, key_point) pairs — independent from corpus
├── run_eval.py       # orchestrates ingest → query → judge → report
└── reports/          # timestamped HTML reports (gitignored)
```

```bash
make eval             # builds eval stack, runs eval, tears down, exits non-zero on failure
```

Workflow:

1. `docker-compose.eval.yml` starts an isolated stack (`name: rag-eval`) on separate ports (8002/8003) with a `tmpfs`-backed Postgres — fresh on every run.
2. `run_eval.py` ingests `corpus.json` via the ingestion service API, then queries each entry in `eval_set.json` via the query service API.
3. Each answer is judged by GPT-4o-mini against the `key_point` for that question.
4. A timestamped HTML report is written to `eval/reports/`. The script exits non-zero if the pass rate falls below the **80% threshold**, making it CI-gate-ready.

---
