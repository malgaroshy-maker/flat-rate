# Spec: Service Layer & Pipeline Orchestration

> Inspired by agency-agents: Backend Architect + Agents Orchestrator patterns.
> Parent project: specs/001-labor-estimator/

## 1. Objective

Refactor the monolithic `query_engine.py` (276 lines, 7 responsibilities) into a coordinated service layer with discrete pipeline stages, quality gates, and state tracking. Apply the Agents Orchestrator pattern to make the RAG pipeline observable and auditable.

## 2. Target Architecture

```
routers/
  query.py ──→ services/query_service.py ──→ services/orchestrator.py
  chat.py  ──→ services/chat_service.py  ──→       │
                                                   ├── Embed Stage
                                                   ├── Search Stage
                                                   ├── Compute Stage (confidence + outliers)
                                                   ├── Explain Stage
                                                   └── Generate Stage (LLM)

services/
  ├── __init__.py
  ├── orchestrator.py       # PipelineOrchestrator: stages → quality gates → state
  ├── pipeline_stages.py    # Stage definitions (Embed, Search, Compute, Explain, Generate)
  ├── quality_gates.py      # Quality checks between stages (non-null, valid range, etc.)
  ├── query_service.py      # High-level query API using orchestrator
  └── chat_service.py       # High-level chat API using orchestrator
```

## 3. Pipeline Stages

| Stage | Input | Output | Quality Gate |
|-------|-------|--------|--------------|
| Embed | query_text | embedding vector | vector non-null, correct dims |
| Search | embedding | ChromaDB hits | hits list non-empty |
| Compute | hits | confidence range + outliers | percentiles monotonic, p10 ≤ p50 ≤ p90 |
| Explain | hits + confidence | contribution weights | weights sum to ~1.0 |
| Generate | context + prompt | LLM response text | response non-empty, no error patterns |

## 4. Orchestrator Pattern (Agents Orchestrator)

- Each stage is a discrete callable with typed input/output
- Pipeline state tracked per execution (stage status, timing, errors)
- Quality gates checked between stages
- Failed gates log warnings but don't block (degraded mode)
- Full pipeline timing captured end-to-end

## 5. Backward Compatibility

- Existing `query_engine.py` functions preserved as thin wrappers
- Routers get optional `use_orchestrator` flag (default false for safety)
- All 76 existing tests must continue to pass
