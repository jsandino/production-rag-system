# Development

---

## Local (no Docker)

All make targets assume the root venv is active. Activate it once per session before running any commands:

```bash
source .venv/bin/activate
```

```bash
make install      # install dev tools + all service runtime deps in root .venv
make hooks        # register pre-commit hooks (run once after cloning)
make test-all     # unit tests across all services + shared
make test-int     # integration tests (requires Docker for testcontainers)
make lint         # ruff + pylint across all services
make format       # ruff format .
make eval         # end-to-end RAG evaluation (requires Docker + OPENAI_API_KEY)
```

Set `TELEMETRY_ENABLED=false` to disable OTel export in local Python runs without a collector.

---

## Docker (full stack)

```bash
export OPENAI_API_KEY=your_key_here
make docker-up     # builds and starts everything
make docker-ingest # smoke-test ingestion
make docker-query  # smoke-test query
make docker-down
make docker-reset  # full wipe + rebuild
```

---

## Observability stack

Available when running the Docker stack:

| Service | URL |
|---|---|
| Ingestion API | http://localhost:8000 |
| Query API | http://localhost:8001 |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090/targets |
