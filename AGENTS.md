# AGENTS.md — Smart Labor Cost Estimator (AI RAG System)

## Project identity
Offline-first, bilingual (Arabic/English) RAG system that estimates labor hours and cost from natural-language queries against historical POS data. RTL support is mandatory for Arabic.

## Tech stack (from PRD)
- **Frontend:** Next.js (landscape-optimized, desktop/tablet) with Fira Code + Fira Sans fonts
- **Backend:** Python FastAPI (RAG logic, query processing)
- **Vector DB:** ChromaDB (local, no cloud dependency)
- **Embedding:** Dual-mode — Gemini Embedding 2 (cloud, 384d) / paraphrase-multilingual-MiniLM-L12-v2 (local, 384d)
- **LLM:** Dual-mode — Gemini 3.1 Flash Lite (cloud, free tier, GA May 2026) / Gemma 4 E4B via llama-cpp (local)
- **PDF:** reportlab with embedded Noto Naskh Arabic font
- **Chat:** SSE streaming, JSON session persistence (`backend/data/chats/`)
- **International rates:** Embedded reference table in system prompt (GCC, European, Global)
- **Data ingestion:** Static CSV/XLSX import (no live sync in V1)
- **Deployment:** Docker Compose, Windows start.bat, manual setup — see `docs/deployment.md`

## Critical files
| File | Role |
|------|------|
| `تقرير اليد العاملة بالكامل.xlsx` | Source POS data — 2,565 records, 32 columns, single sheet `POS_ActualLaboursSalesAnalysis` |
| `backend/data/dictionary.json` | Persistent dictionary store — 106 Libyan Arabic→standard terms across 9 automotive categories, auto-seeded from DOCX on ingestion |
| `labor-bot.md` | Original PRD — note: scope described as "Hyundai trucks only" is **stale**; see real scope below |

## Real scope (from data analysis)
- **25 vehicle brands**: Hyundai CV (59%), Hyundai PV (12%), Toyota (12%), Kia (9%), VW, Nissan, Mercedes, BMW, Mitsubishi, Ford, Audi, Mazda, Chevrolet, etc.
- **95 unique models**: HD45 (615 records), HD65, HD72, H350, Corolla, سيراتو, LC 300, Mighty EX8, سنتافي, etc.
- **3 workshops**: ورشه نافطه (Diesel, 1519 records), ورشه بنزين (Gasoline, 726), ورشه سمكره وطلاء (Body & Paint, 319)
- **Single branch**: Jadedaluma Tajura
- **Date range**: Feb 2025 – May 2026
- **20 labor codes**: codes 2000–4000 mapping to job categories (not vehicle identifiers)

## POS data schema (column positions)
```
Col  3: Branch              Col 16: Account Code
Col  5: WIPNO               Col 17: Account Name
Col  6: Invoice Number      Col 19: Customer Name
Col  7: Invoice Type        Col 20: Franchise (brand)
Col  8: Invoice Date        Col 21: Model
Col  9: Code (labor code)   Col 22: Variant
Col 10: Description (Arabic) Col 23: Chassis
Col 11: QTY (labor hours)   Col 24: Reg Date
Col 12: Price (hourly rate) Col 25: Reg Number
Col 14: Discount %          Col 26: Department (workshop)
Col 15: Total               Col 30: Service Advisor
```

## Key conventions & gotchas
- **"Code" column is NOT vehicle code** — it maps to labor job categories (2000=inspection, 3000=specialty work, 4000=body/paint). The "Model" column drives embedding weighting.
- **Embedding isolation is the hardest constraint** — a Corolla brake job must not influence an HD45 brake job estimate. The vectorization strategy MUST weight Model heavily.
- **Libyan workshop slang** — descriptions use local dialect (e.g., "مسمار ميزان" = stabilizer link). The dictionary bridges slang to standard automotive categories.
- **Confidence intervals, not exact numbers** — AI outputs percentiles from historical data (e.g. "1.5–2.5 hours"), never a single number.
- **RTL is mandatory** — every UI component must support Arabic RTL layout. Use CSS logical properties, not left/right.
- **Workshop separation** — Diesel, Gasoline, and Body/Paint have different labor rates and patterns. The system should filter/group by department naturally.

## Document consistency rules
After every action that changes the codebase, update the relevant `.md` files:

| Trigger | Action |
|---------|--------|
| Task completed | Check `[x]` the task in `specs/001-labor-estimator/tasks.md` |
| Phase completed | Run `specs/001-labor-estimator/checklist.md` P0 items → mark all done → update phase to ✅ in `STATUS.md` → write `implementation-summary.md` |
| Scope or data schema changes | Update schema section in both `AGENTS.md` and `specs/001-labor-estimator/spec.md` |
| New dependency added | Update `requirements.txt` and note in `implementation-summary.md` |
| New file created outside `frontend/`/`backend/`/`scripts/` | Explain its purpose in `implementation-summary.md` |

**Post-implementation summary template** (write in `specs/001-labor-estimator/implementation-summary.md` after each phase):
```
## Phase X: [Name] — YYYY-MM-DD

### Files created/modified
- ...

### Decisions made
- ...

### Verification
- [ ] checklist.md P0 items passed
- [ ] STATUS.md phase marker updated
```

## Development workflow
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000   # must run from backend/ directory

# Frontend
cd frontend
npm install
npm run dev

# Data ingestion (one-time)
python scripts/ingest.py --input "../تقرير اليد العاملة بالكامل.xlsx"

