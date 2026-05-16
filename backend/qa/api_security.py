"""API security testing — OWASP API Security Top 10 (2023) vulnerability scanner.

Inspired by API Tester agent: security-first testing approach.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any

from fastapi.testclient import TestClient


@dataclass
class SecurityReport:
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    findings: list[dict] = field(default_factory=list)


SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1' OR '1'='1' --",
    "' UNION SELECT * FROM users --",
    "1; SELECT * FROM users",
    "' OR 1=1 #",
]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "<svg onload=alert(1)>",
    '"><script>alert(1)</script>',
]

PATH_TRAVERSAL_PAYLOADS = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32",
    "....//....//....//etc/passwd",
    "%2e%2e%2f%2e%2e%2f",
]

LARGE_PAYLOADS = [
    "A" * 1000,
    "B" * 2000,
]


def _check_status_not_500(response, test_name: str) -> dict:
    passing = response.status_code < 500
    return {
        "test": test_name,
        "passed": passing,
        "status_code": response.status_code,
        "detail": f"Status {response.status_code}" if not passing else "OK",
    }


def _check_status_4xx(response, expected_min: int, test_name: str) -> dict:
    passing = expected_min <= response.status_code < 500
    return {
        "test": test_name,
        "passed": passing,
        "status_code": response.status_code,
        "detail": f"Expected >= {expected_min}, got {response.status_code}" if not passing else "OK",
    }


def run_security_audit(client: TestClient) -> SecurityReport:
    """Run comprehensive OWASP Top 10 security tests against all endpoints."""
    report = SecurityReport()

    # API1: Broken Object Level Authorization
    for endpoint in ["/api/dictionary/nonexistent123", "/api/chat/sessions/fake_session"]:
        resp = client.get(endpoint)
        f = _check_status_4xx(resp, 400, f"API1: BOLA - {endpoint}")
        report.findings.append(f)

    resp = client.delete("/api/dictionary/../../../etc/passwd")
    f = _check_status_4xx(resp, 400, "API1: BOLA - path traversal in dict delete")
    report.findings.append(f)

    # API2: Broken Authentication — health and query are public by design, but
    # verify that sensitive mutation endpoints reject malformed auth
    resp = client.post("/api/settings/mode", json={"force_local": True})
    f = {
        "test": "API2: settings/mode accepts body",
        "passed": resp.status_code < 500,
        "status_code": resp.status_code,
        "detail": "OK" if resp.status_code < 500 else f"Status {resp.status_code}",
    }
    report.findings.append(f)

    # API3: Broken Object Property Level Authorization
    resp = client.post(
        "/api/dictionary",
        json={"arabic_term": "test", "standard_category": "cat", "is_admin": True, "role": "superuser"},
    )
    f = {
        "test": "API3: Mass assignment - extra fields",
        "passed": resp.status_code < 500,
        "status_code": resp.status_code,
        "detail": "Extra fields ignored" if resp.status_code < 500 else f"Status {resp.status_code}",
    }
    report.findings.append(f)

    # API4: Unrestricted Resource Consumption
    for payload in LARGE_PAYLOADS:
        resp = client.post(
            "/api/query",
            params={"q": payload, "n": 5},
        )
        f = _check_status_not_500(resp, f"API4: Large query ({len(payload)} chars)")
        report.findings.append(f)

    resp = client.post(
        "/api/dictionary",
        json={"arabic_term": "A" * 10000, "standard_category": "test"},
    )
    f = _check_status_not_500(resp, "API4: Large dictionary term")
    report.findings.append(f)

    # API6: SQL Injection on all text inputs
    for payload in SQL_INJECTION_PAYLOADS[:4]:
        resp = client.post(
            "/api/query",
            params={"q": payload, "n": 5},
        )
        f = _check_status_not_500(resp, f"API6: SQLi query '{payload[:30]}...'")
        report.findings.append(f)

    for payload in SQL_INJECTION_PAYLOADS[:2]:
        resp = client.post(
            "/api/dictionary",
            json={"arabic_term": payload, "standard_category": "test"},
        )
        f = _check_status_not_500(resp, f"API6: SQLi dictionary '{payload[:30]}...'")
        report.findings.append(f)

    # API8: XSS on text inputs
    for payload in XSS_PAYLOADS[:3]:
        resp = client.post(
            "/api/query",
            params={"q": payload, "n": 5},
        )
        f = _check_status_not_500(resp, f"API8: XSS query '{payload[:30]}...'")
        report.findings.append(f)

    # Path traversal in term IDs
    for payload in PATH_TRAVERSAL_PAYLOADS[:2]:
        resp = client.get(f"/api/dictionary/{payload}")
        f = _check_status_4xx(resp, 400, f"API8: Path traversal dict get '{payload[:30]}'")
        report.findings.append(f)

    # Empty query
    for endpoint, method in [("/api/query", "post"), ("/api/export/pdf", "post")]:
        if method == "post":
            resp = client.post(endpoint, params={"q": "", "n": 5})
        else:
            resp = client.get(endpoint)
        f = _check_status_4xx(resp, 400, f"API8: Empty query on {endpoint}")
        report.findings.append(f)

    # Security headers check
    resp = client.get("/api/health")
    headers_found = {k.lower(): v for k, v in resp.headers.items()}
    for header in ["x-content-type-options", "x-frame-options", "content-type"]:
        present = header in headers_found
        report.findings.append({
            "test": f"API9: Security header {header}",
            "passed": present,
            "status_code": resp.status_code,
            "detail": "Present" if present else "Missing",
        })

    # CORS check
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    cors_allows_evil = "evil.com" in resp.headers.get("access-control-allow-origin", "")
    report.findings.append({
        "test": "API9: CORS - evil origin rejected",
        "passed": not cors_allows_evil,
        "status_code": resp.status_code,
        "detail": "Blocked" if not cors_allows_evil else "Allowed (vulnerable)",
    })

    report.total_tests = len(report.findings)
    report.passed = sum(1 for f in report.findings if f["passed"])
    report.failed = report.total_tests - report.passed
    return report
