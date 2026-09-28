# Architecture (as built)

> This describes what **actually exists** in the repo and on AWS. The target design is in `.claude/constitution/TECH_STACK.md`.
> Update this file whenever a component, endpoint group, table, AWS resource or data flow is added or changed.

**Last updated:** 2026-09-28

## Current state
Monorepo skeleton only. `backend/` is a uv project (Python 3.14, FastAPI, Uvicorn; pytest/ruff/mypy for dev) with empty layer packages under `app/`. `frontend/`, `infra/` and `.github/workflows/` are empty placeholders. Nothing runs or is deployed yet.

## Components
| Component | Target | Status |
|---|---|---|
| Frontend | React + TS + Vite on S3 + CloudFront | Planned |
| Backend API | FastAPI on ECS Fargate behind an ALB | Planned |
| Database | RDS PostgreSQL (private) | Planned |
| Auth | Cognito user pool + Google login | Planned (Phase 1) |
| DNS / TLS | Route 53 zone for `taskly.mukundchoudhary.space`, ACM | Planned |
| Secrets | Secrets Manager / SSM | Planned |
| Monitoring | CloudWatch logs and alarms, AWS Budgets | Planned |
| IaC | Terraform, state in S3 | Planned |
| CI/CD | GitHub Actions with OIDC; staging → prod with approval | Planned |

## Environments
| Environment | Frontend URL | API URL | Status |
|---|---|---|---|
| Staging | `staging.taskly.mukundchoudhary.space` | `api.staging.taskly.mukundchoudhary.space` | Not created |
| Prod | `taskly.mukundchoudhary.space` | `api.taskly.mukundchoudhary.space` | Not created |

## API surface
_No endpoints yet._ When endpoints are added, list them here by group (e.g. `health`, `me`, `tasks`) with one line each. The full contract is the generated OpenAPI spec.

## Data model
_No tables yet._ When a migration adds or changes a table, summarise it here and note the migration id.

## Request flow
_Not implemented yet._ Target flow: browser → CloudFront (frontend) → API over HTTPS with a Cognito JWT → FastAPI verifies the token → PostgreSQL.

## Decision log
Record significant decisions here (what, why, alternatives). Decisions already made at planning time are in `.claude/constitution/TECH_STACK.md`.

| Date | Decision | Why | Alternatives considered |
|---|---|---|---|
| 2026-09-28 | Backend on ECS Fargate | Portable container skills; suits future AI workloads | Lambda, EC2, EKS |
| 2026-09-28 | Auth with Cognito | Managed, secure, supports Google login | Build in FastAPI, Auth0, Clerk |
| 2026-09-28 | Terraform for IaC | Multi-cloud, widely used | AWS CDK |
| 2026-09-28 | Recurring tasks stored as rules + per-day completions | Clean edits and streaks | Pre-generating task copies |
