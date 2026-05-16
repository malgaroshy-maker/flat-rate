# Spec: RAG Quality Layer (Model QA + AI Engineer)

> Inspired by agency-agents: Model QA Specialist + AI Engineer patterns.
> Parent project: specs/001-labor-estimator/

## 1. Objective

Add a dedicated QA layer to the RAG pipeline that measures, validates, and explains estimate quality. Current system outputs P10/P50/P90 confidence intervals with no calibration verification, no retrieval accuracy metrics, no drift detection, and no explainability.

## 2. Architecture

```
backend/qa/
├── __init__.py
├── calibration.py          # Compare predicted ranges vs held-out actuals
├── drift.py                # PSI across time windows
├── retrieval_metrics.py    # MRR, NDCG, precision@k
├── embedding_quality.py    # Model isolation validation
├── pipeline_observability.py # Per-stage latency tracking
├── test_calibration.py     # Pytest: calibration error thresholds
└── test_retrieval.py       # Pytest: retrieval metric assertions
```

## 3. Five QA Domains

### 3.1 Calibration Testing (Model QA Specialist)
- Split raw records by date: early (training) vs recent (test)
- For each (Model, Code) group, predict P10-P90 from training
- Measure: % of test records falling within predicted range
- Calibration score target: ≥80% within-range rate
- Detect systematic over/under-estimation bias

### 3.2 Drift Detection (Model QA Specialist)
- PSI (Population Stability Index) of QTY distributions across monthly windows
- Flag groups with PSI ≥ 0.25 (significant shift)
- Identify seasonal patterns or trend changes

### 3.3 Retrieval Metrics (AI Engineer)
- Ground truth: each chunk's description → that chunk should rank #1
- MRR (Mean Reciprocal Rank): average 1/rank of correct chunk
- precision@k: % of queries where correct chunk is in top-k
- NDCG@k: normalized discounted cumulative gain

### 3.4 Embedding Quality (AI Engineer)
- Intra-model vs inter-model cosine similarity
- Verify model isolation: same-model chunks cluster tighter than cross-model
- Isolation ratio: intra-model similarity / inter-model similarity

### 3.5 Pipeline Observability (AI Engineer)
- Per-stage latency: embed, search, compute, generate
- Timing distributions (mean, p50, p95, p99)
- Bottleneck identification

## 4. Integration Points

| Module | Input | Output | Consumer |
|--------|-------|--------|----------|
| calibration.py | XLSX raw records, ChromaDB metadata | CalibrationReport | query_engine.py (explain_estimate) |
| drift.py | XLSX raw records | DriftReport | Monitoring dashboard |
| retrieval_metrics.py | ChromaDB collection | RetrievalReport | query_engine.py |
| embedding_quality.py | ChromaDB vectors | IsolationReport | Ingestion pipeline |
| pipeline_observability.py | query_engine.py timings | LatencyReport | Health endpoint |

## 5. Non-functional requirements
- All QA modules run independently (no impact on production query path)
- Calibration uses raw XLSX re-parse (no shared state with ChromaDB)
- Drift computation O(n) where n = chunks × time_windows
- Tests must run < 30 seconds (use cached/fixture data where needed)
