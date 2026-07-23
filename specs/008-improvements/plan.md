# Improvement Plan — Android App, AI Components & Backend

> Created: 2026-07-23 | Updated: 2026-07-23 | Status: Phases A, B, E done and verified; C/D done for chat+search+dictionary+settings; F/G not started
> Scope: Backend responsiveness + AI quality (system prompt & Libyan dictionary) + Flutter app UX/design/features

## Progress snapshot

| Phase | Status |
|---|---|
| A — Backend streaming & cold start | ✅ Done, live on Render |
| B — Dictionary-aware RAG + prompt rebuild | ✅ Done, live on Render (B6 eval harness skipped) |
| C — Chat UX overhaul | ✅ Core done (stop/retry/copy/suggestions); C7 session search still open |
| D — Visual redesign | ◐ Dark mode + Arabic typography + theme-aware screens done; micro-interactions (D4) and full screen-by-screen polish (D3) not done |
| E — Offline resilience | ✅ E1–E3 done (dictionary/search cache, chat outbox); E4–E6 (voice input, quick-estimate form, PDF from phone) not started |
| F — Deploy/ops hardening | Not started |
| G — Signed release APK | ✅ Build/signing done, v1.0.0 delivered; needs a real on-device smoke test + in-app update check (blocked on F4) |

---

## Decisions (confirmed with owner)

| Decision | Choice |
|---|---|
| Hosting | Stay on Render free tier; mitigate cold starts |
| LLM | Keep Gemini (free tier) |
| App priorities | Chat UX overhaul, visual redesign, offline resilience, new features |
| Distribution | Signed APK sideload (internal workshop team) |

---

## Findings from analysis (what drives this plan)

1. **Streaming exists but is broken in feel, not in wiring.** SSE is implemented end-to-end, but:
   - `_stream_cloud_multi()` in `backend/chat_engine.py` iterates the Gemini stream **synchronously inside an async generator** — it blocks the FastAPI event loop and chunks arrive in bursts instead of smoothly.
   - Render free tier sleeps → 30–60s cold start with zero feedback in the app.
   - No first-byte feedback: the user sees nothing until the first model token arrives (RAG search + prompt build + Gemini TTFB all happen silently).
2. **The Libyan dictionary is underused.**
   - At query time, the user's raw text (often dialect: براونطي، فرسيوني، مزطوري) goes straight to the embedding model with **no term expansion** — recall suffers when records were normalized differently.
   - The system prompt contains a **hardcoded, abbreviated, partially wrong** copy of the glossary (e.g. maps ديسكو only to clutch disc; the curated MD says it is context-dependent: wheel disc / brake disc / clutch disc). Two sources of truth that have already drifted.
3. **Flutter bug:** `chat_provider.dart:101` — `data.substring(14)` on the 13-char `'__session_id:'` prefix drops the first character of every session ID.
4. **RAG runs only on the first message** of a session (`chat_engine.py:24`) — follow-ups like "and what about the rear bumper?" get no fresh data.
5. Chat renders raw text (the model outputs Markdown tables/bold that show as literal `**` and `|`), no typing indicator, no retry, no cold-start state.

---

## Phase A — Backend responsiveness & streaming (highest impact)

**Goal: first visible token < 2s on warm server; smooth token-by-token flow; graceful cold start.**

- [x] A1. Fix blocking Gemini stream: switched to `client.aio.models.generate_content_stream(...)`. Verified locally and in prod that chunks arrive smoothly, not in one burst.
- [x] A2. Immediate SSE feedback: `{"status":"searching"}` / `{"status":"thinking"}` events wired end-to-end, rendered in the app as a labeled progress indicator.
- [x] A3. RAG now runs on every message, not just the first.
- [x] A4. Cold-start mitigation: cron-job.org keep-alive configured (every 10–15 min, workshop hours, documented in `docs/deployment.md`); app-side `/api/health` warm-up ping fires when the chat screen opens. Startup lazy-imports were already in place.
- [x] A5. Streaming hardening: `event: done` terminator + `: ping` heartbeats every 15s added.
- [x] A6. Session-id prefix bug fixed — replaced the magic-number `substring(14)` with length-derived stripping off a shared prefix constant.

## Phase B — AI quality: dictionary-aware RAG + rebuilt system prompt

**Goal: one source of truth for terminology; dialect queries retrieve as well as fusha ones; prompt stays correct as the dictionary grows.**

