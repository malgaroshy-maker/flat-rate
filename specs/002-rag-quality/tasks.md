# Tasks — RAG Quality Layer

> **Parent:** specs/001-labor-estimator/ | **Status:** Phase 8 — with 14/15 tasks complete

## Phase 1: Embedding Quality
- [x] **1.1** Create `backend/qa/__init__.py`
- [x] **1.2** Create `backend/qa/embedding_quality.py` — intra/inter-model cosine similarity, isolation ratio
- [x] **1.3** Create `backend/qa/test_retrieval.py` — model isolation assertions

## Phase 2: Retrieval Metrics
- [x] **2.1** Create `backend/qa/retrieval_metrics.py` — MRR, NDCG@k, precision@k against ChromaDB
- [x] **2.2** Add retrieval metric tests to `backend/qa/test_retrieval.py`

## Phase 3: Calibration
- [x] **3.1** Create `backend/qa/calibration.py` — held-out date split, calibration error, bias report
- [x] **3.2** Create `backend/qa/test_calibration.py` — calibration score assertions

## Phase 4: Drift Detection
- [x] **4.1** Create `backend/qa/drift.py` — PSI computation, monthly window analysis, drift flags
- [x] **4.2** Add drift tests to `backend/qa/test_calibration.py`

## Phase 5: Explainability + Observability
- [x] **5.1** Modify `backend/vector_store.py` — add `search_with_metadata()` returning distances + IDs
- [x] **5.2** Modify `backend/query_engine.py` — add `explain_estimate()` returning chunk influence weights
- [x] **5.3** Modify `backend/query_engine.py` — add latency tracking decorator
- [x] **5.4** Create `backend/qa/pipeline_observability.py` — per-stage timing distributions

## Phase 6: Documentation
- [x] **6.1** Update `STATUS.md` — add Phase 8: RAG Quality row
- [x] **6.2** Update `AGENTS.md` — add qa/ directory reference
- [x] **6.3** Update `specs/001-labor-estimator/implementation-summary.md` — add Phase 8 section
- [ ] **6.4** Run `backend/tests/**` + `backend/qa/**` tests, verify all pass
