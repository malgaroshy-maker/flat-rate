# Plan: RAG Quality Layer

## Phase 1: Embedding Quality
Validate model isolation in the vector space.
- Write `embedding_quality.py` — intra/inter-model cosine similarity
- Write `test_retrieval.py` — model isolation assertions

## Phase 2: Retrieval Metrics
Measure how well ChromaDB finds the right chunks.
- Write `retrieval_metrics.py` — MRR, NDCG, precision@k
- Extend `test_retrieval.py` — metric threshold assertions

## Phase 3: Calibration
Verify confidence intervals are actually calibrated.
- Write `calibration.py` — held-out split, calibration error, bias detection
- Write `test_calibration.py` — calibration score assertions

## Phase 4: Drift Detection
Detect data distribution shifts over time.
- Write `drift.py` — PSI computation, time-window analysis
- Extend `test_calibration.py` — drift threshold assertions

## Phase 5: Explainability + Observability
Show users why estimates were given and track performance.
- Modify `query_engine.py` — add `explain_estimate()`, latency tracking
- Modify `vector_store.py` — add `search_with_metadata()`
- Write `pipeline_observability.py` — timing distributions

## Phase 6: Documentation
Update project .md files to reflect new QA layer.
- Update `STATUS.md` — add Phase 8 entry
- Update `AGENTS.md` — add qa/ directory reference
- Update `implementation-summary.md` — add Phase 8 section
