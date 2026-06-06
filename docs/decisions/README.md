# Architecture Decision Records (ADRs)

Each ADR is a short, immutable record of a non-obvious design decision: what was chosen, what alternatives were considered, and why. ADRs explain the _"why"_ that won't otherwise be obvious from reading the code.

## When to write one

Write an ADR when:

- A design choice has more than one reasonable alternative
- The decision affects multiple files or modules
- The decision encodes a constraint that isn't visible from any single file
- A reviewer would otherwise ask "why did you do it this way?"

**Don't** write ADRs for trivial refactors, obvious naming choices, or decisions that are self-evident from the code.

## When to supersede

ADRs are immutable once committed. If a decision changes, write a _new_ ADR that supersedes the old one. Add `Supersedes: NNNN` to the new record and `Superseded by: NNNN` to the old one. This preserves the audit trail of why the design evolved.

## Numbering

Files are numbered sequentially: `NNNN-short-slug.md`. Numbers are never reused, even after supersession.

## Template

See [TEMPLATE.md](TEMPLATE.md). Keep ADRs short — one page is typical, two is the upper bound.

---

## Current ADRs

| # | Title | Status |
|---|---|---|
| 0001 | [Layered architecture](0001-layered-architecture.md) | Accepted |
| 0002 | [Protocol-based abstractions](0002-protocol-based-abstractions.md) | Accepted |
| 0003 | [Package naming by service](0003-package-naming.md) | Accepted |
| 0004 | [Unit of Work for ingestion](0004-unit-of-work.md) | Accepted |
| 0005 | [LangGraph query pipeline](0005-langgraph-query-pipeline.md) | Accepted |
| 0006 | [Shared telemetry library](0006-shared-telemetry.md) | Accepted |
