# Spec: Accessibility & RTL Audit (Accessibility Auditor)

> Inspired by agency-agents: Accessibility Auditor pattern.
> Parent project: specs/001-labor-estimator/

## 1. Objective

Remediate critical WCAG 2.2 AA gaps found in the bilingual (Arabic/English) RTL frontend. Current audit found zero `aria-*` attributes, no labeled form inputs, non-keyboard-accessible interactive elements, no focus indicators, and no live regions for dynamic content.

## 2. Audit Findings (14 issues)

| # | Severity | Issue | Components affected |
|---|----------|-------|---------------------|
| 1 | Critical | Clickable divs not keyboard-accessible | SessionList |
| 2 | Critical | No labeled form inputs (7 inputs) | QueryInput, ChatPanel, DictionaryPanel, PendingPanel |
| 3 | Critical | No live regions for dynamic content | ChatPanel (streaming), all loading/empty states |
| 4 | High | No `:focus-visible` ring globally | globals.css, all interactive elements |
| 5 | High | 15+ inline SVGs lack `aria-hidden="true"` | All components |
| 6 | High | No `aria-expanded` on expandable sections | ResultsCard, OutlierPanel |
| 7 | High | No skip-to-content link | layout.tsx |
| 8 | High | No `aria-label` on icon-only buttons | All components |
| 9 | Medium | No `aria-current` on navigation | ClientShell, SessionList |
| 10 | Medium | No `aria-pressed` on toggle buttons | SettingsPanel |
| 11 | Medium | No `scope="col"` on table headers | DictionaryPanel |
| 12 | Medium | Chat message `role` prop unused for ARIA | ChatMessage |
| 13 | Low | No `forced-colors` media query support | globals.css |
| 14 | Low | No `<title>` in inline SVGs | All SVG icons |

## 3. Target Standards

- WCAG 2.2 Level AA
- Arabic RTL screen reader compatibility (VoiceOver/NVDA)
- Keyboard-only operation for all critical user journeys
- `prefers-reduced-motion` respected already (maintain this)
- `eslint-plugin-jsx-a11y` enabled for CI linting
