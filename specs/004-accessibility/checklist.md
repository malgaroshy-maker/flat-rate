# Validation Checklist — Accessibility & RTL

## P0 — Critical (must fix before phase complete)

### Keyboard Accessibility
- [x] SessionList items are keyboard-operable (converted to `<button>` elements)
- [x] All interactive elements reachable via Tab key
- [x] No keyboard traps (all elements are native interactive elements)
- [x] Focus returns to trigger after interactions (native browser behavior)

### Form Labeling
- [x] QueryInput has accessible label (aria-label)
- [x] ChatPanel input has accessible label (aria-label)
- [x] DictionaryPanel inputs (4) all have accessible labels (aria-label)
- [x] PendingPanel inputs (3) all have accessible labels (aria-label)

### Dynamic Content
- [x] ChatPanel streaming area has `role="log"` + `aria-live="polite"`
- [x] Loading states announce to screen readers (role="status")
- [x] Empty states announced to screen readers (role="status")

## P1 — High

- [x] `focus-visible:ring-2` on all interactive elements via Tailwind utility classes
- [x] All decorative SVGs have `aria-hidden="true"` (20+ icons)
- [x] All icon-only buttons have `aria-label`
- [x] Expandable sections have `aria-expanded` and `aria-controls` (ResultsCard, OutlierPanel)
- [x] Skip-to-content link present in ClientShell header

## P2 — Medium

- [x] `aria-current="page"` on active nav link
- [x] Toggle buttons have `aria-pressed` and `role="radio"` + `role="radiogroup"`
- [x] Table headers have `scope="col"`
- [x] Chat messages have ARIA roles (`role="article"`, `aria-label`)
- [x] `forced-colors` media query present in CSS

## P3 — Low

- [x] Build compiles with 0 errors (6 routes)
- [x] Lint passes with 0 warnings
- [x] `prefers-reduced-motion` still works
- [x] `viewport` metadata correctly exported per Next.js 16 spec
