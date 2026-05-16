# Deployment Guide

## Option 1: Docker Compose (recommended)

```bash
git clone https://github.com/malgaroshy-maker/flat-rate.git
cd flat-rate

# Create .env from template
copy backend\.env.template backend\.env
# Edit backend\.env — add your GEMINI_API_KEY

# Build and start
docker compose up --build
```

The first run takes 3-5 minutes (downloading models). Subsequent starts take ~10 seconds.

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

### First-time data ingestion (Docker)

```bash
# Ingest POS data + dictionary into ChromaDB
docker compose exec backend python scripts/ingest.py \
  --input "/app/تقرير اليد العاملة بالكامل.xlsx" \
  --input2 "/app/اليد العاملة منذ فتح المركز.xlsx" \
  --dictionary "/app/The Libyan Automotive Dictionary of Mechanical and Technical Terms.docx"
```

---

## Option 2: Manual Setup (Windows)

### Prerequisites

- Python 3.12+
- Node.js 22+
- Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Steps

```bash
# 1. Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.template .env
# Edit .env — add GEMINI_API_KEY

# 2. Data ingestion (one-time)
cd ..   # back to project root
python scripts\ingest.py \
  --input "تقرير اليد العاملة بالكامل.xlsx" \
  --input2 "اليد العاملة منذ فتح المركز.xlsx" \
  --dictionary "The Libyan Automotive Dictionary of Mechanical and Technical Terms.docx"

# 3. Start backend
cd backend
uvicorn main:app --reload --port 8000

# 4. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Or just run `start.bat` which does all of the above automatically.

---

## Option 3: Manual Setup (Linux/macOS)

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env

# Data ingestion
cd ..
python scripts/ingest.py \
  --input "تقرير اليد العاملة بالكامل.xlsx" \
  --input2 "اليد العاملة منذ فتح المركز.xlsx" \
  --dictionary "The Libyan Automotive Dictionary of Mechanical and Technical Terms.docx"

# Start
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd ../frontend
npm install
npm run dev
```

---

## Production hardening

Before deploying to production:

1. **Set strong Gemini API key** — rotate regularly
2. **Enable HTTPS** — use nginx reverse proxy with Let's Encrypt
3. **Change CORS origins** — replace `localhost:3000` with your production domain in `backend/main.py`
4. **Increase rate limits** — adjust `backend/middleware/rate_limit.py` from 30 req/min as needed
5. **Add authentication** — currently no auth (single-user V1)
6. **Backup ChromaDB** — `chroma_db/` directory contains all vector data
7. **Monitor logs** — check `backend/data/chats/` for session data growth

---

## Environment variables reference

See [backend/.env.template](../backend/.env.template) for all available variables.

Key variables for production:

| Variable | Production value |
|----------|-----------------|
| `GEMINI_API_KEY` | Your production API key |
| `EMBEDDING_SOURCE` | `gemini` (requires API quota) |
| `FORCE_LOCAL` | `false` |
| `CHROMA_PERSIST_DIR` | Persistent volume path |

---

## Troubleshooting

### "You exceeded your current quota" (429)
Gemini free tier has daily quota limits. Either:
- Wait for quota reset (~24h)
- Set `EMBEDDING_SOURCE=local` in `.env` to use local embeddings
- Upgrade to Gemini paid tier

### "HF Hub unauthenticated" warning
Set `HF_TOKEN` in `.env` from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Dictionary is empty
Run the ingestion script with `--dictionary` flag to seed terms from the DOCX dictionary.

### Port already in use
Change ports: `uvicorn main:app --port 8001`, update `NEXT_PUBLIC_API_URL` accordingly.
