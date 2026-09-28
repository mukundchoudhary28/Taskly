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

### Changed
- Project docs stay under `.claude/` (`CLAUDE.md`, `constitution/`, `docs/`, `specs/`, `skills/`). Path references in `CLAUDE.md`, `TECH_STACK.md`, `ROADMAP.md`, `docs/ARCHITECTURE.md` and the `create-spec` skill now say `.claude/...`
- `CLAUDE.md`: added the feature flow (PRD → plan mode → EDD → build) and the `specs/` folder
- `create-spec` skill now checks for a clean working tree, parses `<phase> <name>`, creates a `feat/phase-NN-<slug>` branch from an up-to-date `main`, pre-approves only the tools it needs, and ends with a completion report
- Restructured `CLAUDE.md`: added repo map with "where things belong", code style, tech constraints, subagent policy, planned commands, and a warnings section
