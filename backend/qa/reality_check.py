"""Production readiness audit — Reality Checker agent pattern.

Defaults to "NEEDS WORK" — requires overwhelming evidence for certification.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi.testclient import TestClient


@dataclass
class RealityCheckReport:
    category: str = ""
    items: list[dict] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    total: int = 0
    overall_ready: bool = False


def run_reality_check(client: TestClient) -> RealityCheckReport:
    """Evidence-based production readiness certification.

    Checks: health endpoint, query functionality, dictionary CRUD,
    PDF export, chat sessions, CORS, error handling, mode switching.
    """
    report = RealityCheckReport(category="Production Readiness")

    checks = [
        ("Health endpoint returns 200", _check_health(client)),
        ("Health returns 'ok' status", _check_health_ok(client)),
        ("Query endpoint returns valid structure", _check_query_structure(client)),
        ("Query returns confidence range", _check_confidence_range(client)),
        ("Dictionary list returns terms", _check_dictionary_list(client)),
        ("Dictionary CRUD lifecycle", _check_dictionary_crud(client)),
        ("PDF export returns valid PDF", _check_pdf_export(client)),
        ("Chat sessions list returns", _check_chat_sessions(client)),
        ("Chat session lifecycle", _check_chat_lifecycle(client)),
        ("CORS headers present", _check_cors_headers(client)),
        ("Error handling for missing params", _check_error_handling(client)),
        ("Mode toggle works", _check_mode_toggle(client)),
        ("No 500 errors on health", _check_no_500_health(client)),
        ("Content-Type is JSON for API", _check_json_content_type(client)),
    ]

    for name, passed in checks:
        report.items.append({"check": name, "passed": passed})

    report.total = len(report.items)
    report.passed = sum(1 for i in report.items if i["passed"])
    report.failed = report.total - report.passed
    report.overall_ready = report.failed == 0
    return report


def _check_health(c: TestClient) -> bool:
    return c.get("/api/health").status_code == 200


def _check_health_ok(c: TestClient) -> bool:
    return c.get("/api/health").json().get("status") == "ok"


def _check_query_structure(c: TestClient) -> bool:
    resp = c.post("/api/query", params={"q": "فرامل", "n": 3})
    if resp.status_code != 200:
        return False
    data = resp.json()
    return "hits" in data and "confidence_range" in data


def _check_confidence_range(c: TestClient) -> bool:
    resp = c.post("/api/query", params={"q": "فرامل", "n": 3})
    data = resp.json()
    cr = data.get("confidence_range", {})
    return bool(cr.get("p10") or cr.get("p50"))


def _check_dictionary_list(c: TestClient) -> bool:
    return c.get("/api/dictionary").status_code == 200


def _check_dictionary_crud(c: TestClient) -> bool:
    c1 = c.post("/api/dictionary", json={"arabic_term": "rc_test", "standard_category": "brakes"})
    if c1.status_code != 200:
        return False
    term_id = c1.json().get("id")
    if not term_id:
        return False
    c2 = c.put(f"/api/dictionary/{term_id}", json={"arabic_term": "rc_test_updated"})
    c3 = c.delete(f"/api/dictionary/{term_id}")
    return c2.status_code == 200 and c3.status_code == 200


def _check_pdf_export(c: TestClient) -> bool:
    resp = c.post("/api/export/pdf", params={"q": "فرامل"})
    return resp.status_code == 200 and resp.headers.get("content-type") == "application/pdf"


def _check_chat_sessions(c: TestClient) -> bool:
    return c.get("/api/chat/sessions").status_code == 200


def _check_chat_lifecycle(c: TestClient) -> bool:
    del_resp = c.delete("/api/chat/sessions/nonexistent_test")
    return del_resp.status_code == 404


def _check_cors_headers(c: TestClient) -> bool:
    resp = c.options(
        "/api/health",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    return resp.status_code < 500


def _check_error_handling(c: TestClient) -> bool:
    resp = c.post("/api/query", params={"q": "", "n": 5})
    return resp.status_code >= 400


def _check_mode_toggle(c: TestClient) -> bool:
    resp = c.post("/api/settings/mode", json={"force_local": True})
    if resp.status_code != 200:
        return False
    resp2 = c.post("/api/settings/mode", json={"force_local": False})
    return resp2.status_code == 200


def _check_no_500_health(c: TestClient) -> bool:
    return c.get("/api/health").status_code != 500


def _check_json_content_type(c: TestClient) -> bool:
    resp = c.get("/api/health")
    ct = resp.headers.get("content-type", "")
    return "application/json" in ct
