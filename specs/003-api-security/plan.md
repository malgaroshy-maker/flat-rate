# Plan: API Security & Performance

## Phase 1: Security Audit
Audit existing endpoints for OWASP Top 10 gaps.
- Write `api_security.py` — input validation, fuzzing payloads, rate limit tests
- Write `test_api_security.py` — 16+ security test cases

## Phase 2: Performance Benchmarks
Measure and validate response times against SLAs.
- Write `api_performance.py` — benchmark runner, SLA checker
- Write `test_api_performance.py` — 10+ performance test cases

## Phase 3: Security Middleware
Harden the FastAPI application.
- Create `middleware/security_headers.py`
- Create `middleware/rate_limit.py`
- Create `middleware/input_sanitizer.py`
- Integrate into `main.py`

## Phase 4: Reality Check
Production readiness audit.
- Write `reality_check.py` — evidence-based certification
- Run full audit against the hardened endpoints

## Phase 5: Documentation
Update project .md files.
- Update `STATUS.md` — add Phase 9
- Update `AGENTS.md` — add security middleware section
- Update `implementation-summary.md` — add Phase 9 section
