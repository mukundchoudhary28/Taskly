# CLAUDE.md — Taskly

## Project overview
- Taskly is a daily to-do web app: tasks for today, carry-over from the last 7 days, and recurring tasks with streaks.
- It is a **production-grade learning project**. The app is small on purpose; the real goal is to build auth, database, AWS deployment, Terraform, CI/CD and monitoring the way a software company would.
- Live at `taskly.mukundchoudhary.space` (prod) and `staging.taskly.mukundchoudhary.space` (staging) once Phase 0 ships.

## Source of truth
| File | Holds | Can Claude change it? |
|---|---|---|
| `.claude/constitution/MISSION.md` | Scope and feature rules | Only with approval |
| `.claude/constitution/TECH_STACK.md` | Target architecture, decisions, data model | Only with approval |
| `.claude/constitution/ROADMAP.md` | Phases and definition of done | Only with approval |
| `.claude/docs/PROJECT_STATUS.md` | Current phase, next steps, blockers | Yes, keep current |
| `.claude/docs/ARCHITECTURE.md` | What is actually built | Yes, keep current |
| `.claude/docs/CHANGELOG.md` | What changed | Yes, keep current |

- **Start every session by reading `.claude/docs/PROJECT_STATUS.md`.**
- If the code and the constitution disagree, stop and ask. Don't "fix" either one silently.

## Architecture
Monorepo (folders are created in Phase 0 — don't assume anything exists until `ARCHITECTURE.md` says it does):
- `backend/app/api/v1/` — FastAPI routers (HTTP only)
- `backend/app/services/` — business rules (dates, carry-over, recurrence, streaks)
- `backend/app/repositories/` — database access
- `backend/app/models/` — SQLAlchemy models · `backend/app/schemas/` — Pydantic request/response models
- `backend/app/core/` — config, auth (Cognito JWT), time helpers
- `backend/alembic/` — migrations · `backend/tests/` — tests
- `frontend/src/api/` — typed API client · `pages/` · `components/` · `hooks/`
- `infra/modules/` — Terraform modules · `infra/envs/{staging,prod}/` — environments
- `.github/workflows/` — CI/CD
- `.claude/specs/` — PRDs (`phase-NN-<slug>.md`) and implementation plans (`phase-NN-<slug>-edd.md`)
- `.claude/skills/` — project skills (e.g. `create-spec`)

**Where things belong:**
- Routers parse the request, call a service, return a schema. No SQL and no business rules in routers.
- Business rules → services, as pure functions where possible. No HTTP concepts in services.
- DB queries → repositories only. Every query is scoped to the current user.
- "What day is it for this user" → one helper in `core/`. Never compute it anywhere else.
- Frontend calls the API only through `src/api/`. No `fetch` inside components.
- Any AWS resource → Terraform in `infra/`. Never the console.

## API design
- REST + JSON under `/api/v1`. Plural nouns (`/tasks`, `/recurring-rules`); non-CRUD actions as sub-resources (`POST /tasks/{id}/move-to-today`).
- Status codes: 201 create, 204 delete, 401 no/invalid token, 404 for missing *or someone else's* data, 409 conflict, 422 validation.
- One error shape: `{"error": {"code": "...", "message": "..."}}`.
- Dates as `YYYY-MM-DD`; timestamps ISO 8601 in UTC.
- Feature rules (past-date edits, occurrence locking) are enforced by the API, not just hidden in the UI.
- The generated OpenAPI spec is the contract. Breaking changes need a new version or an agreed plan.

## Code style
- Python: typed, PEP 8, formatted and linted; snake_case. Async where FastAPI and the DB driver support it.
- TypeScript: `strict` mode; no `any` without a comment explaining why.
- SQL only through SQLAlchemy / parameterised queries — never string-built SQL.
- Errors: raise explicit HTTP errors from routers and domain errors from services. No bare `except`, no swallowed errors.
- Logs are structured; never log tokens, passwords or personal data.

## Tech constraints
- Stack is fixed by `.claude/constitution/TECH_STACK.md`: FastAPI, React + TS + Vite, PostgreSQL, Cognito, ECS Fargate, Terraform, GitHub Actions.
- **No new packages or AWS services** without flagging it first and saying why.
- Python packages via **uv** only.
- Flag any change that adds a recurring AWS cost (budget is the free tier + $100 credit).

## Workflow
- Work one roadmap phase at a time. **Don't build anything from a later phase** unless the current task targets it.
- **Feature flow:** `/create-spec <phase> <name>` (creates the `feat/` branch and PRD) → approved PRD in `.claude/specs/` → plan mode produces the EDD → build against the PRD's acceptance criteria → one PR. No feature code without an approved PRD.
- For small fixes, plan briefly (files, migrations, infra) and get a go-ahead.
- Explain the *why* when introducing a tool or pattern — this is a learning project.
- Branch (`feat/ fix/ infra/ chore/ docs/`) → PR → CI green → merge → staging → approved prod deploy. Conventional commits.
- **Docs are part of every change.** After each commit that changes behaviour, infra or structure: add to `.claude/docs/CHANGELOG.md` under `[Unreleased]`, update `.claude/docs/PROJECT_STATUS.md`, and update `.claude/docs/ARCHITECTURE.md` if a component, endpoint group, table or AWS resource changed. Not done until the docs are updated in the same PR.

## Subagent policy
- Use an Explore subagent to survey the codebase before planning or implementing a feature.
- Use a Plan subagent in plan mode.
- After implementing, use a separate subagent to run the tests and review the change against the phase's definition of done.

## Commands
Planned — confirm and correct these in Phase 0.
- Backend: `uv sync` · `uv run uvicorn app.main:app --reload` · `uv run pytest` · `uv run ruff check . && uv run ruff format .` · `uv run mypy app`
- Migrations: `uv run alembic revision --autogenerate -m "msg"` · `uv run alembic upgrade head`
- Local DB: `docker compose up -d db`
- Frontend: `npm install` · `npm run dev` · `npm run build` · `npm run lint` · `npm test`
- Infra: `terraform -chdir=infra/envs/staging init|plan|apply`

## Warnings and things to avoid
- Never use the server's clock or `date.today()` for "today" — use the user's timezone helper. Never store naive datetimes.
- Never take `user_id` from the request body or query — only from the verified token.
- Never edit a migration that has already run anywhere; write a new one.
- Never `terraform apply` without reviewing the plan; never commit `.tfstate`, `.env` or secrets.
- No NAT gateway, no public RDS — both are cost/security traps here.
- The CloudFront certificate must be in `us-east-1`, whatever region the rest runs in.
- Verify Cognito tokens fully: signature, expiry, issuer, audience/client id and `token_use`.
- Don't weaken a rule from `MISSION.md` to make an implementation easier — ask instead.
