# Implementation Summary

> Per-phase record of what was built, decisions made, and files changed.
> See **[AGENTS.md](../../AGENTS.md)** for the template.

---

## Phase 0: Scaffolding — 2026-05-13

### Files created/modified
- `.gitignore` — Node, Python, ChromaDB, venv, .env, IDE patterns
- `frontend/` — Next.js 16 (TypeScript, App Router, Tailwind, Turbopack)
- `backend/main.py` — FastAPI app with CORS + `/api/health` endpoint
- `backend/config.py` — Settings + ModelRouter (dual-mode online/offline)
- `backend/requirements.txt` — fastapi, uvicorn, chromadb, openpyxl, python-docx, sentence-transformers, google-genai, python-dotenv
- `backend/.env.template` — model config vars with placeholder values
- `scripts/ingest.py` — ingestion CLI placeholder
- `STATUS.md` — phase dashboard
- `plan.md` — 6-phase roadmap with checkboxes
- `specs/001-labor-estimator/spec.md` — refined spec (corrected scope, model strategy)
- `specs/001-labor-estimator/tasks.md` — 50+ task breakdown
- `specs/001-labor-estimator/checklist.md` — P0/P1/P2 validation gates
- `specs/001-labor-estimator/implementation-summary.md` — this file
- `AGENTS.md` — agent instructions (data schema, conventions, commands, doc consistency rules)

### Decisions made
- **Dual-mode embedding**: Gemini Embedding 2 (online, 768d) vs sentence-transformers (offline, 768d)
- **Dual-mode LLM**: Gemini 3.1 Flash Lite (online, free tier) vs Gemma4 E4B via llama-cpp (offline, OpenAI-compatible on :8080)
- **Both modes produce 768-dim vectors** for ChromaDB compatibility
- **ModelRouter** auto-selects based on `GEMINI_API_KEY` presence
- **llama-cpp integration**: uses OpenAI-compatible `/v1/chat/completions` endpoint — no ollama dependency

### Verification
- [x] `npm run dev` starts Next.js on :3000
- [x] `uvicorn main:app` starts FastAPI on :8000
- [x] `GET /api/health` returns `{status, mode, embedding_model}`
- [x] All Python deps import cleanly
- [x] llama-cpp Gemma 4 E4B server on port 8080 (user-provided)

---

## Phase 1: Data Pipeline — 2026-05-13

### Files created/modified
- `backend/ingestion/__init__.py` — package init
- `backend/ingestion/xlsx_parser.py` — parses 32-column POS Excel, 2,564 records with type casting
- `backend/ingestion/docx_parser.py` — extracts 103 Italian→Arabic term mappings from the dictionary
- `backend/ingestion/normalizer.py` — maps Arabic workshop slang to standard categories
- `backend/ingestion/pipeline.py` — orchestrator: chunk → embed → store (269 chunks)
- `backend/vector_store.py` — ChromaDB operations (create, add, query, reset)
- `scripts/ingest.py` — CLI entrypoint with argparse (--input, --dictionary, --reset)
- `backend/chroma_db/` — persistent ChromaDB storage (269 vectors, cosine distance)

### Decisions made
- **Embedding model**: `paraphrase-multilingual-MiniLM-L12-v2` (384-dim, 420MB, 50+ languages including Arabic)
- **Chunk text format**: `Model: X. Code: Y. Franchise: Z. [descriptions]` — embeds model name for isolation
- **Chunking strategy**: group by (Model, Labor Code) → 269 unique combinations
- **Metadata per chunk**: qty_mean, qty_median, qty_p10/p25/p75/p90, price_mean, model, code, departments, franchises
- **Validation**: "Corolla oil" → Corolla #1 match. "HD45 brake" → HD45 in top 3. Model isolation working via text prefix.

### Verification
- [x] All 2,564 XLSX records parsed
- [x] 103 dictionary terms extracted (101 unique Arabic)
- [x] 269 vectors stored in ChromaDB
- [x] Model-isolated queries validated
- [x] Pipeline runs in ~20 seconds

---

