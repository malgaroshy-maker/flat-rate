# Plan: Accessibility & RTL Remediation

## Phase 1: Critical Fixes
Keyboard accessibility + labeled inputs + live regions.
- Fix SessionList clickable divs → semantic buttons
- Add labels to all 7 form inputs
- Add `aria-live` regions for streaming chat + loading states

## Phase 2: Focus + SVG
Focus indicators and SVG accessibility.
- Add `:focus-visible` ring to globals.css
- Add `aria-hidden="true"` to all 15+ inline SVGs
- Add `aria-label` to all icon-only buttons

## Phase 3: Expand + Skip
Interactive state announcements and navigation.
- Add `aria-expanded` + `aria-controls` to expandable sections
- Add skip-to-content link in layout.tsx
- Add `aria-current` to active nav + session items

## Phase 4: Semantic Enrichment
ARIA attributes for Settings, Dictionary, Chat.
- Add `aria-pressed` to toggle buttons
- Add `scope="col"` to table headers
- Apply `role` prop as actual ARIA role in ChatMessage
- Add `aria-label` to chat messages

## Phase 5: CSS & Linting
Low-priority CSS improvements and linting integration.
- Add `forced-colors` media query
- Enable `eslint-plugin-jsx-a11y`

## Phase 6: Documentation
Update project .md files.
