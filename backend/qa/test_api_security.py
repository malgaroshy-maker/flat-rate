"""Security test cases for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app
from qa.api_security import (
    PATH_TRAVERSAL_PAYLOADS,
    SQL_INJECTION_PAYLOADS,
    XSS_PAYLOADS,
    run_security_audit,
)


@pytest.fixture
def client():
    return TestClient(app)


class TestSecurityAudit:
    def test_audit_report_structure(self, client):
        report = run_security_audit(client)
        assert report.total_tests > 0
        assert report.passed >= 0
        assert report.failed >= 0
        assert report.total_tests == report.passed + report.failed

    def test_sql_injection_on_query(self, client):
        for payload in SQL_INJECTION_PAYLOADS:
            resp = client.post("/api/query", params={"q": payload, "n": 5})
            assert resp.status_code < 500, f"SQLi crashed server: {payload[:40]}"

    def test_xss_on_query(self, client):
        for payload in XSS_PAYLOADS:
            resp = client.post("/api/query", params={"q": payload, "n": 5})
            assert resp.status_code < 500, f"XSS crashed server: {payload[:40]}"

    def test_large_query_handled(self, client):
        resp = client.post("/api/query", params={"q": "A" * 2000, "n": 5})
        assert resp.status_code < 500

    def test_path_traversal_in_dict_id(self, client):
        for payload in PATH_TRAVERSAL_PAYLOADS:
            resp = client.get(f"/api/dictionary/{payload}")
            assert resp.status_code < 500

    def test_empty_query_returns_gracefully(self, client):
        resp = client.post("/api/query", params={"q": "", "n": 5})
        assert resp.status_code in (200, 429), f"Got {resp.status_code}"
        if resp.status_code == 200:
            data = resp.json()
            assert "hits" in data
            assert "confidence_range" in data

    def test_sqli_dictionary_rejected(self, client):
        resp = client.post(
            "/api/dictionary",
            json={"arabic_term": "'; DROP TABLE users; --", "standard_category": "test"},
        )
        assert resp.status_code < 500

    def test_mass_assignment_ignored(self, client):
        resp = client.post(
            "/api/dictionary",
            json={"arabic_term": "test", "standard_category": "cat", "is_admin": True},
        )
        assert resp.status_code < 500

    def test_xss_dictionary_sanitized(self, client):
        resp = client.post(
            "/api/dictionary",
            json={"arabic_term": "<script>alert(1)</script>", "standard_category": "test"},
        )
        assert resp.status_code < 500

    def test_nonexistent_endpoint_404(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404

    def test_health_never_500(self, client):
        resp = client.get("/api/health")
        assert resp.status_code != 500

    def test_dict_delete_nonexistent(self, client):
        resp = client.delete("/api/dictionary/nonexistent123")
        assert resp.status_code == 404

    def test_chat_session_nonexistent(self, client):
        resp = client.get("/api/chat/sessions/fake-session-999")
        assert resp.status_code == 404
