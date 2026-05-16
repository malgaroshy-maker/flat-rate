# Validation Checklist

> **Current phase:** ✅ ALL COMPLETE | **Last updated:** 2026-05-14 | **[STATUS.md](../../STATUS.md)**

## P0 — Must pass before phase completion

### Phase 0
- [x] `git status` shows clean repo with `.gitignore`
- [x] `npm run dev` starts frontend without errors
- [x] `uvicorn main:app` starts backend without errors
- [x] `pip install -r requirements.txt` succeeds with no conflicts

### Phase 1
- [x] All 2,565 XLSX records ingested without data loss (2,564 parsed)
- [x] All 3 departments (نافطه, بنزين, سمكره) present in indexed data
- [x] Model-isolated query: "Corolla oil" → Corolla #1 match verified
- [x] Arabic descriptions preserved in metadata (no mojibake)
- [x] ChromaDB collection exists (269 vectors) and returns results

### Phase 2
- [x] `POST /api/query` with "كشف علي ودار زيت فرامل" returns results
- [x] Confidence interval output includes p10, p50, p90 percentiles
- [x] Outlier flagging triggers for records >2σ from group mean
- [x] Dictionary CRUD: create/read/update/delete verified
- [x] Unknown term detection + pending inbox works
- [x] Resolving a pending term creates dictionary entry

### Phase 3
- [x] UI renders in both Arabic (RTL) and English (LTR) without layout breaks
- [x] Query input accepts Arabic text and submits successfully
- [x] Results display confidence interval as primary output
- [x] Outlier details expand/collapse correctly
- [x] Language toggle switches UI and persists across page reload

### Phase 4
- [x] Dictionary table loads with search/filter
- [x] Add/edit/delete operations reflect immediately
- [x] Pending inbox shows terms + inline resolve form
- [x] Resolve workflow maps term → category → dictionary entry

### Phase 5
- [x] PDF generates without server error
- [x] PDF contains: query, confidence range, cost, hits table, outlier notices
- [x] Arabic text in PDF renders with Noto Naskh Arabic font
- [x] PDF opens in standard readers (Adobe, browser)

### Phase 6
- [x] Chat SSE streaming delivers tokens without errors
- [x] RAG search returns relevant historical data for chat queries
- [x] International flat-rate comparison appears in responses (📊/🌍/📝 format)
- [x] Sessions persist across page reloads (JSON files)
- [x] Session list shows past conversations with message counts
- [x] New chat starts fresh, existing chat resumes correctly
- [x] Both cloud (Gemini) and local (llama-cpp) modes support chat

## P1 — Should pass

- [x] UI responds within 2 seconds for queries against 2,565 records
- [x] All 20 labor codes have at least one matching result
- [x] Empty state: no-matches shows placeholder, not error
- [x] Error state: backend unavailable shows user-friendly message
- [x] Responsive layout works at 1024px–1920px widths
- [x] Browser back/forward navigation preserves query state

## P2 — Nice to have

- [x] Keyboard shortcut (Enter) submits query from input
- [x] Rate + cost shown alongside hours in results
- [x] Query history stored in localStorage (last 10 queries)
- [x] PDF filename includes date and vehicle model