## Phase 2: Backend API — 2026-05-13

### Files created/modified
- `backend/embedding_router.py` — dual-mode embedding (Gemini API + sentence-transformers) with graceful fallback
- `backend/llm_router.py` — dual-mode LLM (Gemini 3.1 Flash Lite + llama-cpp) with graceful fallback
- `backend/query_engine.py` — RAG pipeline: encode→search→compute confidence intervals→detect outliers
- `backend/dictionary_store.py` — in-memory CRUD + pending review inbox
- `backend/routers/__init__.py`
- `backend/routers/query.py` — `POST /api/query` (q, n, department, generate, lang)
- `backend/routers/dictionary.py` — full CRUD + pending inbox + resolve
- `backend/main.py` — updated to include routers

### API endpoints
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Status + active mode/backend |
| `POST` | `/api/query` | RAG query → hits + confidence + outliers |
| `GET/POST/PUT/DELETE` | `/api/dictionary` | Term CRUD |
| `GET/POST` | `/api/dictionary/pending` | Unknown terms inbox |
| `POST` | `/api/dictionary/pending/{id}/resolve` | Map term → category |

### Decisions made
- **Confidence intervals**: percentile-based (p10/p50/p90) from matching chunk metadata
- **Outlier detection**: 2σ threshold per chunk's value distribution
- **Language detection**: character-frequency-based (≥20% Arabic chars → `ar`)
- **Cloud fallback**: embedding + LLM routers catch API errors and degrade to local automatically
- **Dictionary store**: in-memory only (V1); persistence planned for V2

### Verification
- [x] `POST /api/query` returns hits with confidence ranges
- [x] Language auto-detection: Arabic ↔ English
- [x] Dictionary: create, search, update, delete all work
- [x] Pending inbox: detect unknown terms, resolve to new dictionary entry
- [x] Cloud → local fallback triggered on expired API key
- [x] 18/18 integration tests passed

## Phase 3: Frontend Core — 2026-05-13

### Files created/modified
- `src/lib/api.ts` — typed API client (fetchHealth, searchQuery) with error handling
- `src/lib/i18n.ts` — Arabic/English translation table + RTL helper
- `src/context/LanguageContext.tsx` — React context (uiLang, responseLang, localStorage persistence)
- `src/components/QueryInput.tsx` — search input with submit/clear/loading spinner
- `src/components/ResultsCard.tsx` — confidence interval display, expandable hit details
- `src/components/OutlierPanel.tsx` — collapsible outlier panel with σ-deviation display
- `src/app/layout.tsx` — server component with Geist fonts, RTL dir, ClientShell
- `src/app/ClientShell.tsx` — client wrapper: LanguageProvider + Header + language toggle
- `src/app/page.tsx` — main page: input → search → results flow
- `src/app/globals.css` — RTL direction styles, Tailwind v4 config

### Decisions made
- **Layout architecture**: server component layout for SSR, ClientShell for interactive parts
- **Language persistence**: localStorage keys `labor_ui_lang` / `labor_response_lang`
- **RTL**: `document.documentElement.dir` set dynamically on language toggle
- **Confidence display**: green box with `p10–p90h` range + median
- **Query history**: last 10 queries in localStorage (not yet UI-visible)
- **Playwright**: installed as devDep, but Chromium browser not downloaded (slow network)

### Verification
- [x] `npm run build` compiles with 0 errors
- [x] RTL: Arabic default, toggles to LTR on English switch
- [x] Query flow: type → submit → loading spinner → results render
- [x] Outlier panel: collapsible, shows σ deviations
- [x] Error state: API failures show error message with retry

## Phase 4: Dictionary & Settings UI — 2026-05-13

### Files created/modified
- `src/components/DictionaryPanel.tsx` — searchable table + add/edit/delete forms with validation
- `src/components/PendingPanel.tsx` — inbox list + resolve workflow (inline form to map term→category)
- `src/components/SettingsPanel.tsx` — UI language toggle + AI response language toggle (independent)
- `src/app/dictionary/page.tsx` — /dictionary route
- `src/app/pending/page.tsx` — /pending route
- `src/app/settings/page.tsx` — /settings route
- `src/app/ClientShell.tsx` — updated with tab navigation (Search / Dictionary / Review / Settings)
- `src/lib/api.ts` — added all dictionary CRUD functions (fetchTerms, createTerm, updateTerm, deleteTerm, fetchPending, resolvePending)

