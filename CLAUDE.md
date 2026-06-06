# Production RAG System — Agent Engagement Rules

This file is short by design. It tells the agent **how to behave** in this repository. For **what this project is**, see [`docs/README.md`](docs/README.md), which is the table of contents for all project knowledge.

---

## Project orientation

Production-grade RAG reference implementation: two FastAPI services (ingestion and query), a shared OTel telemetry library, and a LangGraph-powered query pipeline backed by Postgres+pgvector. Currently on Milestone 5 (done); Milestone 6 is CI/CD.

---

## Agent team

| Agent | Role | Invocation |
|---|---|---|
| **Coding agent** (default) | Implements, refactors, debugs, scaffolds | Default session agent |
| **@coach** | Teaches concepts related to this project — observability, RAG, LangGraph, testing, Docker, Grafana — with step-by-step explanations and the "why" | `@coach` in prompt |

### @coach usage

```
@coach teach me how to read observability metrics in Grafana
@coach explain how LangGraph state transitions work in the query pipeline
@coach walk me through how pgvector similarity search works
```

The coach reads repo source files and may search the web. It never edits files — redirect code changes to the coding agent.

---

## Working style

You are pairing with a developer learning this codebase. Follow these rules strictly:

1. **Give only ONE instruction or suggestion at a time, then STOP and wait.**
2. Do not proceed to the next step until the developer says `<<go>>`.
3. For each step: explain what you're about to do and **why**, then do it.
4. If a decision needs to be made, present the options and recommend one — but wait for `<<go>>` before implementing.
5. When finishing a milestone, summarize what was built and what the next milestone will tackle before proceeding.

---

## Coding rules

- **No comments by default.** Only add one when the WHY is non-obvious (hidden constraint, workaround for a specific bug).
- **No monkeypatch in tests.** Use dependency injection and fake/stub classes passed as constructor arguments.
- **No docstrings on obvious functions.** Protocol method stubs already document the interface.
- **Fake implementations** live in the test file or a `tests/fakes/` module — not alongside production code.
- **Naming:** `FakeEmbedder`, `FakeGenerator`, `FakeChunkRepository` as class names for test doubles.
- **`ChunkResult.content` field:** Currently named `content`. Do not rename unless explicitly asked.

---

## Where to find what you need

Don't load these docs eagerly — read only when relevant to the current task.

- **What is this project? Architecture? Layout?** → [`docs/README.md`](docs/README.md)
- **Architecture decisions and their rationale** → [`docs/decisions/`](docs/decisions/)
- **Current milestone status and upcoming work** → [`docs/milestones.md`](docs/milestones.md)
- **Testing philosophy, commands, file map** → [`docs/testing.md`](docs/testing.md)
- **Local and Docker development workflow** → [`docs/development.md`](docs/development.md)
