# PRD: Skeleton Application

| | |
|---|---|
| **Phase** | Phase 0 — Minimal deployed version (see `.claude/constitution/ROADMAP.md`) |
| **Status** | Approved |
| **Owner** | Shubham Choudhary |
| **Created** | 2026-09-28 |
| **Last updated** | 2026-09-28 |
| **Related specs** | None |
| **EDD** | `.claude/specs/phase-00-skeleton-application-edd.md` (once written) |

> **Scope note:** `ROADMAP.md`'s Phase 0 bundles the app skeleton together with the full AWS stack and CI/CD into one scope and one DoD. This spec deliberately covers only the local, containerized half — the running app. The AWS infrastructure, GitHub Actions CI/CD and going live on `taskly.mukundchoudhary.space` are deferred to a follow-up spec (working name `phase-00-cloud-deployment`). Phase 0 in `ROADMAP.md` is only "Done" once both specs ship. See Open questions.

## 1. Summary
A buildable, containerized skeleton of Taskly: a FastAPI backend with a health check that also reports on the database connection, and a React + TypeScript + Vite page that calls it and shows the result. This is the first deployable increment of Phase 0 — proving the backend and frontend run and talk to each other, with a local database and migration tooling in place, before any cloud infrastructure is built on top of it.

## 2. Problem and why now
The monorepo currently has an empty, uv-managed `backend/` project and no frontend or running code — there is nothing to run, test or containerize. `ROADMAP.md`'s Phase 0 goal is "a trivial app running end to end on AWS, deployed only through CI/CD." Building and proving the app skeleton locally first means the infrastructure work that follows (Terraform, ECS, CI/CD) deploys something real, and problems in the app itself (startup, DB connectivity, container build) are caught without needing AWS access.

## 3. Goals
- A FastAPI backend that runs locally and in a container, exposing a health check that reports both API and database status.
- A React + TS + Vite page that calls the health check and displays the result to a visitor.
- A local PostgreSQL database a developer can start with one documented command.
- Alembic installed and initialized with an empty baseline migration.
- Working, documented local commands for both backend and frontend: install, run, lint, type-check (backend).

## 4. Non-goals
- Not deployed anywhere. No AWS resources, no Terraform, no live URL — that is the follow-up `phase-00-cloud-deployment` spec.
- No CI/CD pipeline.
- No user accounts, authentication, tasks or any product feature. The frontend's only job here is showing the health result.
- No Dockerfile performance/size tuning beyond building and running correctly.

## 5. User stories
- **US-1:** As a developer, I want to run the whole stack locally with one or two commands, so that I can verify the app works before pushing.
- **US-2:** As a developer, I want a frontend page that visibly confirms the backend and database are reachable, so that I have a quick end-to-end signal the stack is wired up correctly.
- **US-3:** As an on-call engineer (future), I want the health check to fail loudly and distinctly when the database is down, so that monitoring can alert on it once deployed.

## 6. Functional requirements
| ID | Requirement | Priority |
|---|---|---|
| FR-1 | The system shall expose a health check that reports whether the API is running. | Must |
| FR-2 | The health check shall also report whether the database connection is working, as part of the same check. | Must |
| FR-3 | The health check shall return a response that clearly distinguishes "API up, database reachable" from "API up, database unreachable." | Must |
| FR-4 | The system shall provide a single web page that calls the health check and displays its result to a visitor. | Must |
| FR-5 | The web page shall show a loading state while the health check is in flight. | Must |
| FR-6 | The web page shall show a distinct error state if the health check request fails outright (e.g. the API is unreachable from the browser). | Must |
| FR-7 | The backend shall be packaged as a container image that can be built and run with no machine-specific setup beyond a container runtime. | Must |
| FR-8 | The system shall provide a documented way to run a local PostgreSQL database for development, independent of any cloud database. | Must |
| FR-9 | The system shall have database migration tooling installed and initialized, including a first migration that establishes an empty baseline (no tables). | Must |
| FR-10 | The backend and frontend shall each have documented, repeatable local commands to install dependencies and run in development mode; the backend shall also have working lint and type-check commands. | Must |

## 7. Business rules
| ID | Rule | Source |
|---|---|---|
| BR-1 | The health check's response must not expose internal error detail (e.g. raw driver exceptions, connection strings, stack traces) — only a status and a safe message. | Decided in this spec, extending `CLAUDE.md`'s "never log tokens, passwords or personal data" principle to error responses |
| BR-2 | The health check's database check must use the same connectivity path the rest of the application will use — no mocked or special-cased check — so a failure here reflects a real outage. | Decided in this spec |

## 8. User experience
- **Where it appears:** a single page — the only page in the frontend at this stage.
- **Main flow:** the page loads, immediately calls the health check, shows a loading state, then shows either a healthy result or an error/unhealthy result.
- **States:**
  - *Loading:* shown from page load until the health check responds.
  - *Healthy:* API and database both reachable.
  - *Degraded:* API reachable, database unreachable (FR-3).
  - *Error:* the health check request itself failed (e.g. network error, API unreachable) — distinct from "degraded" (FR-6).
- **Mobile:** the page is legible and usable at phone width; no layout-specific behaviour needed at this stage beyond not being broken.
- **Copy:** plain-language status text (e.g. "API: healthy", "API: database unreachable", "API: unreachable") — exact wording decided in the EDD/implementation, not prescribed here.