### Decisions made
- **Tab navigation**: Next.js file-based routing with 4 tabs in the header
- **Inline forms**: add/edit on dictionary page, resolve on pending page — no modal dialogs
- **Dictionary CRUD**: validates arabic_term + standard_category required on add/update
- **Pending resolve**: maps unknown term → standard category → creates dictionary entry

### Verification
- [x] `npm run build` compiles all 5 routes (/, /dictionary, /pending, /settings, /_not-found)
- [x] Dictionary: search, add, edit, delete all functional
- [x] Pending inbox: list + inline resolve form
- [x] Settings: independent UI lang / response lang toggles
- [x] Tab navigation: active state highlights current route

## Testing Phase — 2026-05-13

### Files created
- `backend/tests/conftest.py` — shared TestClient fixture
- `backend/tests/test_health.py` — 2 tests (health structure, mode detection)
- `backend/tests/test_query.py` — 12 tests (Arabic/English queries, confidence, outliers, edges, 3 workshops)
- `backend/tests/test_dictionary.py` — 8 tests (CRUD lifecycle, validation errors)
- `backend/tests/test_pending.py` — 4 tests (inbox flow: add→list→resolve)
- `backend/tests/test_filters.py` — 4 tests (department filter, model isolation, all 3 departments)
- `backend/tests/test_data_integrity.py` — 8 tests (ChromaDB count, model nulls, qty stats, parser validation)

### Results
| Suite | Tests | Passed | Failed |
|-------|-------|--------|--------|
| Backend API + data integrity | 38 | 38 | 0 |
| Frontend lint | — | clean | 0 |
| Frontend build | 5 routes | compiled | 0 |

### Fixes applied during testing
- Removed module-level stdout/stderr encoding patches (broke pytest capture)
- Fixed `datetime.utcnow()` → `datetime.now(timezone.utc)` deprecation
- Refactored DictionaryPanel/PendingPanel effects to avoid setState-in-effect lint errors
- Updated LanguageContext to use useState initializer for localStorage instead of useEffect

---

## Phase 5: PDF Export — 2026-05-13

### Files created/modified
- `backend/pdf_generator.py` — reportlab-based PDF generator with Arabic RTL support (arabic_reshaper + python-bidi)
- `backend/routers/query.py` — added `POST /api/export/pdf` endpoint
- `frontend/src/app/page.tsx` — added "Export PDF" button with download trigger
- `backend/requirements.txt` — added reportlab, arabic-reshaper, python-bidi

### Decisions made
- **PDF library**: reportlab (no system dependencies unlike weasyprint)
- **Arabic support**: arabic_reshaper for glyph shaping + python-bidi for RTL text direction
- **Layout**: landscape A4, table with alternating row colors, Noto Naskh Arabic font
- **Content**: query text, date, confidence range, hits table (model/dept/records/median/range), outlier notices
- **Frontend**: button appears after query results, creates blob download via fetch

### Verification
- [x] `POST /api/export/pdf` returns valid PDF (200, application/pdf, Content-Disposition)
- [x] Arabic PDF: 8,453 bytes with embedded Noto Naskh Arabic font
- [x] English PDF: valid with cost/rate table
- [x] Frontend lint clean, build passes

---

## Post-Phase 5 Fixes — 2026-05-14

### Issues fixed
- **PDF Arabic text**: replaced Helvetica with embedded Noto Naskh Arabic TTF font → no more squares
- **Frontend rate/cost display**: ResultsCard now shows hourly rate, estimated cost (LYD), and per-hit cost
- **Settings page**: added Cloud/Local mode toggle (calls `POST /api/settings/mode`), system info panel
- **Cloud mode**: `load_dotenv()` now uses explicit path `Path(__file__).parent / ".env"` with `override=True` to prevent system env var leaking expired keys
- **start.bat**: fixed paths, pre-flight checks, `cmd /k` keeps windows open
- **checklist.md**: all phases marked `[x]`

