# Changelog

All notable changes to Taskly are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

**How to update:** add entries under `[Unreleased]` in the same PR as the change, using the sections Added / Changed / Fixed / Removed / Security. When a release goes to prod, rename `[Unreleased]` to the version and date, and start a new empty `[Unreleased]`.

## [Unreleased]

### Added
- Monorepo layout: `backend/`, `frontend/`, `infra/modules/`, `infra/envs/{staging,prod}/`, `.github/workflows/`, root `.gitignore`
- `backend/` uv project (Python 3.14): FastAPI + Uvicorn; dev tools pytest, ruff, mypy (strict); empty `app/` layers (`api/v1`, `services`, `repositories`, `models`, `schemas`, `core`) and `tests/`
- Project constitution: `MISSION.md`, `TECH_STACK.md`, `ROADMAP.md`
- `CLAUDE.md` with working agreements, architecture principles and API design rules
- Living docs: `docs/ARCHITECTURE.md`, `docs/CHANGELOG.md`, `docs/PROJECT_STATUS.md`

- `create-spec` project skill (`.claude/skills/create-spec/`) with a PRD template, and a `specs/` folder for PRDs and EDDs
- `phase-00-skeleton-application` PRD (`.claude/specs/phase-00-skeleton-application.md`, Approved): scopes the local, containerized app skeleton — FastAPI `GET /health` with a database check, a React page showing the result, a local Postgres, and Alembic initialized with an empty baseline migration. Splits `ROADMAP.md`'s Phase 0 into this spec plus a follow-up `phase-00-cloud-deployment` spec (AWS infra + CI/CD); `ROADMAP.md` itself is unchanged
- FastAPI app (`backend/app/main.py`) with `GET /health` reporting API and database status; bounded DB timeout (default 3s); structured logging of each result; no internal error detail leaked on DB failure (BR-1)
- Backend config via `pydantic-settings` (`app/core/config.py`); `backend/.env.example`
- Async SQLAlchemy engine (`app/core/db.py`) using the `postgresql+psycopg` (psycopg 3) dialect for both the app and Alembic
- Alembic initialized (`backend/alembic/`, async template) with an empty baseline migration creating no product tables
- `backend/Dockerfile` and `backend/.dockerignore` — backend buildable/runnable as a container with only `DATABASE_URL` supplied
- Root `docker-compose.yml` with a `db` service (`postgres:16`, named volume, healthcheck)
- Frontend scaffolded with Vite + React + TypeScript; `src/api/`, `src/pages/`, `src/components/`, `src/hooks/` structure; single `HealthPage` showing loading/healthy/degraded/error states, distinguished by text
- Backend unit tests (`test_health.py`, `test_health_service.py`) and integration tests (`test_health_integration.py`, `test_migrations.py`) covering AC-1, AC-2, AC-9, AC-11

### Changed
- Project docs stay under `.claude/` (`CLAUDE.md`, `constitution/`, `docs/`, `specs/`, `skills/`). Path references in `CLAUDE.md`, `TECH_STACK.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md` and the `create-spec` skill now say `.claude/...`
- `CLAUDE.md`: added the feature flow (PRD → plan mode → EDD → build) and the `specs/` folder
- `create-spec` skill now checks for a clean working tree, parses `<phase> <name>`, creates a `feat/phase-NN-<slug>` branch from an up-to-date `main`, pre-approves only the tools it needs, and ends with a completion report
- Restructured `CLAUDE.md`: added repo map with "where things belong", code style, tech constraints, subagent policy, planned commands, and a warnings section
