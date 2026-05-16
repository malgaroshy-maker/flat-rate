# Implementation Plan — Smart Labor Cost Estimator

## Phase 0: Project Scaffolding & Git Init
**Goal:** Runnable skeletons of all three tiers.

- [x] `git init` with `.gitignore` (Node, Python, ChromaDB, venv, .env)
- [x] `frontend/`: `npx create-next-app@latest` — TypeScript, App Router, Tailwind
- [x] `backend/`: FastAPI project with `requirements.txt` (fastapi, uvicorn, chromadb, openpyxl, python-docx, sentence-transformers, google-genai, python-dotenv, reportlab, arabic-reshaper, python-bidi)
- [x] `scripts/`: data ingestion and utility scripts
- [x] Python venv setup, `.env` for paths/config/model keys
- [x] llama-cpp with Gemma 4 E4B running on port 8080 (offline LLM)
- [x] `backend/config.py`: ModelRouter with connectivity detection + automatic fallback
- [x] Verify: `npm run dev` works, `uvicorn main:app` works

## Phase 1: Data Pipeline
**Goal:** Parse XLSX → normalize with dictionary → generate embeddings.

- [x] Parse `تقرير اليد العاملة بالكامل.xlsx` — extract all 2,565 records with typed fields
- [x] Parse `The Libyan Automotive Dictionary...docx` — build Italian→Arabic→English term map
- [x] Normalization layer: map Arabic slang descriptions to standardized automotive categories using the dictionary
- [x] Chunking strategy: group records by (Model, Labor Code, Description) for embedding
- [x] Embedding generation: use sentence-transformers multilingual model (e.g., `paraphrase-multilingual-MiniLM-L12-v2`)
- [x] Store embeddings in ChromaDB with metadata (Model, Franchise, Department, QTY stats)
- [x] Verify: query "HD45 brake inspection" returns HD45-related records, not Corolla

## Phase 2: Backend API
**Goal:** RAG query endpoint + dictionary management.

- [x] `POST /api/query` — accepts natural-language query, returns:
  - Top-k matching historical records
  - Confidence interval (percentile-based QTY range)
  - Outlier annotations flagged records
  - Source department (workshop) context
- [x] `GET/POST/PUT/DELETE /api/dictionary` — CRUD for term mappings
- [x] `GET /api/dictionary/pending` — unknown terms flagged during queries
- [x] `POST /api/dictionary/pending/{id}/resolve` — map an unknown term to a category
- [x] Language detection: recognize Arabic vs English input, set response language accordingly
- [x] ModelRouter embedding: Gemini Embedding 2 (online) vs local sentence-transformers (offline)
- [x] ModelRouter LLM: Gemini 3.1 Flash Lite (online) vs llama-cpp Gemma4 (offline)
- [x] Connectivity detection: auto-select mode on startup, graceful fallback
- [x] Verify: manually test RAG accuracy on 10 known job types across 3 workshops

## Phase 3: Frontend — Query Interface
**Goal:** Advisors can query and get estimates.

- [x] Landscape-optimized layout (fixed-width, centered, 1200px+)
- [x] Query input with Arabic/English toggle (independent UI language vs response language)
- [x] Results panel: confidence interval as primary output, collapsible "Details" section
- [x] Outlier display: highlighted anomalous records with hours/date
- [x] RTL support: `dir="rtl"` on Arabic, CSS logical properties throughout
- [x] Loading/skeleton states, error boundaries
- [x] Verify: Playwright smoke test on top 20 query patterns

## Phase 4: Frontend — Dictionary & Settings
**Goal:** Advisors manage terminology and preferences.

- [x] Settings page: UI language toggle, AI response language toggle
- [x] Dictionary CRUD: table view with add/edit/delete, search/filter
- [x] Pending Review Inbox: list of unknown terms with quick-map action
- [x] Term mapping workflow: select unknown term → choose standard category → confirm
- [x] Verify: add a new slang term, confirm it influences subsequent queries

## Phase 5: PDF Export
**Goal:** One-click advisor reference sheet.

- [x] "Export PDF" button on results page
- [x] Server-side PDF generation (Python reportlab)
- [x] PDF content: vehicle details, queried jobs, estimate ranges, costs, outlier notes
- [x] Basic internal formatting (not customer-facing invoice quality)
- [x] Verify: export 5 different queries, check Arabic text renders correctly

## Phase 6: AI Assistant Chat
**Goal:** Conversational AI with RAG access and international flat-rate comparison.

- [x] `POST /api/chat/send` — SSE streaming chat with RAG context
- [x] `GET /api/chat/sessions` — list past chat sessions
- [x] `GET /api/chat/sessions/{id}` — retrieve session with messages
- [x] `DELETE /api/chat/sessions/{id}` — delete a session
- [x] JSON file-based persistence (`backend/data/chats/`)
- [x] Auto-named sessions from first user message
- [x] `/assistant` page: sidebar + chat panel with token-by-token streaming
- [x] System prompt: full workshop context + Libyan slang + 26-category international reference table
- [x] Side-by-side comparison format: 📊 Local | 🌍 International | 📝 Recommendation
- [x] Dual-mode: cloud (Gemini 3.1 Flash Lite) + offline (llama-cpp Gemma 4)
- [x] Verify: streaming response, session persistence, international comparison format

## Phase 7: UI/UX Redesign
**Goal:** Professional slate-themed interface following ui-ux-pro-max design system.

- [x] Fira Code + Fira Sans fonts replacing Geist
- [x] Slate palette: primary #0F172A, CTA #0369A1, bg #F8FAFC
- [x] Navy header with Lucide SVG nav icons
- [x] Emerald confidence box with metric pulse animation
- [x] All emoji replaced with Lucide SVG (AlertTriangle, X, Send, Search, Plus, Trash)
- [x] cursor-pointer + transition-colors on all interactive elements
- [x] Rounded-xl cards with shadow-sm throughout
- [x] Verify: lint clean, 6 routes compiled

## Phase 6: V2+ (Future)
- [ ] Role-Based Access Control for multiple advisors
- [ ] Migration to PostgreSQL + pgvector (cloud sync, multi-branch)
- [ ] ERP integration (Odoo API — push estimates to work orders)
- [ ] Continuous data ingestion from POS system