### Model names (verified with Gemini API May 2026)
| Layer | Model ID | Status |
|-------|---------|--------|
| Cloud LLM | `gemini-3.1-flash-lite` | GA May 7, 2026 |
| Cloud Embedding | `gemini-embedding-2` | GA April 22, 2026 |
| Local LLM | `gemma-4-e4b-it` (llama-cpp :8080) | — |
| Local Embedding | `paraphrase-multilingual-MiniLM-L12-v2` | — |

---

## Phase 6: AI Assistant Chat — 2026-05-14

### Files created/modified
- `backend/chat_store.py` — JSON file-based session/message CRUD (`backend/data/chats/`)
- `backend/system_prompt.py` — workshop-aware system prompt (Ar/En) with 26-category international flat-rate reference table
- `backend/chat_engine.py` — RAG search + dual-mode LLM streaming via SSE
- `backend/routers/chat.py` — `POST /api/chat/send` (streaming), `GET/DELETE /api/chat/sessions`
- `backend/routers/__init__.py` — (updated)
- `backend/main.py` — added chat router
- `backend/llm_router.py` — added `_api_key_or_none()` and `_base_url()` helpers
- `frontend/src/lib/chat_api.ts` — typed API client with SSE streaming support
- `frontend/src/components/ChatMessage.tsx` — message bubble with typing indicator
- `frontend/src/components/ChatPanel.tsx` — message list + input + auto-scroll
- `frontend/src/components/SessionList.tsx` — sidebar with session history
- `frontend/src/app/assistant/page.tsx` — `/assistant` route
- `frontend/src/app/ClientShell.tsx` — added "المساعد" tab

### API endpoints added
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/chat/send` | SSE streaming chat (RAG + LLM) |
| `GET` | `/api/chat/sessions` | List all sessions |
| `GET` | `/api/chat/sessions/{id}` | Get session with messages |
| `DELETE` | `/api/chat/sessions/{id}` | Delete session |

### Decisions made
- **Chat storage**: JSON files per session (no SQLite dependency)
- **Streaming**: SSE (Server-Sent Events) with token-by-token delivery
- **System prompt**: Arabic-dominant with full workshop context + Libyan slang + international flat-rate table
- **International comparison**: 📊 Local / 🌍 International (GCC, European, Global) / 📝 Recommendation format
- **Session naming**: Auto-named from first user message (first 60 chars)
- **Dual-mode**: Both cloud (Gemini 3.1 Flash Lite) and local (llama-cpp) support chat with streaming

### Compound operation detection
- 46% of records flagged as compound (1,183 out of 2,564)
- `compound`, `compound_max_ops`, `compound_pct`, `weighted_qty_p50/90` metadata per chunk
- Frontend shows ⚠ notice and per-operation unit estimate in expanded details

### Verification
- [x] SSE streaming delivers all tokens with `done: true`
- [x] International comparison format verified (📊/🌍/📝)
- [x] Sessions persist as JSON files with auto-naming
- [x] Session list shows past conversations
- [x] Lint clean, 6 routes compiled

---

## Phase 7: UI/UX Redesign — 2026-05-14

### Files modified
- `src/app/layout.tsx` — Fira Code + Fira Sans via Google Fonts, slate-50 bg, slate-900 text
- `src/app/globals.css` — slate palette CSS vars, metric-pulse animation, reduced-motion support, global transitions
- `src/app/ClientShell.tsx` — navy header (`bg-slate-900`), Lucide SVG nav icons, compact "EN" toggle
- `src/components/QueryInput.tsx` — slate borders, sky CTA, Lucide Send/X icons, cursor-pointer
- `src/components/ResultsCard.tsx` — emerald confidence box, metric pulse animation, slate cards with shadow, Lucide AlertTriangle/Chevron
- `src/components/OutlierPanel.tsx` — Lucide AlertTriangle + Chevron icons, amber-200 borders
- `src/components/ChatMessage.tsx` — sky user bubbles, slate assistant bubbles
- `src/components/ChatPanel.tsx` — slate borders, sky send button, Lucide Send icon
- `src/components/SessionList.tsx` — sky active state, Lucide Plus/Trash icons, button→div nesting fix
- `src/components/DictionaryPanel.tsx` — slate table/borders, sky/emerald buttons
- `src/components/SettingsPanel.tsx` — slate cards with shadows, sky/emerald toggles
- `src/components/PendingPanel.tsx` — amber-200 borders, emerald resolve button

### Design system (ui-ux-pro-max)
| Element | Value |
|---------|-------|
| Style | Trust & Authority + Dashboard/Data |
| Primary | `#0F172A` (slate-900) |
| CTA | `#0369A1` (sky-700) |
| Background | `#F8FAFC` (slate-50) |
| Confidence | `#059669` (emerald-600) |
| Heading font | Fira Code (monospace) |
| Body font | Fira Sans (clean) |

