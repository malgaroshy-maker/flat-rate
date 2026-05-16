# Smart Labor Cost Estimator

Bilingual (Arabic/English) RAG system that estimates labor hours and cost from natural-language queries against historical POS data. Built for automotive workshops.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)

## Features

- **Natural language queries** in Arabic or English — "تغيير باطني امامي مع تغيير زيت hd45"
- **Confidence intervals** — P10/P50/P90 percentile ranges from historical data
- **AI Assistant** — SSE streaming chat with multi-turn context, international rate comparison
- **Dictionary** — 106 Libyan Arabic→standard automotive terms across 9 categories
- **Pending review** — Unknown terms inbox with batch resolve
- **PDF export** — Professional reports with embedded Arabic font
- **Dual-mode** — Cloud (Gemini 3.1 Flash Lite) or local (Gemma 4 E4B via llama-cpp)
- **RTL support** — Full Arabic right-to-left layout, WCAG 2.2 AA accessibility
- **Confidence rating** — High/Medium/Low badge on every estimate

## Data scope

| Metric | Value |
|--------|-------|
| Records | 8,422 (from 2 POS XLSX files) |
| Vehicle brands | 25 |
| Vehicle models | 95 |
| Workshops | 6 departments across diesel, gasoline, body & paint |
| ChromaDB chunks | 514 |
| Date range | Center opening — May 2026 |

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16 (TypeScript, App Router, Tailwind v4) |
| Backend | Python FastAPI |
| Vector DB | ChromaDB (local) |
| Embedding | Gemini Embedding 2 (cloud, 384d) / paraphrase-multilingual-MiniLM-L12-v2 (local) |
| LLM | Gemini 3.1 Flash Lite (cloud) / Gemma 4 E4B via llama-cpp (local) |
| PDF | reportlab + arabic-reshaper + Noto Naskh Arabic font |
| Chat | SSE streaming, JSON session persistence |

## Quick start

### Prerequisites
- Python 3.12+
- Node.js 22+
- Gemini API key (free tier, from [aistudio.google.com](https://aistudio.google.com))

### Option 1: start.bat (Windows)
```bash
start.bat
```
Opens backend (:8000) and frontend (:3000) in separate windows. Pre-flight checks for venv, node_modules, .env, and API key.

### Option 2: Manual
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.template .env
# Edit .env — add your GEMINI_API_KEY
python scripts/ingest.py \
  --input "../تقرير اليد العاملة بالكامل.xlsx" \
  --input2 "../اليد العاملة منذ فتح المركز.xlsx" \
  --dictionary "../The Libyan Automotive Dictionary of Mechanical and Technical Terms.docx"
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Option 3: Docker
```bash
docker compose up --build
```

## API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Status, mode, model info |
| `POST` | `/api/query` | RAG search: hits + confidence + outliers |
| `POST` | `/api/export/pdf` | Generate PDF report |
| `GET/POST/PUT/DELETE` | `/api/dictionary` | Term CRUD |
| `GET/POST` | `/api/dictionary/pending` | Unknown terms inbox |
| `POST` | `/api/dictionary/pending/{id}/resolve` | Map term to category |
| `POST` | `/api/settings/mode` | Toggle cloud/local mode |
| `POST` | `/api/chat/send` | SSE streaming chat |
| `GET` | `/api/chat/sessions` | List chat sessions |
| `GET/DELETE` | `/api/chat/sessions/{id}` | Get/delete session |

## Frontend routes

| Route | Purpose |
|-------|---------|
| `/` | Search & query results |
| `/assistant` | AI chat with international comparison |
| `/dictionary` | Term CRUD table |
| `/pending` | Review inbox |
| `/settings` | Language + mode toggles + system info |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Gemini API key (required for cloud mode) |
| `GEMINI_MODEL` | `gemini-3.1-flash-lite` | Cloud LLM model |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-2` | Cloud embedding model |
| `EMBEDDING_SOURCE` | `gemini` | "gemini" or "local" |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Local embedding model |
| `LOCAL_LLM_BACKEND` | `llamacpp` | "llamacpp" or "ollama" |
| `LOCAL_LLM_HOST` | `http://localhost:8080` | Local LLM URL |
| `LOCAL_LLM_MODEL` | `gemma-4-e4b-it` | Local LLM model name |
| `HF_TOKEN` | — | HuggingFace token (for higher rate limits) |
| `FORCE_LOCAL` | `false` | Force offline mode |
| `CHROMA_PERSIST_DIR` | `../chroma_db` | Vector DB storage path |

## Running tests

```bash
# All tests (core + QA + security + performance)
cd backend
venv\Scripts\python.exe -m pytest tests qa -v

# Frontend lint
cd frontend
npm run lint
```

## Project structure

```
├── backend/
│   ├── ingestion/          # XLSX/DOCX parsers, normalizer, pipeline
│   ├── routers/            # FastAPI route handlers
│   ├── services/           # Pipeline orchestrator, query/chat service
│   ├── middleware/          # Rate limiter, security headers, input sanitizer
│   ├── qa/                 # RAG quality, API security, performance, reality check
│   └── data/               # Chat sessions, dictionary JSON
├── frontend/
│   └── src/
│       ├── app/            # Next.js pages + layout
│       ├── components/     # UI components (QueryInput, ResultsCard, ChatPanel, etc.)
│       ├── context/        # Language context provider
│       └── lib/            # API client, i18n, chat SSE client
├── scripts/
│   └── ingest.py           # Data ingestion CLI
├── specs/                  # Spec folders (12 phases)
├── docker-compose.yml
└── start.bat
```

## License

MIT — see [LICENSE](LICENSE) for details.
