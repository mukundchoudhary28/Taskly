# Project Status

> Read this first in every session. Update it after every commit that changes behaviour, infra or structure, and at the end of every feature.

**Last updated:** 2026-09-28
**Current phase:** Phase 0 — Minimal deployed version (in progress)
**Overall:** Planning complete. Ready to start building.

## Phase progress
| Phase | Name | Status |
|---|---|---|
| 0 | Minimal deployed version | In progress |
| 1 | Authentication | Not started |
| 2 | Core tasks | Not started |
| 3 | Dates | Not started |
| 4 | Priority and ordering | Not started |
| 5 | Carry-over | Not started |
| 6 | Recurring tasks | Not started |
| 7 | Streaks | Not started |
| 8 | Hardening | Not started |

Statuses: Not started / In progress / Blocked / Done (DoD met and deployed to prod).

## Done recently
- Local git repo, monorepo folders and `backend/` uv project scaffolded (no app code yet)
- Mission, tech stack and roadmap agreed and written to `constitution/`
- `CLAUDE.md` and living docs created
- `create-spec` skill added; each feature starts with a PRD in `specs/`

## Next up (Phase 0)
- [x] Monorepo layout (local)
- [ ] Create the GitHub repo and push
- [ ] Terraform state bucket (S3)
- [x] uv project for `backend/`
- [ ] Minimal FastAPI app with `GET /health` (checks DB), Dockerfile
- [ ] Minimal React + TS + Vite page that shows API health
- [ ] Terraform: VPC (no NAT gateway), ECR, ECS Fargate + ALB, RDS, S3 + CloudFront, Route 53 zone, ACM, CloudWatch, Budgets
- [ ] Add NS records for `taskly.` at the domain registrar
- [ ] GitHub Actions: CI (lint, type-check, test) and CD (staging auto, prod with approval) using OIDC
- [ ] Alembic set up with an empty first migration
- [ ] Verify DoD: `https://taskly.mukundchoudhary.space` shows "API: healthy"

## Blockers
- None

## Open questions / to confirm
- Async Postgres driver for SQLAlchemy (asyncpg vs psycopg 3) — decide when adding the DB check / Alembic
- Check current AWS prices and free-tier terms before provisioning
- Which registrar hosts `mukundchoudhary.space` (needed to add the NS records)

## Ideas / later
- Reminders and notifications (v1/v2)
- Billing (v1/v2)
- PWA / mobile app, shared lists, stats dashboard
