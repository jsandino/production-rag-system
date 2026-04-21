# Production RAG Reference Implemenation

Production-grade RAG system showcasing ingestion & query pipelines, observability, and Azure deployment.

---

## Milestones

| Phase | Focus | Status |
|---|---|---|
| **1** | Foundation — monorepo structure, architecture definition | 🟢 Done |
| **2** | Ingestion Pipeline — chunking, embeddings, pgvector storage | 🟢 Done |
| **3** | Query Pipeline — LangGraph RAG workflow, `/query` endpoint | 🟢 Done |
| **4** | Observability — OpenTelemetry tracing, Prometheus metrics, Grafana, Tempo, Loki | 🟢 Done |
| **5** | Testing & Evaluation — unit tests, integration tests, RAG evaluation framework | 🔵 In Progress |
| **6** | CI/CD — GitHub Actions (lint, test, build, evaluation) | 🟡 Planned |
| **7** | Deployment — Terraform on Azure + AWS, managed Postgres | 🟡 Planned |
| **8** | Documentation & Polish — final diagrams, onboarding docs, demo workflows | 🟡 Planned |

---

## Architecture Overview

This system is designed as a production-style Retrieval-Augmented Generation (RAG) architecture with clear separation of concerns across four layers:

- Application Layer (services)
- Data Layer (storage & retrieval)
- AI Layer (LLM & embeddings)
- Observability Layer (metrics, logs, traces)

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

This layer provides full visibility into system behavior, performance, and failures.

### Components

- **OpenTelemetry Collector**
  - Central pipeline for traces and metrics

- **Tempo**
  - Distributed tracing backend

- **Prometheus**
  - Metrics collection (latency, throughput, ingestion stats)

- **Grafana**
  - Unified dashboard for traces, metrics, and logs visualization

- **Loki**
  - Log aggregation backend
  - Receives logs from the OTel collector via OTLP
  - Structured log fields (document name, chunk count, query, timings) are searchable in Grafana Explore

---

## System Architecture Diagram

```mermaid
flowchart LR

User[User / Client]

QueryService[Query Service - FastAPI + LangGraph]
IngestService[Ingestion Service - API to Batch Worker]

LLM[Azure OpenAI / LLM API]
Postgres[(Postgres + pgvector)]

OTEL[OpenTelemetry Collector]
Tempo[Tempo Traces]
Prometheus[Prometheus Metrics]
Loki[Loki Logs]
Grafana[Grafana Dashboards]

User --> QueryService
QueryService --> Postgres
IngestService --> Postgres
QueryService --> LLM

QueryService --> OTEL
IngestService --> OTEL

OTEL --> Tempo
OTEL --> Prometheus
OTEL --> Loki
Tempo --> Grafana
Prometheus --> Grafana
Loki --> Grafana
```
