# Tasks — Service Layer & Pipeline Orchestration

> **Parent:** specs/001-labor-estimator/ | **Status:** Phase 11 — all tasks complete

## Phase 1: Pipeline Stages
- [x] **1.1** Create `backend/services/__init__.py`
- [x] **1.2** Create `backend/services/pipeline_stages.py` — stage definitions
- [x] **1.3** Create `backend/services/quality_gates.py` — stage validation

## Phase 2: Orchestrator
- [x] **2.1** Create `backend/services/orchestrator.py` — PipelineOrchestrator

## Phase 3: Service Layer
- [x] **3.1** Create `backend/services/query_service.py`
- [x] **3.2** Create `backend/services/chat_service.py`

## Phase 4: Router Integration
- [x] **4.1** Wire into `routers/query.py`
- [x] **4.2** Wire into `routers/chat.py` (adapter via chat_service.py)

## Phase 5: Verification & Docs
- [x] **5.1** Run `pytest tests qa -v`, verify all pass (76/76)
- [x] **5.2** Update `STATUS.md` — add Phase 11
- [x] **5.3** Update `AGENTS.md` — add services section
- [x] **5.4** Update `implementation-summary.md` — add Phase 11