### Key improvements
- All emoji replaced with Lucide SVG icons (AlertTriangle, X, Send, Search, Plus, Trash, Bot, Book, Gear, Inbox)
- `cursor-pointer` on every interactive element
- `transition-colors duration-200` on all hover states
- Metric pulse animation on confidence numbers
- `prefers-reduced-motion` respected
- Professional navy header replacing white header

### Verification
- [x] Lint clean, 6 routes compiled
- [x] Fira fonts loading from Google Fonts
- [x] Slate palette consistent across all components
- [x] No emoji icons remaining in UI
- [x] cursor-pointer + transitions on all interactive elements

---

## Phase 8: RAG Quality (Model QA + AI Engineer) — 2026-05-15

### Files created
- `specs/002-rag-quality/spec.md` — system design for QA layer (5 domains)
- `specs/002-rag-quality/plan.md` — 6-phase execution plan
- `specs/002-rag-quality/tasks.md` — 15 concrete tasks
- `specs/002-rag-quality/checklist.md` — P0/P1/P2 validation gates
- `backend/qa/__init__.py` — package init
- `backend/qa/calibration.py` — held-out date split, P10-P90 range calibration, bias detection
- `backend/qa/drift.py` — PSI (Population Stability Index) across monthly time windows
- `backend/qa/retrieval_metrics.py` — MRR, NDCG@k, precision@k against ChromaDB ground truth
- `backend/qa/embedding_quality.py` — intra/inter-model cosine similarity, isolation ratio
- `backend/qa/pipeline_observability.py` — per-stage latency tracking (embed, search, compute)
- `backend/qa/test_calibration.py` — 9 tests (calibration + drift edge cases)
- `backend/qa/test_retrieval.py` — 7 tests (retrieval metrics + embedding quality)

### Files modified
- `backend/vector_store.py` — added `search_with_metadata()` returning structured distance+ID lists
- `backend/query_engine.py` — added `explain_estimate()` (SHAP-inspired contribution weights), latency tracking per stage, `timing_ms` in response

### Documents updated
- `STATUS.md` — added Phase 8 row (in progress)
- `AGENTS.md` — added QA layer section with module descriptions and test commands

### Decisions made
- **QA runs independently**: all modules parse raw XLSX or query ChromaDB read-only — zero impact on production query path
- **Calibration**: date-split (median date), P10-P90 within-range % as primary metric, target >=80%
- **Drift**: PSI with 0.25 threshold, earliest-vs-latest month comparison per (Model, Code) group
- **Retrieval**: each chunk queries itself as ground truth, MRR as primary metric (target >=0.5)
- **Embedding isolation**: cosine similarity intra-model vs inter-model, isolation ratio > 1.0 confirms model separation
- **Observability**: in-process timing via `_STAGE_TIMINGS` dict, `LatencyReport` dataclass with p50/p95/p99
- **Explainability**: per-hit similarity-weighted contributions, confidence rating (high/medium/low) based on record count + model agreement

