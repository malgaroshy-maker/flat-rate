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

## Option 4: Cloudflare Tunnel (public URL, free)

The easiest way to make your local backend accessible from anywhere — no server, no cost.

### How it works
```
Phone/Mobile App → Cloudflare Edge → Encrypted QUIC Tunnel → Your PC (localhost:8000)
```

### Setup (one-time)

```bash
# Windows (PowerShell as admin)
iwr https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe -OutFile "$env:ProgramFiles\cloudflared\cloudflared.exe"
# Add to PATH: setx PATH "$env:PATH;$env:ProgramFiles\cloudflared"
```

### Usage

```bash
# 1. Start backend (keep running)
start.bat

# 2. Start tunnel in a new terminal
tunnel.bat
```

The tunnel prints a URL like `https://britannica-nominated-scotia-patterns.trycloudflare.com`. Copy this URL into your mobile app config:

```dart
// flutter_app/lib/core/constants/api_config.dart
static const String baseUrl = 'https://YOUR-TUNNEL.trycloudflare.com';
```

Then rebuild the Flutter APK. The URL stays the same as long as the `tunnel.bat` window stays open.

### What didn't work (and why)

| Service | Issue |
|---------|-------|
| **Fly.io** (free) | 1GB RAM insufficient for sentence-transformers (~500MB) + backend |
| **Gemini free tier** | Embedding quota exhausted after 1-2 queries (need 514 chunks) |
| **ngrok** | Blocked by ISP in some regions (ERR_NGROK_9040) |
| **serveo** | Unstable SSH tunnel, 502 errors |

---

## Option 5: Render (current production backend)

The live backend is deployed on [Render](https://render.com) free tier at `https://flat-rate.onrender.com`, wired to auto-deploy on every push to `master`. ChromaDB is baked into the Docker image (Render's free tier disk is ephemeral, so it can't be written at runtime).

### Cold starts

Render free-tier web services spin down after ~15 minutes with no incoming traffic, then take 30–60s to wake on the next request. Two mitigations are in place:

1. **Keep-alive ping** — a free [cron-job.org](https://cron-job.org) job hits `GET https://flat-rate.onrender.com/api/health` every 10 minutes during workshop hours (09:00–17:00, Africa/Tripoli, Sunday–Thursday + Saturday — Friday excluded as the weekend day). Crontab: `0,10,20,30,40,50 9-17 * * 0-4,6`. Outside that window the service is allowed to sleep to conserve free-tier instance hours, since no one is using it.
2. **App-side warm-up** — the Flutter app fires a fire-and-forget `GET /api/health` as soon as the chat screen opens (`ChatRepository.warmUp()`), so a cold start overlaps with the user typing instead of happening after they hit send.

If workshop hours change, update the cron-job.org schedule's Hours/Days-of-week fields to match.

### Verifying a deploy went live

```bash
curl https://flat-rate.onrender.com/api/health
```

---

## Mobile app releases (Android APK sideload)

The app is distributed as a signed APK sideloaded directly to the workshop team's devices — no Play Store.

### The signing keystore

`flutter_app/android/keystore/upload-keystore.jks` is the **upload key** — it's what proves every release build actually came from you. It is **not committed to git** (gitignored, along with `key.properties`), which means:

- **Back it up somewhere durable** (password manager, private cloud folder) — if it's lost, there is no way to publish an update that Android will accept as "the same app" on devices that already have it installed. The only recovery is uninstalling and reinstalling on every device.
- `flutter_app/android/key.properties` holds the store/key passwords in plain text, matching the keystore above. Treat it like a credential file — back it up alongside the keystore, never paste its contents anywhere public.
- On a fresh clone (or a new machine) without `key.properties` present, `flutter build apk --release` still succeeds but silently falls back to the **debug** signing key (see `android/app/build.gradle.kts`) — that build is fine for local testing but must never be distributed to the team, since it can't be upgraded in place by a properly-signed build later.

### Building a release

```bash
cd flutter_app
flutter build apk --release --split-per-abi --dart-define=API_BASE_URL=https://flat-rate.onrender.com
```

Output lands in `flutter_app/build/app/outputs/flutter-apk/` — `--split-per-abi` produces separate smaller APKs per CPU architecture (`app-armeabi-v7a-release.apk`, `app-arm64-v8a-release.apk`, `app-x86_64-release.apk`); most modern phones are `arm64-v8a`.

Before bumping a release, update the version in `flutter_app/pubspec.yaml` (`version: X.Y.Z+buildNumber`) — Android uses `buildNumber` to decide whether an APK you sideload counts as an upgrade over what's installed.

### Installing on a device

Transfer the relevant `app-<abi>-release.apk` to the phone (USB, or share via the workshop's usual method) and open it — the device needs "install unknown apps" allowed for whatever app is used to open the file (Settings → Apps → Special access → Install unknown apps).

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
