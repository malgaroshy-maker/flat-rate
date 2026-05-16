# Tasks — Smart Labor Cost Estimator

> **Current phase:** 0 | **Last updated:** 2026-05-13 | **[STATUS.md](../../STATUS.md)**

## Phase 0: Scaffolding
- [x] **0.1** Git init + `.gitignore` (Node, Python, venv, ChromaDB, .env)
- [x] **0.2** Scaffold Next.js app in `frontend/` (TypeScript, App Router, Tailwind)
- [x] **0.3** Scaffold FastAPI app in `backend/` with `requirements.txt`
- [x] **0.4** Create `scripts/` directory with `ingest.py` placeholder
- [x] **0.5** Python venv + install deps (fastapi, uvicorn, chromadb, openpyxl, python-docx, sentence-transformers, google-genai, python-dotenv)
- [x] **0.6** Local LLM: llama-cpp server with `gemma-4-e4b-it` on port 8080 (user-provided)
- [x] **0.7** Create `.env.template` with model config vars (`GEMINI_API_KEY`, `GEMINI_MODEL`, `OLLAMA_MODEL`, `EMBEDDING_MODEL`)
- [x] **0.8** Create `backend/config.py`: ModelRouter with embedding+LLM backend selection + connectivity detection
- [x] **0.9** Verify: `npm run dev` + `uvicorn main:app` both start clean

## Phase 1: Data Pipeline
- [x] **1.1** XLSX parser: read all 32 columns, 2,565 rows, type-cast dates/floats
- [x] **1.2** DOCX parser: extract Italian→Arabic→English term mappings from the automotive dictionary
- [x] **1.3** Normalizer: map Arabic slang descriptions to standard categories using dictionary
- [x] **1.4** Chunker: group records by (Model, Labor Code) for embedding isolation
- [x] **1.5** Embedder: generate vectors with multilingual sentence-transformer model
- [x] **1.6** Store embeddings in ChromaDB with full metadata (Model, Franchise, Department, QTY, Price, Date)
- [x] **1.7** Validation: query "Corolla oil" → Corolla returns #1; "HD45 brake" → HD45 in top 3; no cross-contamination

## Phase 2: Backend API
- [x] **2.1** `POST /api/query` endpoint — RAG query with confidence intervals
- [x] **2.2** Outlier detection logic — flag records >2σ from mean per (Model, Code) group
- [x] **2.3** `GET/POST/PUT/DELETE /api/dictionary` — term CRUD
- [x] **2.4** `GET /api/dictionary/pending` — unknown terms inbox
- [x] **2.5** `POST /api/dictionary/pending/{id}/resolve` — map term to category
- [x] **2.6** Language detection middleware (Arabic vs English input)
- [x] **2.7** Workshop filter — query results include department context
- [x] **2.8** Embedding router: `embed()` dispatches to Gemini API (online) or sentence-transformers (offline)
- [x] **2.9** LLM router: `generate()` dispatches to Gemini 3.1 Flash Lite (online) or llama-cpp Gemma4 (offline)

## Phase 3: Frontend Core
- [x] **3.1** Layout shell: landscape-optimized, Arabic RTL + English LTR
- [x] **3.2** Query input component with submit + clear
- [x] **3.3** Results card: confidence interval display, min/max hours, estimated cost
- [x] **3.4** Outlier details panel: collapsible, shows anomalous records with dates
- [x] **3.5** Language context provider (UI language + response language, persisted to localStorage)
- [x] **3.6** API client layer with error handling and loading states
- [x] **3.7** Playwright smoke tests: 10 query patterns, verify RTL rendering

## Phase 4: Dictionary & Settings UI
- [x] **4.1** Settings page: UI language toggle, AI response language toggle
- [x] **4.2** Dictionary table: paginated, searchable, filterable
- [x] **4.3** Term add/edit/delete forms with validation
- [x] **4.4** Pending inbox page: list of unknown terms from queries
- [x] **4.5** Resolve workflow: select term → assign standard category → save
- [x] **4.6** Verify: add new slang term, re-query, confirm improved results

## Phase 5: PDF Export
- [x] **5.1** Server-side PDF generation endpoint (`POST /api/export/pdf`)
- [x] **5.2** PDF template: vehicle info, job list, estimate ranges, outlier notes
- [x] **5.3** Arabic font embedding for PDF (e.g., Noto Naskh Arabic)
- [x] **5.4** Frontend: "Export PDF" button with download trigger
- [x] **5.5** Verify: export 5 queries, check Arabic renders, open in Adobe Reader

## Phase 6: AI Assistant Chat
- [x] **6.1** `chat_store.py` — JSON-based session/message persistence
- [x] **6.2** `system_prompt.py` — full workshop context + Libyan slang + international reference table
- [x] **6.3** `chat_engine.py` — RAG search + dual-mode LLM streaming (SSE)
- [x] **6.4** `routers/chat.py` — `POST /api/chat/send` (streaming), `GET/DELETE /api/chat/sessions`
- [x] **6.5** Frontend: `/assistant` page with sidebar + chat panel
- [x] **6.6** Frontend: SSE streaming with token-by-token rendering
- [x] **6.7** International flat-rate comparison in system prompt
- [x] **6.8** Auto-named sessions + history persistence

## Phase 7: UI/UX Redesign (ui-ux-pro-max)
- [x] **7.1** Replace Geist fonts with Fira Code + Fira Sans (Google Fonts)
- [x] **7.2** Slate color palette: primary #0F172A, CTA #0369A1, bg #F8FAFC
- [x] **7.3** Navy header with Lucide SVG navigation icons
- [x] **7.4** Replace emoji icons (⚠ ×) with Lucide SVG (AlertTriangle, X, Search, Send, FileDown)
- [x] **7.5** Professional confidence green (#059669) with metric pulse animations
- [x] **7.6** cursor-pointer + transition-colors duration-200 on all interactive elements
- [x] **7.7** Slate cards with elevated shadows across all panels
- [x] **7.8** Sky CTA buttons throughout (sky-600/700 replacing blue-600)