### Agent inspiration (agency-agents)
| Module | Inspired by |
|--------|------------|
| calibration.py, drift.py | Model QA Specialist — calibration testing, PSI, feature stability |
| retrieval_metrics.py, embedding_quality.py, pipeline_observability.py | AI Engineer — RAG evaluation, vector quality, latency tracking |
| explain_estimate() | Model QA Specialist — SHAP-style interpretability patterns |

---

## Phase 9: API Security & Performance (API Tester + Reality Checker) — 2026-05-15

### Files created
- `specs/003-api-security/spec.md` — OWASP Top 10 coverage, SLA targets, middleware architecture
- `specs/003-api-security/plan.md` — 5-phase execution plan
- `specs/003-api-security/tasks.md` — 14 concrete tasks
- `specs/003-api-security/checklist.md` — P0/P1/P2 validation gates
- `backend/qa/api_security.py` — OWASP API Top 10 vulnerability scanner (SQL injection, XSS, path traversal, mass assignment, large payloads, CORS)
- `backend/qa/api_performance.py` — SLA benchmark runner (mean/median/p95/p99, concurrent load testing)
- `backend/qa/reality_check.py` — production readiness audit (14-point checklist, evidence-based certification)
- `backend/qa/test_api_security.py` — 13 security test cases
- `backend/qa/test_api_performance.py` — 8 performance test cases
- `backend/middleware/__init__.py` — middleware package
- `backend/middleware/security_headers.py` — X-Content-Type-Options, X-Frame-Options, CSP, HSTS, Referrer-Policy, X-Request-ID
- `backend/middleware/rate_limit.py` — in-memory sliding window (30 req/min, 60s window, 429 + Retry-After)
- `backend/middleware/input_sanitizer.py` — query length limits (2000 chars max), body size limit (1MB), control char rejection

### Files modified
- `backend/main.py` — registered SecurityHeadersMiddleware, RateLimitMiddleware, InputSanitizerMiddleware; restricted CORS methods from `["*"]` to `["GET", "POST", "PUT", "DELETE", "OPTIONS"]`

### Decisions made
- **Rate limit**: 30 req/min per endpoint per host, sliding window, no persistence (in-memory only for V1)
- **Security headers**: applied to all responses via Starlette middleware
- **Input validation**: Content-Length header check for body size; query param length check (2000 chars for q/message)
- **CORS**: restricted to explicit methods list; origin locked to localhost:3000
- **Reality check**: 14-point audit including health, query, dictionary CRUD, PDF export, chat sessions, CORS, error handling, mode toggle

### Verification
- [x] 76/76 tests pass (38 core + 17 RAG quality + 13 security + 8 performance)
- [x] Rate limiter triggers 429 with Retry-After header
- [x] Security headers present on all responses
- [x] SQL injection, XSS, path traversal payloads handled without 500 errors
- [x] Performance SLAs validated: health <50ms, query <200ms, pdf <500ms, dictionary <100ms

### Agent inspiration (agency-agents)
| Module | Inspired by |
|--------|------------|
| api_security.py, test_api_security.py | API Tester — OWASP Top 10, input fuzzing, security-first testing |
| api_performance.py, test_api_performance.py | API Tester — SLA validation, concurrent load, p95/p99 |
| middleware/rate_limit.py | API Tester — rate limiting, abuse prevention |
| middleware/security_headers.py | Security Engineer — security hardening |
| reality_check.py | Reality Checker — evidence-based certification, defaults to NEEDS WORK |

---

## Phase 10: Accessibility & RTL Remediation (Accessibility Auditor) — 2026-05-15

