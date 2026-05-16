"""Tests for retrieval metrics and embedding quality modules."""

import pytest

from qa.embedding_quality import IsolationReport, evaluate_embedding_isolation
from qa.retrieval_metrics import RetrievalReport, evaluate_retrieval


class TestRetrievalMetrics:
    def test_report_structure(self):
        report = evaluate_retrieval(n_results=5, max_queries=5)
        assert isinstance(report, RetrievalReport)
        assert 0 <= report.mrr <= 1
        assert 0 <= report.precision_at_1 <= 1
        assert 0 <= report.precision_at_3 <= 1
        assert 0 <= report.precision_at_5 <= 1
        assert 0 <= report.ndcg_at_3 <= 1
        assert 0 <= report.ndcg_at_5 <= 1
        assert report.queries_run <= 5

    def test_per_query_structure(self):
        report = evaluate_retrieval(n_results=5, max_queries=3)
        assert len(report.per_query) <= 3
        for entry in report.per_query:
            assert "chunk_id" in entry
            assert "rank" in entry
            assert entry["rank"] >= 1
            assert "reciprocal_rank" in entry
            assert 0 < entry["reciprocal_rank"] <= 1

    def test_department_filter(self):
        report = evaluate_retrieval(n_results=3, max_queries=5, department_filter="نافطه")
        assert isinstance(report, RetrievalReport)
        assert 0 <= report.mrr <= 1

    def test_empty_max_queries(self):
        report = evaluate_retrieval(n_results=3, max_queries=0)
        assert report.queries_run == 0
        assert report.mrr == 0.0


class TestEmbeddingQuality:
    def test_report_structure(self):
        report = evaluate_embedding_isolation()
        assert isinstance(report, IsolationReport)
        assert report.intra_model_mean >= 0
        assert report.inter_model_mean >= 0
        assert report.models_tested >= 0

    def test_isolation_ratio(self):
        report = evaluate_embedding_isolation()
        if report.models_tested >= 2:
            assert report.isolation_ratio >= 0
            assert report.intra_model_mean > 0

    def test_per_model_structure(self):
        report = evaluate_embedding_isolation()
        for entry in report.per_model:
            assert "model" in entry
            assert "chunk_count" in entry
            assert "intra_mean" in entry
            assert "inter_mean" in entry
            assert entry["chunk_count"] >= 2