- [x] B1. **Single source of truth.** `ingestion/md_parser.py` now captures fusha meaning + context-dependency notes (was silently dropped before) and splits multi-variant terms (براونطي/برونطي/باراوانطي) into separately matchable entries. `dictionary_store.seed_or_update_terms()` backfilled 158 existing terms + added 70 new ones. Hardcoded glossary blocks removed from `system_prompt.py`.
- [x] B2. **Query-time term expansion.** `backend/term_expander.py` — Arabic normalization (tashkeel stripped, أ/إ/آ→ا, ة→ه, ى→ي) + dictionary term matching, expands the embedding query with fusha/English before search. Verified: "براونطي" correctly resolves without the model asking what it means.
- [x] B3. **Dynamic glossary injection.** `format_rag_context()` now takes `matched_terms` and renders only the terms actually found in the current query.
- [x] B4. **Rebuilt the system prompt.** Hardcoded glossary removed; workshop stats now computed live from ChromaDB via `workshop_stats.py` (real data: 150 models / 8,422 records vs. the stale hardcoded "95 models / 2,564 records"). Two few-shot examples added (dialect query + sparse-data case). Markdown format guidance already matched the app's renderer.
- [x] B5. **RAG context format**: hit descriptions added, similarity now labeled high/medium/low.
- [ ] B6. Evaluation harness — not built. Improvement was verified manually (dialect query test) but not measured with a scored eval set. **Still open if rigor is wanted.**

## Phase C — Flutter chat UX overhaul

**Goal: the chat feels like a modern AI assistant.**

- [x] C1. Markdown rendering was already in place (`flutter_markdown`); made theme-aware for dark mode.
- [x] C2. Status-driven progress indicator ("يبحث في البيانات…" → "يفكر…") wired to the new backend events.
- [ ] C3. Cold-start-specific banner ("الخادم يستيقظ…") not built — the generic offline/status indicators exist but there's no dedicated slow-warm-up messaging distinct from a normal wait.
- [x] C4. Stop-generation button, retry on error (fixed a bug where errors used to wipe the whole conversation via `AsyncValue.error`), offline detection banner.
- [x] C5. Copy-to-clipboard on long-press done. Share and regenerate-response not done.
- [x] C6. Suggested prompt chips on empty chat.
- [~] C7. Auto-title (pre-existing) and swipe-to-delete (added) done; session search not built.

## Phase D — Visual redesign

**Goal: coherent, modern Material 3 identity with first-class Arabic/RTL.**