## 9. Edge cases
| Case | Expected behaviour |
|---|---|
| Database unreachable when the health check runs | Response reports the degraded state (BR-1, FR-3); no crash, no leaked internal detail |
| Database does not respond at all (hangs) | The health check does not hang indefinitely — treated as unreachable after a bounded wait (see NFR performance) |
| Frontend loaded before the backend has started | Health check request fails outright; page shows the error state (FR-6), not a blank or stuck loading state |
| Migration tool run against a fresh database | Completes successfully, creates no tables |
| Migration tool run a second time with no new migrations | No-op; completes without error |
| Container image built and run with no `.env` or local Python/Node setup present | Backend still starts and serves the health check, given only a container runtime and (for FR-2) a reachable database connection string supplied to the container |

## 10. Non-functional requirements
- **Security and privacy:** health check response contains no secrets, credentials or stack traces (BR-1). No personal data is involved at this stage.
- **Performance:** the health check responds within 5 seconds even when the database is unreachable or not responding — it must not hang indefinitely.
- **Accessibility:** the page's health/degraded/error states are conveyed through text, not colour alone.
- **Observability:** each health check result (status, database check outcome) is logged by the backend in structured form, with no secrets or personal data, per `CLAUDE.md`'s logging rule.
- **Cost:** None. Everything in this spec runs locally and in containers; no AWS resources are created.

## 11. Acceptance criteria
| ID | Covers | Given / When / Then |
|---|---|---|
| AC-1 | FR-1, FR-2, FR-3 | **Given** the backend is running with a reachable database, **When** a client requests the health check, **Then** the response reports the API as running and the database as connected. |
| AC-2 | FR-2, FR-3, BR-1 | **Given** the backend is running but the database is unreachable, **When** a client requests the health check, **Then** the response reports the database as unreachable and contains no internal error detail beyond a safe status message. |
| AC-3 | FR-4, FR-5 | **Given** the frontend page is loaded, **When** it is waiting on the health check, **Then** it shows a loading state before any result appears. |
| AC-4 | FR-4 | **Given** the backend reports healthy, **When** the frontend's health check completes, **Then** the page displays the healthy result. |
| AC-5 | FR-4, FR-3 | **Given** the backend reports the database as unreachable, **When** the frontend's health check completes, **Then** the page displays the degraded result, visibly different from the healthy result. |
| AC-6 | FR-6 | **Given** the backend is unreachable from the browser, **When** the frontend's health check request fails outright, **Then** the page displays an error state, visibly different from both the healthy and degraded results. |
| AC-7 | FR-7 | **Given** a machine with only a container runtime installed, **When** the backend's container image is built and run with a database connection string supplied, **Then** the health check responds without any further manual setup. |
| AC-8 | FR-8 | **Given** a developer runs the documented local-database command, **When** it completes, **Then** a PostgreSQL instance is reachable locally for the backend to connect to. |
| AC-9 | FR-9 | **Given** a fresh local database, **When** the migration tool is run to the latest migration, **Then** it completes successfully, creates no tables, and running it again is a no-op. |
| AC-10 | FR-10 | **Given** a clean checkout, **When** the documented backend and frontend install/run/lint/type-check commands are run, **Then** each completes without configuration errors. |
| AC-11 | NFR performance | **Given** the database does not respond, **When** the health check runs, **Then** it returns within 5 seconds rather than hanging. |

## 12. Dependencies and assumptions
- **Depends on:** the monorepo scaffold and `backend/` uv project already committed to `main`.
- **Assumptions:** a container runtime (e.g. Docker) is available on the developer's machine for the local database and image builds; Node.js/npm is available for the frontend; no AWS account access is required for anything in this spec.

## 13. Out of scope / future
- All AWS infrastructure: VPC, ECS Fargate, ALB, RDS, S3 + CloudFront, Route 53, ACM, CloudWatch, Budgets — `phase-00-cloud-deployment` (or similarly named follow-up spec).
- GitHub Actions CI/CD, OIDC login to AWS, staging/prod pipelines — same follow-up spec.
- NS records at the domain registrar — same follow-up spec.
- Authentication, tasks, or any feature from Phase 1 onward.

## 14. Open questions
| # | Question | Recommended answer | Status |
|---|---|---|---|
| 1 | Exact name/slug for the follow-up spec covering AWS infra + CI/CD | `phase-00-cloud-deployment` | Resolved — use `phase-00-cloud-deployment` |
| 2 | Whether `ROADMAP.md`'s Phase 0 entry should be split in the roadmap itself (e.g. 0a/0b) to reflect two specs, or stay as one entry delivered by two specs | Keep `ROADMAP.md` as a single Phase 0 entry; track the two-spec delivery in `.claude/docs/PROJECT_STATUS.md` only, since `ROADMAP.md` changes need explicit approval | Resolved — `ROADMAP.md` stays as is |

## 15. Definition of done
- All acceptance criteria (AC-1 – AC-11) pass locally, including in the containerized backend.
- This spec does **not** by itself satisfy `ROADMAP.md`'s Phase 0 DoD (which requires the site live over HTTPS on AWS) — that requires the follow-up `phase-00-cloud-deployment` spec as well.
- `.claude/docs/CHANGELOG.md`, `.claude/docs/PROJECT_STATUS.md` and `.claude/docs/ARCHITECTURE.md` are updated.

## Revision history
| Date | Change |
|---|---|
| 2026-09-28 | Draft created |
| 2026-09-28 | Approved. Open questions resolved: follow-up infra spec named `phase-00-cloud-deployment`; `ROADMAP.md` kept as is. |
