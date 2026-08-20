# Testing

The project uses three distinct testing layers, each with a clear scope and isolation strategy.

---

## Running tests

```bash
# Unit tests across all services + shared (from repo root)
make test

# Integration tests — spins up real Postgres via testcontainers
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

---

## Test layers

### Unit tests

Exercise one class or function with injected fakes. No I/O, no database, no network.

- Fakes (`FakeEmbedder`, `FakeGenerator`, `FakeChunkRepository`) satisfy the Protocol interfaces and are passed as constructor arguments — no `monkeypatch`.
- Coverage: pipeline node behaviour, ranking threshold logic, state transitions.

### Integration tests

Hit a real Postgres+pgvector instance via [testcontainers](https://testcontainers.com/). Marked `@pytest.mark.integration` and excluded from the default `make test` target.

- A session-scoped `pg_dsn` fixture starts the container once per run; a function-scoped `clean_tables` fixture truncates tables between tests.
- The query-service integration tests seed data via raw SQL — not through the ingestion pipeline — to keep the test boundary tight.
- Integration tests run using the consolidated root venv. The root `make test-int` delegates via `$(MAKE) -C` into each service directory.

### RAG evaluation

End-to-end quality check against a fixed corpus. Runs the full production stack in Docker and scores each answer with [RAGAS](https://docs.ragas.io/en/stable/) — faithfulness, context recall, context precision, and answer relevancy — rather than a single hand-rolled LLM judge. Exits non-zero if **any metric's mean score** falls below **80%**, making it CI-gate-ready.

```
eval/
├── corpus.json       # documents to ingest before each eval run
├── eval_set.json     # (question, reference) pairs — independent from corpus
├── run_eval.py       # orchestrates ingest → query → score → report
├── requirements.in   # eval-only deps (ragas, langchain-openai, openai) — isolated from root/service venvs
├── requirements.txt  # pinned, compiled from requirements.in
├── .venv/            # provisioned by `make eval`, gitignored
└── reports/          # timestamped HTML reports (gitignored)
```

Workflow:
1. `docker-compose.eval.yml` starts an isolated stack (`name: rag-eval`) on separate ports (8002/8003) with a `tmpfs`-backed Postgres — fresh on every run.
2. `run_eval.py` ingests `corpus.json` via the ingestion API, then queries each entry in `eval_set.json` via the query API, collecting each answer's retrieved chunks (from the `/query` response's `sources[].text`) alongside the `reference`.
3. The collected samples are scored in a single batched `ragas.evaluate()` call, using a LangChain-wrapped OpenAI model (`gpt-4o-mini`) as the evaluator LLM plus an OpenAI embeddings model (needed for answer relevancy).
4. A timestamped HTML report is written to `eval/reports/`, breaking down all four metrics per question and as means, alongside a per-metric PASS/FAIL gate.

`corpus.json` and `eval_set.json` are intentionally independent — there is no positional alignment between them. The eval script's dependencies (`ragas`, `langchain-openai`, `openai`) are pinned in `eval/requirements.txt` and installed into their own `eval/.venv`, isolated from the root and service dependency graphs — see [Development](development.md#managing-dependencies).

---

## Test file map

| File | Covers |
|---|---|
| `services/ingestion-service/tests/test_chunker.py` | `Chunker.split` |
| `services/ingestion-service/tests/test_ingest_pipeline.py` | `IngestionPipeline.run` with fakes |
| `services/ingestion-service/tests/test_integration.py` | Ingestion pipeline end-to-end against real Postgres |
| `services/query-service/tests/test_query_pipeline.py` | `QueryPipeline` nodes, ranking threshold, state transitions with fakes |
| `services/query-service/tests/test_integration.py` | Query pipeline end-to-end against real Postgres |
| `shared/shared/tests/test_telemetry.py` | `@traced` decorator |
