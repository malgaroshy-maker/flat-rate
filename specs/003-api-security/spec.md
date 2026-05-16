# Spec: API Security & Performance (API Tester + Reality Checker)

> Inspired by agency-agents: API Tester + Reality Checker patterns.
> Parent project: specs/001-labor-estimator/

## 1. Objective

Harden the 8 backend API endpoints against OWASP API Security Top 10 (2023), add rate limiting, validate response times against SLAs, and produce a Reality Checker production readiness audit.

## 2. Architecture

```
backend/qa/
├── api_security.py          # OWASP Top 10 checks, input fuzzing, validation
├── api_performance.py        # Response time benchmarks, concurrent load
├── reality_check.py          # Production readiness audit + checklist
├── test_api_security.py      # Security test cases (16+ tests)
└── test_api_performance.py   # Performance test cases (10+ tests)

backend/
├── middleware/
│   ├── __init__.py
│   ├── security_headers.py   # X-Content-Type-Options, X-Frame-Options, etc.
│   ├── rate_limit.py         # In-memory sliding window rate limiter
│   └── input_sanitizer.py    # Input length/pattern validation
└── main.py                   # Add middleware
```

## 3. OWASP API Security Top 10 Coverage

| # | Risk | Mitigation |
|---|------|------------|
| API1:2023 | Broken Object Level Auth | Test term_id/session_id enumeration |
| API2:2023 | Broken Authentication | Test unauthenticated access |
| API3:2023 | Broken Object Property Level Auth | Test body field injection |
| API4:2023 | Unrestricted Resource Consumption | Rate limiting, request size limits |
| API5:2023 | Broken Function Level Auth | Test method override attacks |
| API6:2023 | Unrestricted Access to Sensitive Flows | Rate limit on dictionary/chat |
| API7:2023 | Server-Side Request Forgery | N/A (no outbound requests) |
| API8:2023 | Security Misconfiguration | CORS, security headers, debug mode |
| API9:2023 | Improper Inventory | Document all endpoints |
| API10:2023 | Unsafe Consumption of APIs | Input sanitization on all endpoints |

## 4. Performance SLAs

| Endpoint | Target | Type |
|----------|--------|------|
| GET /api/health | <50ms | Synchronous |
| POST /api/query | <200ms | RAG pipeline |
| POST /api/export/pdf | <500ms | PDF generation |
| GET /api/dictionary | <100ms | In-memory lookup |
| POST /api/chat/send | <5000ms | SSE streaming (first token) |

## 5. Security Middleware

- **Rate limit**: 30 req/min per endpoint (sliding window, in-memory)
- **Security headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Strict-Transport-Security, Content-Security-Policy
- **Input validation**: max 2000 chars for query text, max 500 for dictionary terms, reject control chars
- **Request size**: 1MB body limit on all POST endpoints
