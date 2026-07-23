# STATUS — Smart Labor Cost Estimator

> Updated: 2026-07-23 | Deployment: Render (production) + Cloudflare Tunnel (local dev, free)

| Phase | Name | Status | Completed |
|-------|------|--------|-----------|
| 0 | Scaffolding | ✅ done | 9/9 |
| 1 | Data Pipeline | ✅ done | 7/7 |
| 2 | Backend API | ✅ done | 9/9 |
| 3 | Frontend Core | ✅ done | 7/7 |
| 4 | Dictionary & Settings UI | ✅ done | 6/6 |
| 5 | PDF Export | ✅ done | 5/5 |
| 6 | AI Assistant Chat | ✅ done | 8/8 |
| 7 | UI/UX Redesign | ✅ done | 8/8 |
| 8 | RAG Quality | ✅ done | 15/15 |
| 9 | API Security & Performance | ✅ done | 14/14 |
| 10 | Accessibility & RTL Remediation | ✅ done | 18/18 |
| 11 | Service Layer & Orchestration | ✅ done | 10/10 |
| 12 | Performance + Data + UX | ✅ done | 20/20 |
| 13 | GitHub Prep + Deployment | ✅ done | 7/7 |
| 14 | Flutter Mobile App | ✅ done | 30/30 |
| 15 | Public Hosting & Tunneling | ✅ done | 5/5 |
| 16 | [Improvement Plan](specs/008-improvements/plan.md): streaming, dictionary AI, chat UX, dark mode, offline | ◐ in progress | A/B/E done, C/D partial, F/G not started |

## Deployment

| Method | File | Purpose |
|--------|------|---------|
| Render | (GitHub-linked, auto-deploy on push to `master`) | **Production backend** — `https://flat-rate.onrender.com`, free tier, kept warm via cron-job.org during workshop hours |
| `start.bat` | Windows | Local dev — web + mobile (0.0.0.0:8000, shows network IP) |
| `tunnel.bat` | Windows | Public URL via Cloudflare Tunnel for local dev (free, no server) |
| `deploy.bat` | Windows | Backend 24/7 background (no terminal) |
| `docker compose up` | Any | Full stack (backend + frontend) |
| `deploy_vps.sh` | Linux VPS | One-command production deployment (alternative to Render) |

## Quick links
- [Spec](specs/001-labor-estimator/spec.md)
- [Tasks](specs/001-labor-estimator/tasks.md)
- [Checklist](specs/001-labor-estimator/checklist.md)
- [Implementation Summary](specs/001-labor-estimator/implementation-summary.md)
- [Deployment Guide](../docs/deployment.md)
- [RAG Quality Spec](specs/002-rag-quality/spec.md)
- [API Security Spec](specs/003-api-security/spec.md)
- [Accessibility Spec](specs/004-accessibility/spec.md)
- [Improvement Plan (streaming/AI/UX/offline)](specs/008-improvements/plan.md)