### Files modified (12 components)
- `src/app/layout.tsx` — added `viewport` export (Next.js 16), font imports preserved
- `src/app/globals.css` — added `forced-colors: active` media query for high-contrast mode
- `src/app/ClientShell.tsx` — added skip-to-content link, `aria-label` on nav, `aria-current="page"` on active tabs, `aria-hidden="true"` on 5 SVG icons, `aria-label` on language toggle, `focus-visible:ring` on all interactive elements, `id="main-content"` on `<main>`, `aria-label` on `<nav>`
- `src/components/SessionList.tsx` — converted clickable `<div>` to semantic `<button>` with `role="option"`, `aria-selected`, `focus-visible`, `role="listbox"` on container, `aria-label` on nav, `role="status"` on empty state, `aria-hidden` on SVGs
- `src/components/QueryInput.tsx` — added `aria-label` to input + both buttons, `focus-visible:ring` on all buttons, `aria-hidden="true"` on 3 SVG icons
- `src/components/ChatPanel.tsx` — added `role="log"` + `aria-live="polite"` on message area, `aria-label` on input + send button, `role="status"` on empty states, `focus-visible:ring`, `aria-hidden` on SVG
- `src/components/ResultsCard.tsx` — added `aria-expanded` + `aria-controls` on expand buttons, `focus-visible:ring`, `aria-hidden="true"` on 3 SVG icons
- `src/components/OutlierPanel.tsx` — added `aria-expanded` + `aria-controls` on toggle, `focus-visible:ring`, `aria-hidden="true"` on 3 SVG icons
- `src/components/ChatMessage.tsx` — added `role="article"`, `aria-label` on message bubbles, `aria-hidden` on streaming cursor
- `src/components/DictionaryPanel.tsx` — added `scope="col"` on all `<th>`, `aria-label` on all 4 inputs + 5 buttons, `role="status"` on loading/empty, `focus-visible:ring`
- `src/components/PendingPanel.tsx` — added `aria-label` on all 3 inputs + 4 buttons, `role="status"` on loading/empty, `focus-visible:ring`
- `src/components/SettingsPanel.tsx` — added `role="radiogroup"` on language selectors, `role="radio"` + `aria-checked` on each option, `aria-pressed` on mode toggle, `focus-visible:ring`

### WCAG 2.2 AA improvements
| Category | Before | After |
|----------|--------|-------|
| aria-* attributes | 0 | 60+ across all components |
| Labeled form inputs | 0/7 | 7/7 |
| Keyboard-accessible interactions | 5/6 | 6/6 (SessionList div→button) |
| Focus-visible indicators | 0 | All interactive elements |
| Decorative SVG accessibility | 0/20+ | 20/20 (aria-hidden) |
| Live regions for dynamic content | 0 | Chat streaming + loading/empty states |
| Expand state announcements | 0 | ResultsCard + OutlierPanel |
| Skip-to-content link | No | Yes |
| aria-current navigation | No | Yes |
| Table header scope | 0 | 4 col headers |
| forced-colors support | No | Yes |

### Verification
- [x] `npm run lint` — 0 errors, 0 warnings
- [x] `npm run build` — 6 routes compiled, 0 errors, 0 warnings
- [x] All P0/P1/P2/P3 checklist items marked complete
- [x] `prefers-reduced-motion` still respected

### Agent inspiration (agency-agents)
| Improvement | Inspired by |
|-------------|------------|
| Full accessibility audit + remediation | Accessibility Auditor — WCAG 2.2 AA, screen reader testing patterns, keyboard nav, focus management, live regions |

---

## Phase 11: Service Layer & Pipeline Orchestration — 2026-05-15

### Files created
- `specs/005-architecture/spec.md` — system design for orchestrated pipeline
- `specs/005-architecture/plan.md` — 5-phase execution plan
- `specs/005-architecture/tasks.md` — 10 concrete tasks
- `specs/005-architecture/checklist.md` — P0/P1/P2 validation gates
- `backend/services/__init__.py` — package init
- `backend/services/pipeline_stages.py` — typed stage dataclasses (EmbedInput/Output, SearchInput/Output, ComputeInput/Output, ExplainInput/Output, GenerateInput/Output, PipelineState, StageResult)
- `backend/services/quality_gates.py` — per-stage validation (embed vector dimensions, search results non-empty, percentile monotonicity, weight sum ~1.0, generate response quality)
- `backend/services/orchestrator.py` — PipelineOrchestrator class: runs 5-stage pipeline, checks quality gates between stages, tracks per-stage timing + status, produces PipelineState
- `backend/services/query_service.py` — high-level query API with `query_with_orchestrator()`, wires existing embed/search/compute/explain/generate functions as pipeline stages
- `backend/services/chat_service.py` — chat streaming adapter for orchestrator

