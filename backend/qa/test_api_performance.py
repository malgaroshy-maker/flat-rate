"""Performance test cases for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app
from qa.api_performance import benchmark_concurrent, benchmark_endpoint


@pytest.fixture
def client():
    return TestClient(app)


def _client_factory():
    return TestClient(app)


class TestPerformance:
    def test_health_response_time(self, client):
        report = benchmark_endpoint(
            client, "GET", "/api/health", iterations=10, sla_ms=50.0
        )
        assert report.median_ms <= report.sla_ms * 2, (
            f"Health median {report.median_ms}ms > {report.sla_ms * 2}ms"
        )

    def test_query_response_time(self, client):
        report = benchmark_endpoint(
            client, "POST", "/api/query",
            params={"q": "فرامل", "n": 3},
            iterations=5,
            sla_ms=200.0,
        )
        assert report.median_ms <= report.sla_ms * 3, (
            f"Query median {report.median_ms}ms > {report.sla_ms * 3}ms"
        )

    def test_dictionary_list_response_time(self, client):
        report = benchmark_endpoint(
            client, "GET", "/api/dictionary", iterations=10, sla_ms=100.0
        )
        assert report.median_ms <= report.sla_ms * 3, (
            f"Dict list median {report.median_ms}ms > {report.sla_ms * 3}ms"
        )

    def test_query_concurrent(self):
        report = benchmark_concurrent(
            _client_factory, "POST", "/api/query",
            params={"q": "زيت", "n": 3},
            concurrency=5,
            sla_ms=2000.0,
        )
        assert report.concurrent_failures == 0, f"Concurrent query failures: {report.concurrent_failures}"

    def test_health_concurrent(self):
        report = benchmark_concurrent(
            _client_factory, "GET", "/api/health",
            concurrency=10,
            sla_ms=200.0,
        )
        assert report.concurrent_failures == 0

    def test_pdf_export_response_time(self, client):
        report = benchmark_endpoint(
            client, "POST", "/api/export/pdf",
            params={"q": "فرامل"},
            iterations=3,
            sla_ms=500.0,
        )
        assert report.median_ms <= report.sla_ms * 3, (
            f"PDF median {report.median_ms}ms > {report.sla_ms * 3}ms"
        )

    def test_query_empty_no_crash(self, client):
        resp = client.post("/api/query", params={"q": "", "n": 5})
        assert resp.status_code < 500

    def test_chat_sessions_response_time(self, client):
        report = benchmark_endpoint(
            client, "GET", "/api/chat/sessions", iterations=5, sla_ms=100.0
        )
        assert report.median_ms <= report.sla_ms * 5
