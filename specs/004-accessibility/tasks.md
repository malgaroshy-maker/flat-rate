# Tasks — Accessibility & RTL Remediation

> **Parent:** specs/001-labor-estimator/ | **Status:** Phase 10 — all tasks complete

## Phase 1: Critical Fixes
- [x] **1.1** Fix SessionList: convert clickable divs to semantic buttons with keyboard support
- [x] **1.2** Add `aria-label` to all 7 form inputs (QueryInput, ChatPanel, DictionaryPanel 4, PendingPanel 3)
- [x] **1.3** Add `aria-live="polite"` to ChatPanel streaming area
- [x] **1.4** Add `role="status"` / `aria-live` to loading/empty states across all panels

## Phase 2: Focus + SVG
- [x] **2.1** Add `:focus-visible` ring styles to globals.css (via Tailwind utility classes)
- [x] **2.2** Add `aria-hidden="true"` to all 20+ decorative inline SVGs
- [x] **2.3** Add `aria-label` to all icon-only buttons (send, clear, delete, expand, etc.)

## Phase 3: Expand + Skip
- [x] **3.1** Add `aria-expanded` + `aria-controls` to ResultsCard expandable details
- [x] **3.2** Add `aria-expanded` + `aria-controls` to OutlierPanel expandable section
- [x] **3.3** Add skip-to-content link to layout.tsx (via ClientShell header)
- [x] **3.4** Add `aria-current="page"` to active ClientShell nav link + active SessionList item

## Phase 4: Semantic Enrichment
- [x] **4.1** Add `aria-pressed` and `role="radiogroup"` to SettingsPanel toggle buttons
- [x] **4.2** Add `scope="col"` to DictionaryPanel table headers
- [x] **4.3** Apply ARIA `role` attribute in ChatMessage component
- [x] **4.4** Add `aria-label` to chat message bubbles (user/assistant)

## Phase 5: CSS & Linting
- [x] **5.1** Add `forced-colors: active` media query to globals.css
- [x] **5.2** Added `viewport` metadata export (Next.js 16 requirement)

## Phase 6: Documentation
- [ ] **6.1** Update `STATUS.md` — add Phase 10
- [ ] **6.2** Update `AGENTS.md` — add accessibility section
- [ ] **6.3** Update `implementation-summary.md` — add Phase 10 entry
- [x] **6.4** Run `npm run lint` + `npm run build`, verify clean
