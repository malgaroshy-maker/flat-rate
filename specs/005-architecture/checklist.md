# Validation Checklist — Service Layer & Pipeline Orchestration

## P0 — Must pass

- [x] PipelineOrchestrator imports cleanly
- [x] All 5 pipeline stages defined and callable
- [x] Quality gates return (passed: bool, reason: str) tuples
- [x] Pipeline state tracks stage status per execution
- [x] query_service.py returns extended result with pipeline_state + explanation
- [x] chat_service.py delegates to existing chat_engine.py
- [x] All 76 existing tests pass unchanged

## P1 — Should pass

- [x] Failed quality gates log warnings, don't raise
- [x] Pipeline timing captured per stage (elapsed_ms)
- [x] Orchestrator works with both cloud and local modes
- [x] Backward-compatible — existing routers work without changes (orchestrate=false)

## P2 — Nice to have

- [x] Pipeline state serializable to JSON (returned in response)
- [ ] Stage retry logic for transient failures (not yet — V1)
- [ ] Orchestrator configurable via env vars (not yet — V1)