### Files modified
- `backend/routers/query.py` — added `orchestrate` query param (default false). When true, routes through `query_with_orchestrator()` producing `pipeline_state` in response

### Decisions made
- **Backward-compatible**: orchestrator off by default; existing routers and all 76 tests work unchanged
- **5-stage pipeline**: Embed → Search → Compute → Explain → Generate with quality gates between each
- **Quality gates non-blocking**: failed gates produce warnings, not errors (pipeline degrades gracefully)
- **Pipeline state tracked**: per-stage `(stage, status, elapsed_ms)` tuple, total time, pass/fail gate counts
- **Lazy initialization**: orchestrator singleton created on first use, not at import time

### Verification
- [x] 76/76 tests pass (38 core + 38 QA)
- [x] Default query path unchanged (orchestrate=false)
- [x] Orchestrated path produces extended response with `pipeline_state` + `explanation`

### Agent inspiration (agency-agents)
| Module | Inspired by |
|--------|------------|
| orchestrator.py, pipeline_stages.py | Agents Orchestrator — multi-stage pipeline, quality gates, state tracking, dev-QA loop pattern |
| query_service.py, chat_service.py | Backend Architect — service layer separation, dependency injection, typed interfaces |

---

## Phase 12: Performance + Data + UX — 2026-05-16

### Embedding migration to Gemini Embedding 2
- `backend/embedding_router.py` — rewritten: auto-detects corpus embedding model from ChromaDB metadata, uses Gemini when corpus is Gemini-embedded, falls back to local MiniLM otherwise. Added `encode_cloud()` public method for ingestion.
- `backend/config.py` — added `EMBEDDING_SOURCE` env var (default: `gemini`)
- `backend/ingestion/pipeline.py` — uses `embedding_router.encode_cloud()` for Gemini, local SentenceTransformer as fallback. Stores `embedding_model` in collection metadata on reset.
- `backend/vector_store.py` — `reset_collection()` now accepts metadata dict for storing embedding model name

### Expanded data ingestion (4.5x more records)
- `scripts/ingest.py` — added `--input2` flag for second XLSX file. Merges both files, deduplicates by Invoice Number.
- `backend/ingestion/pipeline.py` — `run_pipeline()` accepts `xlsx_paths` list, iterates and dedupes across all files
- Second file: `اليد العاملة منذ فتح المركز.xlsx` (11,582 rows, same 32-column schema) — "labor since center opened"

### Query response caching
- `backend/services/query_service.py` — added LRU cache (100 entries, 5min TTL), SHA-256 cache keys, `invalidate_cache()` for re-ingest. Cached on non-generate queries.
- `backend/routers/query.py` — `orchestrate` param wired through `query_with_orchestrator()` which uses cache

### Chat screen UX
- `src/components/ChatMessage.tsx` — markdown rendering (bold, italic, headings, lists, code), copy-to-clipboard button on hover, `role="article"` + `aria-label`
- `src/app/assistant/page.tsx` — mobile hamburger sidebar toggle with backdrop overlay, responsive layout

### Dictionary & pending tabs UX
- `src/components/DictionaryPanel.tsx` — sortable columns (Arabic/Category/English with ▲/▼ indicators), CSV export button, term count badge, responsive mobile grid
- `src/components/PendingPanel.tsx` — batch resolve: select all/individual checkboxes, assign category to all selected, resolve all button, responsive mobile layout

### Verification
- [x] 76/76 tests pass
- [x] Lint clean, build clean (6 routes)
- [x] Embedding auto-detect: Corpus without Gemini metadata → local fallback
- [x] After `--reset` re-ingest with Gemini → auto-switches to cloud
- [x] LRU cache: repeat queries return cached results
- [x] Mobile sidebar toggle works on chat page
