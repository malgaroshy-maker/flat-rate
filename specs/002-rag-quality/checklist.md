# Validation Checklist — RAG Quality Layer

## P0 — Must pass before phase completion

### Embedding Quality
- [x] `embedding_quality.py` imports cleanly with no errors
- [x] Intra-model similarity > inter-model similarity for >=90% of models
- [x] Isolation ratio computed and non-negative

### Retrieval Metrics
- [x] MRR >= 0.5 (correct chunk in top-2 on average)
- [x] precision@k computed for k=1,3,5
- [x] NDCG@k computed for k=1,3,5

### Calibration
- [x] Held-out date split produces training and test sets
- [x] Calibration score (within-range %) computed
- [x] Over-estimation and under-estimation rates computed
- [x] No division-by-zero or empty-group errors

### Drift Detection
- [x] PSI computed across monthly time windows
- [x] Groups with PSI >= 0.25 flagged
- [x] No negative PSI values

### Explainability
- [x] `explain_estimate()` returns chunk influence weights
- [x] Each hit has a contributed weight in the explanation
- [x] Explanation is JSON-serializable

### Observability
- [x] Latency tracking captures embed, search, compute, generate stages
- [x] Timing values are positive floats
- [x] No timing collisions in concurrent calls

## P1 — Should pass

- [x] All QA modules run without ChromaDB (rely on raw XLSX where possible)
- [x] Calibration handles edge cases: single-record groups, zero-QTY records
- [x] Drift handles missing months gracefully
- [x] explain_estimate() works with 1-hit and multi-hit results

## P2 — Nice to have

- [ ] Calibration report includes per-department breakdown
- [ ] Drift report includes visual trend direction (increasing/decreasing/stable)
- [ ] Retrieval metrics include per-department breakdown
- [ ] Observability data exportable as JSON for dashboarding
