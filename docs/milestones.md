# Milestones

| Milestone | Focus | Status |
|---|---|---|
| **1** | Foundation — monorepo structure, architecture definition | Done |
| **2** | Ingestion Pipeline — chunking, embeddings, pgvector storage | Done |
| **3** | Query Pipeline — LangGraph RAG workflow, `/query` endpoint | Done |
| **4** | Observability — OpenTelemetry tracing, Prometheus metrics, Grafana, Tempo, Loki | Done |
| **5** | Testing & Evaluation — unit tests, integration tests, RAG evaluation framework | Done |
| **6** | CI/CD — GitHub Actions (lint, test, build, evaluation) | Planned |
| **7** | Deployment — Terraform on Azure + AWS, managed Postgres | Planned |
| **8** | Documentation & Polish — final diagrams, onboarding docs, demo workflows | Planned |

---

## Milestone 6 — CI/CD

GitHub Actions workflows needed:

- **lint-and-test**: `black --check`, `pylint`, `pytest` (unit only, no integration)
- **integration**: spin up Postgres service container, run integration tests
- **build**: `docker build` both service images
- **evaluation**: run RAG eval (`make eval`), fail if quality drops below threshold

---

## Milestone 7 — Deployment

- Terraform modules for Azure (AKS or Container Apps) and/or AWS (ECS or EKS)
- Managed Postgres with pgvector extension enabled (Azure Flexible Server or RDS)
- Secrets: OpenAI API key via Key Vault / Secrets Manager
- OTel collector sidecar or managed APM

---

## Milestone 8 — Documentation & Polish

- Architecture diagrams (Mermaid already exists in READMEs — may need updates)
- Onboarding walkthrough (end-to-end: ingest → query → observe in Grafana)
- Demo workflow script or Makefile targets
