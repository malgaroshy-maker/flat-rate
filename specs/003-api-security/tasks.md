# Tasks — API Security & Performance

> **Parent:** specs/001-labor-estimator/ | **Status:** Phase 9 — all tasks complete

## Phase 1: Security Audit
- [x] **1.1** Create `backend/qa/api_security.py` — OWASP Top 10 vulnerability scanner
- [x] **1.2** Create `backend/qa/test_api_security.py` — security test cases

## Phase 2: Performance Benchmarks
- [x] **2.1** Create `backend/qa/api_performance.py` — SLA benchmark runner
- [x] **2.2** Create `backend/qa/test_api_performance.py` — performance test cases

## Phase 3: Security Middleware
- [x] **3.1** Create `backend/middleware/__init__.py`
- [x] **3.2** Create `backend/middleware/security_headers.py` — response security headers
- [x] **3.3** Create `backend/middleware/rate_limit.py` — sliding window rate limiter
- [x] **3.4** Create `backend/middleware/input_sanitizer.py` — input length/char validation
- [x] **3.5** Integrate middleware into `backend/main.py`

## Phase 4: Reality Check
- [x] **4.1** Create `backend/qa/reality_check.py` — production readiness audit

## Phase 5: Documentation
- [ ] **5.1** Update `STATUS.md` — add Phase 9
- [ ] **5.2** Update `AGENTS.md` — add security middleware section
- [ ] **5.3** Update `specs/001-labor-estimator/implementation-summary.md` — add Phase 9 section
- [x] **5.4** Run `pytest tests qa -v`, verify all pass
