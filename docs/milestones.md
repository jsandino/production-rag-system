# Milestones

Status and progress are tracked in the [README](../README.md). This document contains implementation notes for upcoming milestones.

---

## Milestone 7 — RAGAS Integration

- Replace `eval/run_eval.py`'s binary LLM-as-judge with [RAGAS](https://docs.ragas.io/en/stable/) metrics: faithfulness, context precision, context recall, answer relevancy
- Capture `retrieved_contexts` from the existing `/query` response's `sources[].text` — no query-service changes needed, the data is already returned
- Add `ragas` and a LangChain LLM wrapper as eval-only dependencies (current script is stdlib + `openai` only)
- Restructure `_evaluate()`/`_report()` from a per-item pass/fail loop to a single batched `evaluate()` call with per-metric threshold gates

---

## Milestone 8 — Documentation & Polish

- Architecture diagrams (Mermaid already exists in READMEs — may need updates)
- Onboarding walkthrough (end-to-end: ingest → query → observe in Grafana)
- Demo workflow script or Makefile targets
