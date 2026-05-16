# Plan: Service Layer & Pipeline Orchestration

## Phase 1: Pipeline Stages
Define discrete stage interfaces.
- Write `pipeline_stages.py` — EmbedStage, SearchStage, ComputeStage, ExplainStage, GenerateStage
- Write `quality_gates.py` — stage-specific validation checks

## Phase 2: Orchestrator
Build the pipeline coordinator.
- Write `orchestrator.py` — PipelineOrchestrator with state tracking, quality gates, timing

## Phase 3: Service Layer
Create high-level services.
- Write `query_service.py` — query API using orchestrator
- Write `chat_service.py` — chat API using orchestrator

## Phase 4: Router Integration
Wire services into existing routers.
- Modify `routers/query.py` — add optional orchestrator path
- Modify `routers/chat.py` — add optional orchestrator path

## Phase 5: Verification & Docs
- Run full test suite, verify all pass
- Update .md files
