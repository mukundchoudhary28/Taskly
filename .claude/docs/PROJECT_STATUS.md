# Project Status

> Read this first in every session. Update it after every commit that changes behaviour, infra or structure, and at the end of every feature.

**Last updated:** 2026-09-28
**Current phase:** Phase 0 — Minimal deployed version (in progress)
**Overall:** Skeleton application built and verified locally. Ready for cloud deployment spec.

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
- `phase-00-skeleton-application` implemented: FastAPI `GET /health` with DB check, React health page, Dockerfile, docker-compose, Alembic baseline, tests — all verified locally
- `phase-00-skeleton-application` spec approved and EDD written on branch `feat/phase-00-skeleton-application`
- Local git repo, monorepo folders and `backend/` uv project scaffolded; pushed to `origin main` on GitHub
- Mission, tech stack and roadmap agreed and written to `.claude/constitution/`
- `CLAUDE.md` and living docs created
- `create-spec` skill added; each feature starts with a PRD in `.claude/specs/`

## Next up (Phase 0)
Phase 0 is being delivered as two specs: `phase-00-skeleton-application` (local app skeleton, Approved) and a follow-up `phase-00-cloud-deployment` (AWS infra + CI/CD, not yet written). `ROADMAP.md`'s Phase 0 stays a single entry; its DoD is met only once both specs ship.

**`phase-00-skeleton-application` (Approved — see `.claude/specs/phase-00-skeleton-application.md`)**
- [x] Monorepo layout (local)
- [x] uv project for `backend/`
- [x] Minimal FastAPI app with `GET /health` (checks DB)
- [x] Backend Dockerfile
- [x] Local PostgreSQL via one documented command
- [x] Alembic set up with an empty first migration
- [x] Minimal React + TS + Vite page that shows API health

**`phase-00-cloud-deployment` (not yet spec'd)**
- [x] Create the GitHub repo and push
- [ ] Terraform state bucket (S3)
- [ ] Terraform: VPC (no NAT gateway), ECR, ECS Fargate + ALB, RDS, S3 + CloudFront, Route 53 zone, ACM, CloudWatch, Budgets
- [ ] Add NS records for `taskly.` at the domain registrar
- [ ] GitHub Actions: CI (lint, type-check, test) and CD (staging auto, prod with approval) using OIDC
- [ ] Verify DoD: `https://taskly.mukundchoudhary.space` shows "API: healthy"

## Blockers
- None

## Open questions / to confirm
- Check current AWS prices and free-tier terms before provisioning
- Which registrar hosts `mukundchoudhary.space` (needed to add the NS records)

## Ideas / later
- Reminders and notifications (v1/v2)
- Billing (v1/v2)
- PWA / mobile app, shared lists, stats dashboard
