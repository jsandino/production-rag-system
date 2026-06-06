# 0005 — LangGraph StateGraph for the query pipeline

**Status**: Accepted
**Date**: 2026-04-06

## Context

The query pipeline has four ordered steps — embed, retrieve, rank, generate — where each step needs access to the accumulated state from prior steps (e.g. the generate step needs both the original query and the retrieved chunks). Managing state manually via function arguments becomes brittle as the pipeline grows: adding a step means updating every function signature in the chain.

## Decision

Model the query pipeline as a LangGraph `StateGraph`. Each step is a node that receives the full `QueryState` TypedDict and returns a partial dict; LangGraph merges the partial return into the shared state. Node order: `embed → retrieve → rank → generate`. The compiled graph is the single entry point called by the API layer.

## Alternatives considered

- **Plain Python function chain** — call `embed()`, pass result to `retrieve()`, etc. Rejected because passing state through function arguments scales poorly: each new field requires touching every function signature in the chain.
- **Custom step runner with explicit state object** — a hand-rolled orchestrator that holds a mutable state object. Rejected because it reinvents what LangGraph already provides, including the graph compilation, node introspection, and future streaming/branching capabilities.

## Consequences

- **Positive**: adding, removing, or reordering pipeline steps is a low-friction graph edit.
- **Positive**: `QueryState` is a single TypedDict that documents all state fields in one place.
- **Positive**: LangGraph's tracing hooks integrate naturally with the existing OTel instrumentation.
- **Negative**: introduces a LangGraph dependency; developers unfamiliar with it face a learning curve.
- **Neutral**: the compiled graph is opaque to inspection — debugging requires either LangGraph's tracing tools or explicit logging in each node.

## References

- Pipeline: [`services/query-service/query/pipelines/query_pipeline.py`](../../services/query-service/query/pipelines/query_pipeline.py)
- State: [`services/query-service/query/pipelines/state.py`](../../services/query-service/query/pipelines/state.py)
