# Spec: Smart Labor Cost Estimator (AI RAG System)

> Refined from `labor-bot.md` PRD with actual data analysis corrections.

## 1. Product Overview
**Objective:** An offline-first, bilingual AI system that uses historical POS labor data and Retrieval-Augmented Generation (RAG) to give service advisors accurate, consistent, context-aware labor hour and cost estimates.

**Target users:** Internal service advisors at Jadedaluma Tajura (single-branch, single-user for V1).

**Real scope** (corrected from PRD):
- **25 vehicle brands** across 95 models — not limited to Hyundai trucks
- **3 workshops**: Diesel (ورشه نافطه), Gasoline (ورشه بنزين), Body & Paint (ورشه سمكره وطلاء)
- **2,565 historical records** (Feb 2025 – May 2026) across 20 labor codes

## 2. Architecture & Tech Stack
| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Next.js (TypeScript, App Router, Tailwind) | Landscape-optimized, RTL-capable, offline-friendly |
| Backend | Python FastAPI | RAG orchestration, dictionary management, PDF generation |
| Vector DB | ChromaDB (local) | No cloud dependency, fast local similarity search |
| Embeddings | Gemini Embedding 2 (online) / sentence-transformers (offline) | 768-dim unified vector space |
| LLM | Gemini 3.1 Flash Lite (online, free tier) / Gemma4 via llama-cpp (offline) | Dual-mode with auto-fallback |
| PDF | reportlab or weasyprint | Server-side generation with Arabic text support |

## 3. Data Schema (from `تقرير اليد العاملة بالكامل.xlsx`)

### Source columns
| Col | Field | Type | Notes |
|-----|-------|------|-------|
| 3 | Branch | string | Always "Jadedaluma Tajura" |
| 5 | WIPNO | string | Work-in-progress number |
| 6 | Invoice Number | string | |
| 7 | Invoice Type | string | "I" = invoice |
| 8 | Invoice Date | date | DD-MM-YYYY |
| 9 | Code | string | Labor code (2000–4000) |
| 10 | Description | string (Arabic) | Libyan workshop slang |
| 11 | QTY | float | Labor hours |
| 12 | Price | float | Hourly rate |
| 14 | Discount % | float | |
| 15 | Total | float | QTY × Price × (1 - Discount) |
| 16 | Account Code | string | |
| 17 | Account Name | string | |
| 19 | Customer Name | string | |
| 20 | Franchise | string | Vehicle brand (25 unique) |
| 21 | Model | string | Vehicle model (95 unique) |
| 22 | Variant | string | |
| 23 | Chassis | string | |
| 24 | Reg Date | date | Vehicle registration date |
| 25 | Reg Number | string | |
| 26 | Department | string | Workshop: نافطه / بنزين / سمكره وطلاء |
| 30 | Service Advisor | string | |

### Workshop distribution
| Department | Records | Arabic |
|------------|---------|--------|
| Diesel | 1,519 | ورشه نافطه |
| Gasoline | 726 | ورشه بنزين |
| Body & Paint | 319 | ورشه سمكره وطلاء |

### Brand distribution (top 10)
| Brand | Records | % |
|-------|---------|---|
| Hyundai CV | 1,522 | 59.4% |
| Hyundai PV | 311 | 12.1% |
| Toyota | 303 | 11.8% |
| Kia | 228 | 8.9% |
| Volkswagen | 51 | 2.0% |
| Nissan | 27 | 1.1% |
| Mercedes Benz | 23 | 0.9% |
| Mitsubishi | 21 | 0.8% |
| BMW | 13 | 0.5% |
| Other (15 brands) | 65 | 2.5% |

## 4. Features

### 4.1 Localization
- UI language: toggleable Arabic ↔ English
- AI response language: independent toggle (set output language regardless of UI)
- Full RTL support for Arabic (CSS logical properties, `dir` attribute)

### 4.2 Smart Query Engine
- Natural language input with Libyan slang understanding
- Confidence intervals from historical percentiles (not single numbers)
- Outlier transparency: collapsible details showing anomalous records

### 4.3 Hybrid Dictionary Management
- **Proactive**: CRUD interface for term mappings (Libyan slang → standard category)
- **Reactive**: Pending review inbox for unknown terms encountered during queries
- Base dictionary sourced from `The Libyan Automotive Dictionary...docx`

### 4.4 PDF Export
- One-click internal reference sheet
- Contains: vehicle details, queried jobs, estimate ranges, costs, outlier notes
- Not customer-facing — internal advisor reference only

### 4.5 AI Assistant Chat (المساعد)
- Conversational interface with full RAG access to historical data
- SSE streaming responses (token-by-token)
- Multi-session with persistent history (JSON files in `backend/data/chats/`)
- Dual-mode: cloud (Gemini 3.1 Flash Lite) + offline (llama-cpp Gemma 4)
- **International flat-rate comparison**: AI references GCC, European, and global standards alongside local data
- **Hybrid interaction**: free-form queries + structured guidance when needed
- System prompt includes full workshop context, Libyan slang dictionary, and international reference table
- Compound operation detection and unit estimate support

## 5. Vectorization Strategy
- **Model isolation is critical**: embeddings must weight the Model field heavily to prevent cross-contamination (e.g., Corolla brake job must not influence HD45 brake estimate)
- **Chunking**: group by (Model, Labor Code) — similar jobs for the same model are compared
- **Metrics**: primary = QTY (labor hours), secondary = Price (hourly rate)
- **Normalization**: raw Arabic descriptions cleaned through dictionary before embedding

## 6. Model Strategy (Dual-Mode)
The system operates in two modes, selected at startup via connectivity detection:

| Mode | Embedding | LLM | Internet |
|------|-----------|-----|----------|
| **Online** | `gemini-embedding-2` (384d via REST API) | `gemini-3.1-flash-lite` (free tier, GA May 2026) | Required |
| **Offline** | `paraphrase-multilingual-MiniLM-L12-v2` (384d, local via sentence-transformers) | `gemma-4-e4b-it` (via llama-cpp, OpenAI-compatible API on :8080) | None |

- Both modes produce 768-dimension vectors → same ChromaDB collection
- `ModelRouter` class handles backend selection + automatic fallback
- Embedding model configured via `EMBEDDING_MODEL` env var
- LLM model configured via `GEMINI_MODEL` / `LOCAL_LLM_MODEL` / `LOCAL_LLM_BACKEND` env vars
- API key required for online mode: `GEMINI_API_KEY` env var

## 7. Constraints
- Offline-first — must work without internet after initial data load
- Single-user V1 — no authentication, no role management
- Static data — V1 uses the current XLSX snapshot, no live POS sync
- Arabic text rendering in PDF must be verified with real data