# Env setup (copy template, fill in keys)
copy backend\.env.template backend\.env
```

## Prerequisites
- **llama-cpp** (for offline LLM): Gemma 4 E4B running via `llama-server` on port 8080
- **Gemini API key** (for online LLM/embeddings): get from aistudio.google.com, set `GEMINI_API_KEY` in `.env`

## Config: load_dotenv path
`backend/config.py` loads `.env` via an explicit path:
```python
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)
```
Do NOT change this to `load_dotenv()` without a path — CWD-dependent resolution causes the wrong `.env` or system env vars to leak in.

## Model names (verified May 2026)
| Layer | Cloud model ID | Local fallback |
|-------|---------------|----------------|
| Embedding | `gemini-embedding-2` | `paraphrase-multilingual-MiniLM-L12-v2` |
| LLM | `gemini-3.1-flash-lite` | `gemma-4-e4b-it` (llama-cpp) |

## API endpoints
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Status, mode, model info |
| `POST` | `/api/query` | RAG search: hits + confidence ranges |
| `GET/POST/PUT/DELETE` | `/api/dictionary` | Term CRUD |
| `GET/POST` | `/api/dictionary/pending` | Unknown terms inbox |
| `POST` | `/api/dictionary/pending/{id}/resolve` | Map term to category |
| `POST` | `/api/export/pdf` | Generate PDF report |
| `POST` | `/api/settings/mode` | Toggle cloud/local mode |
| `POST` | `/api/chat/send` | SSE streaming chat message |
| `GET` | `/api/chat/sessions` | List chat sessions |
| `GET/DELETE` | `/api/chat/sessions/{id}` | Get/delete session |

## Key frontend routes
| Route | Purpose |
|-------|---------|
| `/` | Search & query results |
| `/assistant` | AI chat with international comparison |
| `/dictionary` | Term CRUD table |
| `/pending` | Review inbox |
| `/settings` | Language + mode toggles + system info |

## QA layer (Phase 8)
- `backend/qa/` — RAG quality assurance modules (inspired by agency-agents Model QA Specialist + AI Engineer)
  - `calibration.py` — held-out date split, calibration error, bias detection
  - `drift.py` — PSI computation, monthly time-window analysis
  - `retrieval_metrics.py` — MRR, NDCG, precision@k against ChromaDB
  - `embedding_quality.py` — intra/inter-model cosine similarity, isolation validation
  - `pipeline_observability.py` — per-stage latency tracking
  - `test_calibration.py` — calibration and drift tests
  - `test_retrieval.py` — retrieval and embedding quality tests

## Security middleware (Phase 9)
- `backend/middleware/` — security hardening (inspired by agency-agents API Tester + Security Engineer)
  - `security_headers.py` — X-Content-Type-Options, X-Frame-Options, CSP, HSTS, Referrer-Policy
  - `rate_limit.py` — in-memory sliding window (30 req/min, 429 + Retry-After)
  - `input_sanitizer.py` — query length limits (2000 chars), body size limit (1MB)
- `backend/qa/api_security.py` — OWASP API Top 10 vulnerability scanner
- `backend/qa/api_performance.py` — SLA benchmark runner (p50/p95/p99)
- `backend/qa/reality_check.py` — production readiness audit (14-point checklist)
- `backend/qa/test_api_security.py` — 13 security test cases
- `backend/qa/test_api_performance.py` — 8 performance test cases

## Accessibility (Phase 10)
All frontend components are WCAG 2.2 AA hardened:
- All 7 form inputs have `aria-label`
- All 20+ decorative SVGs have `aria-hidden="true"`
- All expandable sections have `aria-expanded` + `aria-controls`
- Chat streaming area uses `role="log"` + `aria-live="polite"`
- Skip-to-content link in header
- `aria-current="page"` on active navigation
- `scope="col"` on table headers
- `role="radiogroup"` + `role="radio"` + `aria-checked` on toggle groups
- `focus-visible:ring-2` on all interactive elements
- `forced-colors: active` media query for high-contrast mode
- `prefers-reduced-motion` respected

## Embedding: Gemini Embedding 2 (Phase 12)
- **Primary**: Gemini Embedding 2 (cloud, 384d). Configure via `EMBEDDING_SOURCE=gemini` in `.env`.
- **Auto-detect**: Reads `embedding_model` from ChromaDB collection metadata. Falls back to local if corpus was embedded with MiniLM.
- **Migration path**: `python scripts/ingest.py --input "تقرير اليد العاملة بالكامل.xlsx" --input2 "اليد العاملة منذ فتح المركز.xlsx" --reset` re-embeds with Gemini. After migration, queries auto-switch to Gemini.
- **Local fallback**: `paraphrase-multilingual-MiniLM-L12-v2` used when Gemini unavailable or corpus in MiniLM space.

## Query cache (Phase 12)
- In-memory LRU cache (100 entries, 5-min TTL) in `services/query_service.py`
- Cache key: SHA-256 of `(query_text, n_results, department_filter)`
- Auto-invalidated on data re-ingest via `invalidate_cache()`

## Running tests
```bash
# Backend (all tests including qa/)
cd backend
venv\Scripts\python.exe -m pytest tests qa -v

# Backend (core only)
venv\Scripts\python.exe -m pytest tests -v

# Frontend lint
cd frontend
npm run lint
```

## Service layer (Phase 11)
- `backend/services/` — orchestrated pipeline architecture (inspired by agency-agents Agents Orchestrator + Backend Architect)
  - `orchestrator.py` — PipelineOrchestrator: 5-stage RAG pipeline with quality gates, state tracking, timing
  - `pipeline_stages.py` — typed stage dataclasses (Embed, Search, Compute, Explain, Generate)
  - `quality_gates.py` — per-stage validation checks (non-null, valid ranges, weight sums)
  - `query_service.py` — high-level query API wired through orchestrator
  - `chat_service.py` — chat streaming adapter