- [x] D1. Material 3 `ColorScheme.fromSeed`-based light/dark themes built (dark theme didn't exist before at all — `themeMode` was hardcoded light). Theme picker added to Settings.
- [x] D2. Arabic typography: IBM Plex Sans Arabic wired in for the `ar` locale (previously Arabic text rendered in a Latin-only font).
- [~] D3. Chat, search, dictionary, pending, and settings screens made theme-aware (were hardcoded `AppColors`, which would've looked broken in dark mode) and their i18n bugs fixed, but this wasn't a visual redesign pass — no new bubble avatars/timestamps, no sticky dictionary index, no confidence-bar redesign.
- [ ] D4. Micro-interactions not done (confidence card already had a scale-in animation from before this session).
- [~] D5. No dedicated RTL audit pass, but every screen touched this session was manually tested in both locales as part of the i18n bug fixes.

## Phase E — Offline resilience & new features

- [x] E1. Offline dictionary: implemented as a synced local SQLite cache (not a bundled static asset) — mirrors every successful fetch, falls back to it when offline, with a visible banner.
- [x] E2. Estimate cache: last 50 distinct search queries cached in SQLite, served with an "offline — cached data" badge when the network is down.
- [x] E3. Outbox: offline chat messages queue to SQLite, show a "queued" bubble, and auto-flush the moment connectivity returns (including messages still queued from a previous app session).
- [ ] E4. Voice input — not started.
- [ ] E5. Quick-estimate form — not started.
- [ ] E6. PDF export from phone — not started (backend `pdf_generator.py`/`/api/export/pdf` already exists and is called by `pdfExportProvider`, but there's no share/download UI wired to it in the app).

## Phase F — Cloud backend: deployment & ops on Render

**Goal: every backend change ships to Render immediately; the deployment itself gets faster, leaner, and observable.**

- [ ] F1. **Deploy pipeline**: auto-deploy on push to `master` (Render GitHub integration); document the flow in `docs/deployment.md` so a backend phase isn't "done" until it's live and verified via `/health`.
- [ ] F2. **Slim the Docker image** for faster cold starts: multi-stage build, prune build deps and unused packages (PDF/docx libs lazy-imported per A4), tighten `.dockerignore` (exclude `venv/`, `chroma_db_upload.zip`, `flutter_app/`, `video/`). Target: measurably faster boot on Render's free instance.
- [ ] F3. **ChromaDB in the image**: keep baking `backend/chroma_db/` into the image (read-only at runtime) since Render free has an ephemeral disk; add a startup integrity check (collection count logged) so a bad build fails loudly, not with empty RAG results.
- [ ] F4. **Config hygiene**: all secrets (GEMINI_API_KEY) and toggles via Render env vars only; add a `/api/version` endpoint returning git SHA + build date so the app and you can confirm what's live.
- [ ] F5. **Observability**: structured logging (request timing, RAG hit counts, Gemini latency, cold-start duration), and Render health-check path set to `/health` so failed deploys roll back instead of serving errors.
- [ ] F6. **Post-deploy smoke test**: tiny script (`scripts/smoke_prod.py`) hitting `/health`, one `/api/query`, and one streamed `/api/chat/send` against the live URL after each deploy.

## Phase G — Release engineering (APK sideload)

- [x] G1. Signed release build done: upload keystore generated (gitignored, backed-up instructions in `docs/deployment.md`), `build.gradle.kts` signing config wired with a safe debug-key fallback when `key.properties` is absent, R8 minify + resource shrinking enabled. `flutter build apk --release --split-per-abi` verified: correct signature fingerprint (not debug key), correct package/version/permissions via `apksigner`/`aapt`. v1.0.0 APK delivered.
- [ ] G2. In-app update check — blocked on F4 (`/api/version` doesn't exist yet). Not started.
- [x] G3. Release API base URL baked via `--dart-define=API_BASE_URL=https://flat-rate.onrender.com`. Crash logging not set up (no Sentry/error-report endpoint).
- [~] G4. No physical device available in this environment — verified everything short of an actual on-device install (signature, manifest, package contents, build success). **A real device install/smoke-test is still needed before handing this to the team.**

---

## Additional fixes made along the way (not originally in the plan)

- **The Flutter app was never tracked in git.** Most of the completed mobile app (STATUS.md Phase 14, "30/30 done") existed only on the local machine. Committed the full app (platform scaffolding + remaining `lib/`/`test/` sources) — 171 files.
- **`/api/chat/send` passed a JSON-encoded conversation history through URL query params on a POST request.** For long conversations this risks hitting router/proxy URL-length limits (~8KB typical cap). Moved to a JSON body; the old query-param path is kept as a fallback so an already-installed APK isn't broken until it's updated (sideload distribution isn't atomic with backend deploys).
- **Dictionary add/edit dialog and the entire Pending Review screen were hardcoded to English** regardless of the selected locale — the Arabic l10n strings existed in the `.arb` files but were never wired up in the widgets.

## Suggested order & effort

| Order | Phase | Effort | Why first |
|---|---|---|---|
| 1 | A (backend streaming/cold start) | ~1 day | Biggest perceived-speed win; everything else builds on it |
| 2 | F1–F4 (deploy pipeline + image slimming) | ~0.5 day | Ship Phase A to Render immediately; faster cold starts compound with A4 |
| 3 | B (dictionary + prompt) | ~1–2 days | Core AI quality; B6 eval proves it — deploy to Render on completion |
| 4 | C (chat UX) | ~1–2 days | Pairs with A's new status events |
| 5 | D (visual redesign) | ~2 days | Independent, can interleave with C |
| 6 | E (offline + features) | ~2–3 days | E1–E3 first, E4–E6 as capacity allows |
| 7 | F5–F6 (observability + smoke test) | ~0.5 day | Lock in ops before release |
| 8 | G (release APK) | ~0.5 day | Ship it |

**Rule for every backend phase (A, B, F): it is not done until it is deployed to Render and verified live via `/health` + a real chat request.**

## Acceptance criteria

- Warm server: first visible chat feedback < 300ms (status event), first token < 2.5s.
- Cold server: user sees an explicit "server waking" state, never a raw timeout.
- Dialect query eval (B6): hit@5 improves measurably over baseline; no regression on fusha queries.
- System prompt contains **zero** hardcoded glossary/stats that duplicate `dictionary.json` or the dataset.
- Assistant answers render as formatted Markdown, RTL-correct, with copy/share/retry.
- Dictionary browsing and cached estimates work in airplane mode.
- Signed release APK installs and passes the smoke-test checklist on a physical device.
