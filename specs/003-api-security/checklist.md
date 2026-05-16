# Validation Checklist — API Security & Performance

## P0 — Must pass before phase completion

### Security
- [x] All 13 security tests pass
- [x] Rate limiter blocks after 30 req/min per endpoint (verified via 429 response)
- [x] Security headers present on all responses (X-Content-Type-Options, X-Frame-Options, etc.)
- [x] SQL injection payloads rejected or safely handled (no 500s)
- [x] XSS payloads rejected in dictionary/chat inputs (no 500s)
- [x] Request body size limit enforced (Content-Length check)
- [x] Query text max 2000 characters enforced via middleware

### Performance
- [x] POST /api/query response < 200ms (median)
- [x] GET /api/health response < 50ms
- [x] POST /api/export/pdf response < 500ms
- [x] GET /api/dictionary response < 100ms
- [x] Concurrent query handling without crashes (0 failures at concurrency=5)

### Middleware
- [x] Security headers middleware active
- [x] Rate limit middleware active
- [x] Input sanitizer middleware active

## P1 — Should pass

- [x] Rate limit returns 429 with Retry-After header
- [x] CORS restricted to localhost:3000
- [x] Content-Type validated on POST endpoints (implied via FastAPI/Pydantic)
- [x] Path traversal in term IDs rejected (404, not 500)
- [x] Empty query text returned gracefully (200 with hits, no crash)

## P2 — Nice to have

- [x] Health endpoint returns correct structure
- [x] Error handling for nonexistent endpoints (404)
- [ ] Request ID header on all responses for tracing (configured but empty values)
- [ ] Input sanitizer logs rejected requests (not yet)
