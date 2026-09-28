# Architecture (as built)

> This describes what **actually exists** in the repo and on AWS. The target design is in `.claude/constitution/TECH_STACK.md`.
> Update this file whenever a component, endpoint group, table, AWS resource or data flow is added or changed.

**Last updated:** 2026-09-28

## Current state
Backend and frontend run locally and in containers. `GET /health` checks API + database status with a bounded timeout (default 3s) and returns no internal error detail. Local PostgreSQL runs via `docker compose up -d db`. Alembic is initialized with an empty baseline migration — no product tables. The React frontend displays loading/healthy/degraded/error states. Nothing is deployed to AWS yet.

## Components
| Component | Target | Status |
|---|---|---|
| Frontend | React + TS + Vite on S3 + CloudFront | Local only (Vite dev server, `npm run dev`) |
| Backend API | FastAPI on ECS Fargate behind an ALB | Local only (`uv run uvicorn`, Dockerfile built) |
| Database | RDS PostgreSQL (private) | Local only (`docker compose up -d db`, postgres:16) |
| Auth | Cognito user pool + Google login | Planned (Phase 1) |
| DNS / TLS | Route 53 zone for `taskly.mukundchoudhary.space`, ACM | Planned |
| Secrets | Secrets Manager / SSM | Planned |
| Monitoring | CloudWatch logs and alarms, AWS Budgets | Planned |
| IaC | Terraform, state in S3 | Planned |
| CI/CD | GitHub Actions with OIDC; staging → prod with approval | Planned |

## Environments
| Environment | Frontend URL | API URL | Status |
|---|---|---|---|
| Local | `http://localhost:5173` | `http://localhost:8000` | Working |
| Staging | `staging.taskly.mukundchoudhary.space` | `api.staging.taskly.mukundchoudhary.space` | Not created |
| Prod | `taskly.mukundchoudhary.space` | `api.taskly.mukundchoudhary.space` | Not created |

## API surface
| Group | Endpoint | Description |
|---|---|---|
| health | `GET /health` | Returns API + database status; 200 when healthy, 503 when database unreachable |

The full contract is the generated OpenAPI spec.

## Data model
Alembic initialized with one baseline migration creating no product tables — only Alembic's own `alembic_version` table exists.

## Request flow
_Not deployed yet._ Local flow: browser → Vite dev server (`localhost:5173`) → `fetch` to backend (`localhost:8000/health`) → FastAPI health router → service layer (bounded `asyncio.wait_for`) → repository (`SELECT 1` via async SQLAlchemy engine) → PostgreSQL (compose `db` service).

Target (post-deployment): browser → CloudFront (frontend) → API over HTTPS with a Cognito JWT → FastAPI verifies the token → PostgreSQL.

## Decision log
Record significant decisions here (what, why, alternatives). Decisions already made at planning time are in `.claude/constitution/TECH_STACK.md`.

| Date | Decision | Why | Alternatives considered |
|---|---|---|---|
| 2026-09-28 | Backend on ECS Fargate | Portable container skills; suits future AI workloads | Lambda, EC2, EKS |
| 2026-09-28 | Auth with Cognito | Managed, secure, supports Google login | Build in FastAPI, Auth0, Clerk |
| 2026-09-28 | Terraform for IaC | Multi-cloud, widely used | AWS CDK |
| 2026-09-28 | Recurring tasks stored as rules + per-day completions | Clean edits and streaks | Pre-generating task copies |
| 2026-09-28 | psycopg 3 as the single Postgres driver | One driver for both the app's async engine and Alembic's migration runner | asyncpg (would need a second sync driver for Alembic) |
| 2026-09-28 | Local Postgres via root `docker-compose.yml` | Simple `docker compose up -d db` workflow; credentials match Settings defaults | Separate docker run command, backend compose service |
| 2026-09-28 | Dedicated `HealthCheckResponse` schema for health check | A degraded health check is a successful check reporting an unhealthy dependency, not a failed request | Reusing the generic `{"error": {...}}` envelope |
| 2026-09-28 | `GET /health` unversioned (not under `/api/v1`) | Health/liveness checks are infra convention; future ALB target group needs a stable path | Versioned under `/api/v1/health` |
