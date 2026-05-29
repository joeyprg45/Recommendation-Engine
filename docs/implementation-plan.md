# GitHub MCP Demo Implementation Plan

Last updated: 2026-05-30

## Goal

Build synthetic GitHub MCP demo data that can be consumed by the current agent stack to infer member skills from:

- Issue timelines
- Push/commit history

The output should be directly usable as chat context.

## Scope

- Fully synthetic data aligned with `github.md`
- Incremental implementation in 8 phases
- One phase per commit and push

## Phases

1. T002: LambdaRank baseline implementation signal
2. T003: Feature store and CosmosDB signal
3. T004: API/plugin architecture signal
4. T005: Data quality and bug-fix signal
5. T011: Embedding + cache integration signal
6. T012: Hybrid reranker and cross-role collaboration signal
7. T013: API refactor and scalability signal
8. T014: Experimentation and statistics signal

## Data Layout

```
demo/github_mcp/
  raw/issues/*.json
  raw/pushes/*.json
  derived/member_skill_profiles.json
  derived/chat_context.json
```

## Processing

`scripts/build_skill_profiles.py`

- reads all `raw/issues` and `raw/pushes`
- computes weighted skill signals per member
- emits:
  - `derived/member_skill_profiles.json`
  - `derived/chat_context.json`
