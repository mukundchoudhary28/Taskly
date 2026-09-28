# EDD: Skeleton Application (Phase 0)

| | |
|---|---|
| **PRD** | `.claude/specs/phase-00-skeleton-application.md` (Approved) |
| **Phase** | Phase 0 — Minimal deployed version |
| **Status** | Draft |
| **Created** | 2026-09-28 |

Implements the approved PRD's FR-1..FR-10, BR-1/BR-2, and AC-1..AC-11. AWS/Terraform/CI-CD are explicitly out of scope (deferred to a follow-up `phase-00-cloud-deployment` spec), per the PRD's scope note.

## 0. Decisions (confirmed, do not re-litigate)
1. **Postgres driver: psycopg 3**, via SQLAlchemy's `postgresql+psycopg` dialect — one driver for both the app's async engine and Alembic's migration runner, avoiding a second sync-only driver.
2. **Local Postgres:** `docker-compose.yml` at the repo root, service named `db` (so the already-planned `docker compose up -d db` command works unmodified), `postgres:16`, named volume.
3. **`GET /health` is unversioned**, not under `/api/v1`. CLAUDE.md's API design rule puts REST endpoints under `/api/v1`, but health/liveness checks are conventionally left unversioned so infra (a future ALB target group) can point at a stable path. `app/api/v1/` stays empty this phase, reserved for real product endpoints from Phase 1 on.
4. **503 body uses a dedicated `HealthCheckResponse` schema**, not CLAUDE.md's generic `{"error": {"code","message"}}` envelope — justified in §1 (a degraded health check is a successful check reporting an unhealthy dependency, not a failed request).
5. **No frontend test tooling this phase.** AC-3..AC-6 are verified manually (checklist in §7); Vitest + Testing Library are deferred to a later phase, not added now.
6. A default (non-secret) `DATABASE_URL` is baked into `Settings`, matching the compose `db` service's credentials, so bare `uv run uvicorn` works with zero config after `docker compose up -d db`. The containerized path (AC-7) always overrides it explicitly via `-e`.

## 1. Backend structure
New files under `backend/app/`:

| File | Responsibility | Layer |
|---|---|---|
| `app/main.py` | `FastAPI()` instance, CORS config, logging config, includes the health router. No business logic. | composition root |
| `app/core/config.py` | `Settings(BaseSettings)`: `database_url`, `cors_origins`, `health_check_db_timeout_seconds`; `get_settings()` cached via `functools.lru_cache` | `core/` = config |
| `app/core/db.py` | `create_async_engine(settings.database_url)`, `get_engine()` FastAPI dependency; no queries | `core/` = infra plumbing |
| `app/core/logging.py` | `configure_logging()` — structured stdlib logging, called once from `main.py` | `core/` = cross-cutting |
| `app/models/base.py` | `class Base(DeclarativeBase): pass` — empty now; gives Alembic `--autogenerate` metadata to diff against from Phase 1 on | `models/` |
| `app/schemas/health.py` | Pydantic response models (below) | `schemas/` |
| `app/repositories/health.py` | `async def check_database(engine) -> None` — issues `SELECT 1` via the real async engine; raises on failure, no interpretation | `repositories/` = all DB access |
| `app/services/health.py` | `async def get_health_status(engine, timeout) -> HealthCheckResponse` — wraps the repository call in `asyncio.wait_for(timeout=...)`, catches `(TimeoutError, OSError, SQLAlchemyError)`, maps to ok/unreachable, logs the result. No HTTP concepts. | `services/` = business rule |
| `app/api/health.py` | `router = APIRouter()`; `GET /health` calls the service via `Depends`, sets HTTP status (200/503) from the result. No SQL, no timeout logic. | `api/` = HTTP only |

**Response schema** (`app/schemas/health.py`), used for both 200 and 503:
```python
class ComponentStatus(str, Enum):
    OK = "ok"
    UNREACHABLE = "unreachable"

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"

class HealthChecks(BaseModel):
    api: Literal[ComponentStatus.OK] = ComponentStatus.OK
    database: ComponentStatus

class HealthCheckResponse(BaseModel):
    status: HealthStatus
    checks: HealthChecks
    message: str          # fixed, safe string — never raw exception text (BR-1)
    timestamp: datetime   # ISO 8601 UTC
```
- Healthy: HTTP 200, `status="healthy"`, `checks.database="ok"`, `message="API and database are healthy"`.
- Degraded: HTTP 503, `status="degraded"`, `checks.database="unreachable"`, `message="Database is unreachable"` (a fixed constant, never `str(exc)`).

**Bounded timeout (FR-2/AC-11):** `asyncio.wait_for(repo.check_database(engine), timeout=settings.health_check_db_timeout_seconds)` in `services/health.py`. Default `3.0s` (`HEALTH_CHECK_DB_TIMEOUT_SECONDS`), under the 5s NFR ceiling to leave headroom for connection setup.

**No leaked detail (BR-1):** the service catches only `(TimeoutError, OSError, SQLAlchemyError)` — the realistic set of psycopg3/SQLAlchemy connectivity failures — logs `repr(exc)` server-side only, returns the fixed safe message. Deliberately no bare `except Exception:` (violates CLAUDE.md's "no bare except"); a genuinely unexpected exception type should surface as an uncaught 500, not be silently swallowed.

## 2. Dependency additions (flagged per CLAUDE.md's "no new packages without saying why")
From `backend/`:
```
uv add sqlalchemy "psycopg[binary]" alembic pydantic-settings
uv add --dev pytest-asyncio httpx
```

| Package | Why |
|---|---|
| `sqlalchemy>=2.0` | Async engine for the DB check now; ORM/models from Phase 1 on; Alembic's standard companion — already implied by `TECH_STACK.md` ("Migrations: Alembic (with SQLAlchemy)") |
| `psycopg[binary]` | Decision 1: psycopg 3 for both the app and Alembic. `[binary]` ships a prebuilt wheel — avoids needing a `libpq`/build toolchain, notably on Windows dev machines, and keeps the Dockerfile free of `apt-get install libpq-dev` |
| `alembic` | Required directly by FR-9 |
| `pydantic-settings` | Typed, validated env-var config (FastAPI's recommended pattern) instead of raw `os.environ` reads |
| `pytest-asyncio` (dev) | Enables `async def test_...` for direct unit tests of `services/health.py` |
| `httpx` (dev) | FastAPI's `TestClient` requires `httpx` installed separately — not a transitive dependency of `fastapi` |

No AWS/paid services — no recurring cost.

## 3. Database / Alembic setup
1. `cd backend && uv run alembic init -t async alembic` — scaffolds `backend/alembic/{env.py,script.py.mako,versions/}` and `backend/alembic.ini`, using the async template to match the app's own async engine.
2. `alembic.ini`: leave `sqlalchemy.url` blank — never hardcode a DSN in a committed file.
3. `alembic/env.py`: import `get_settings` and `Base`; set `config.set_main_option("sqlalchemy.url", get_settings().database_url)`; `target_metadata = Base.metadata`. Wiring this now (even though `Base.metadata` is empty) is required so `uv run alembic revision --autogenerate -m "msg"` — already listed in CLAUDE.md's planned commands — actually works starting Phase 1.
4. Baseline migration: `uv run alembic revision -m "baseline"` (explicit, **not** `--autogenerate`, to guarantee an intentionally empty migration). `upgrade()`/`downgrade()` bodies are `pass`.
5. **"Creates no tables" (AC-9)** means no *product* tables — Alembic's own `alembic_version` bookkeeping table is unavoidable and doesn't count. Verified via `inspect(engine).get_table_names()` excluding `alembic_version`.
6. Idempotency (AC-9, "no-op second time") is inherent to Alembic — running `upgrade head` when already at head does nothing; verified by running it twice in a test.

## 4. Dockerfile
`backend/Dockerfile` — single-stage (per the PRD's non-goal: no size/perf tuning required):
```dockerfile
FROM python:3.14-slim
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
- `python:3.14-slim` matches `backend/.python-version` exactly.
- `uv sync --frozen --no-dev` installs only production deps, respecting the lockfile without re-resolving.
- `alembic/`/`alembic.ini` copied in for forward-readiness (not required by this phase's ACs, low-cost inclusion).
- `backend/.dockerignore` (new): excludes `.venv/`, `__pycache__/`, `.mypy_cache/`, `.ruff_cache/`, `tests/`, `.git`, `.env`.
- **Connection string only via env var** (`DATABASE_URL`, via `docker run -e`) — satisfies FR-7/AC-7.

## 5. docker-compose.yml (repo root)
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: taskly
      POSTGRES_PASSWORD: taskly
      POSTGRES_DB: taskly_dev
    ports:
      - "5432:5432"
    volumes:
      - taskly_pg_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskly"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  taskly_pg_data:
```
Credentials deliberately match `Settings`'s default DSN so `docker compose up -d db` + `uv run uvicorn app.main:app --reload` works with zero extra config — satisfies AC-8 and US-1's "one or two commands."

**No `backend` service in compose this phase.** Local workflow stays two commands: `docker compose up -d db` (matches CLAUDE.md's already-planned command) + `uv run uvicorn --reload` on the host — hot-reload, no bind-mount complexity. The containerized path (AC-7) is a separate, explicit manual step: `docker build -t taskly-backend backend/` then `docker run --rm -p 8000:8000 -e DATABASE_URL=postgresql+psycopg://taskly:taskly@host.docker.internal:5432/taskly_dev taskly-backend` (note: native Linux Docker may need `--add-host=host.docker.internal:host-gateway` — document this caveat where the command is written down).

## 6. Frontend structure
Scaffold: `npm create vite@latest . -- --template react-ts` inside `frontend/` (remove the placeholder `.gitkeep` first). Confirms "React + TS + Vite"; the template's `tsconfig.app.json` already sets `"strict": true`.

Folders, matching CLAUDE.md's target layout even though only one page exists yet:
```
frontend/src/
  api/
    client.ts     # apiFetch<T>() wrapper — the ONLY fetch in the app
    health.ts     # getHealth(): Promise<HealthCheckResponse>
    types.ts      # HealthCheckResponse TS type mirroring the backend schema
  hooks/
    useHealthCheck.ts   # loading/healthy/degraded/error state machine
  components/
    HealthStatus.tsx    # renders the 4 states as distinct text
  pages/
    HealthPage.tsx      # composes the hook + component
  App.tsx                # renders <HealthPage />
```

**FR-3 vs FR-6 is implemented at the `api/client.ts` boundary:**
- `apiFetch` always attempts to parse the JSON body for both 200 and 503 (both use `HealthCheckResponse`) and does **not** throw on a 503 with a valid, parseable body — that's a successful request reporting a degraded dependency (→ hook state `"degraded"`).
- `apiFetch` throws only on: `fetch` itself rejecting (network/DNS/connection-refused/CORS), a body that fails to parse, or an undocumented status — the hook catches this and sets `"error"`.

`useHealthCheck.ts` state union:
```ts
type HealthState =
  | { kind: "loading" }
  | { kind: "healthy"; data: HealthCheckResponse }
  | { kind: "degraded"; data: HealthCheckResponse }
  | { kind: "error"; message: string };
```

`HealthStatus.tsx` renders four visibly distinct **text** labels (NFR accessibility — not color-only), e.g.: "Checking API health…" / "API: healthy (database connected)" / "API: degraded (database unreachable)" / "API: unreachable (request failed)".

**CORS:** `app/main.py` adds `CORSMiddleware(allow_origins=settings.cors_origins_list, allow_methods=["GET"], allow_headers=["*"], allow_credentials=False)`. `CORS_ORIGINS` defaults to `http://localhost:5173` (Vite's default dev port).

**No new frontend dependencies beyond the Vite react-ts template** — plain `fetch` is sufficient for one GET; no axios/react-query justified. Per the confirmed decision, **no test tooling (Vitest/RTL) is added this phase** — AC-3..AC-6 are verified manually (§7).

## 7. Tests — AC mapping
`backend/pyproject.toml` gets one addition: register an `integration` marker, default-skipped (`markers = ["integration: requires docker compose db running"]`, `addopts = "-m 'not integration'"`), since integration tests need the compose `db` running and there's no CI yet.

| AC | Test | Approach |
|---|---|---|
| AC-1 (healthy) | `backend/tests/test_health.py::test_health_healthy` | Route-level `TestClient` test, `app.dependency_overrides` on the health-service dependency returning success instantly — fast, no real DB |
| AC-1 (BR-2, real path) | `backend/tests/test_health_integration.py::test_health_healthy_real_db` (`@pytest.mark.integration`) | Real engine against the compose `db` — exercises the actual connectivity path, satisfying BR-2 |
| AC-2, BR-1 | `test_health.py::test_health_degraded_no_leak` | DI-override raises the mapped failure; assert HTTP 503, `status=="degraded"`, and the body contains none of the DSN, "Traceback", "psycopg", or raw exception text — only the fixed safe message |
| AC-2 (BR-2, real path) | `test_health_integration.py::test_health_degraded_real_db` (`@pytest.mark.integration`) | Real engine pointed at a connection-refused port (e.g. `127.0.0.1:1`) |
| AC-11 (bounded ≤5s) | `backend/tests/test_health_service.py::test_health_timeout_bounded` | Direct async unit test of `services.health.get_health_status` against a repository stub that hangs forever (`asyncio.sleep(999)`), with `timeout` overridden small (e.g. `0.2s`); assert result is `"unreachable"` and elapsed time tracks the override, not the hang — fast, deterministic |
| AC-9 | `backend/tests/test_migrations.py` (`@pytest.mark.integration`) | Alembic's Python API (`command.upgrade(cfg, "head")` twice) against the compose `db`; assert `inspect(engine).get_table_names()` contains only `alembic_version` |
| AC-10 | Manual checklist | Run the actual CLAUDE.md commands (`uv sync`, `uv run uvicorn ...`, `uv run pytest`, `uv run ruff check . && uv run ruff format .`, `uv run mypy app`, `npm install`, `npm run dev`, `npm run build`, `npm run lint`) and confirm exit code 0 — no CI exists yet to automate this. **Note:** `npm test` from CLAUDE.md's planned commands has no test runner installed this phase (decision 5) — flag this as a correction to make when frontend tests are eventually added. |
| AC-3 | Manual checklist | Load the page with the backend not yet started (or `fetch` artificially delayed); confirm a loading state is visibly shown before any result |
| AC-4 | Manual checklist | With `docker compose up -d db` running and the backend healthy, load the page; confirm the healthy state renders |
| AC-5 | Manual checklist | Stop the `db` container, reload the page; confirm the degraded state renders, visibly different from healthy |
| AC-6 | Manual checklist | Stop the backend entirely, reload the page; confirm the error state renders, visibly different from both healthy and degraded |
| AC-7 | Manual checklist | `docker build` + `docker run -e DATABASE_URL=...` (§4); curl `/health`, confirm it responds without further setup |
| AC-8 | Manual checklist | `docker compose up -d db`; confirm `localhost:5432` is reachable (e.g. `pg_isready`) |

## 8. Config / secrets handling
`backend/app/core/config.py`:
```python
class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://taskly:taskly@localhost:5432/taskly_dev"
    cors_origins: str = "http://localhost:5173"
    health_check_db_timeout_seconds: float = 3.0
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
```

`backend/.env.example` (new — already allowlisted by root `.gitignore`'s `!.env.example`):
```
DATABASE_URL=postgresql+psycopg://taskly:taskly@localhost:5432/taskly_dev
CORS_ORIGINS=http://localhost:5173
HEALTH_CHECK_DB_TIMEOUT_SECONDS=3.0
```

`frontend/.env.example`:
```
VITE_API_BASE_URL=http://localhost:8000
```

| Mode | Config source |
|---|---|
| Bare `uv run uvicorn` on host | `Settings` default (matches compose `db` creds) or `backend/.env` copied from `.env.example` |
| `docker compose up -d db` + host uvicorn | Same — port 5432 exposed to `localhost` |
| Standalone container (AC-7) | No `.env` in the image (excluded via `.dockerignore`); `DATABASE_URL` passed via `docker run -e` |

No `.env` is ever committed; `.env.example` is the only committed template in both `backend/` and `frontend/`.

## 9. Rollout / build order
1. Backend deps: `uv add sqlalchemy "psycopg[binary]" alembic pydantic-settings`; `uv add --dev pytest-asyncio httpx`.
2. `app/core/config.py` + `backend/.env.example`.
3. `app/core/db.py` + `app/models/base.py`.
4. `app/repositories/health.py` + `app/services/health.py` + `app/schemas/health.py`.
5. `app/api/health.py` + `app/main.py` (CORS, logging, router) — runnable via `uv run uvicorn app.main:app --reload` against a manually-started Postgres.
6. `backend/tests/conftest.py` + `test_health.py` + `test_health_service.py` — `uv run pytest` green (excluding `integration`-marked tests).
7. `backend/alembic/` init + `env.py` wiring + baseline migration + `test_migrations.py`.
8. `backend/Dockerfile` + `backend/.dockerignore` — verify AC-7 manually.
9. Root `docker-compose.yml` — verify AC-8.
10. `backend/tests/test_health_integration.py` (now that `db` exists to test against) — `uv run pytest -m integration` green.
11. Frontend scaffold + folder structure + `frontend/.env.example`.
12. `frontend/src/api/{client,health,types}.ts`.
13. `frontend/src/hooks/useHealthCheck.ts` + `components/HealthStatus.tsx` + `pages/HealthPage.tsx` + `App.tsx`.
14. Manual `npm run dev`/`lint`/`build`; manual AC-3..AC-6 checklist (§7).
15. Full manual AC-1..AC-11 verification pass.
16. Docs: `.claude/docs/CHANGELOG.md`, `.claude/docs/PROJECT_STATUS.md`, `.claude/docs/ARCHITECTURE.md` — final commit, same PR (see §10 for exact bullets).

## 10. Doc updates (for the implementation PR, not this EDD)
**`.claude/docs/CHANGELOG.md`** — add under `[Unreleased] → Added`:
- FastAPI app (`backend/app/main.py`) with `GET /health` reporting API and database status; bounded DB timeout (default 3s); structured logging of each result; no internal error detail leaked on DB failure (BR-1)
- Backend config via `pydantic-settings` (`app/core/config.py`); `backend/.env.example`
- Async SQLAlchemy engine (`app/core/db.py`) using the `postgresql+psycopg` (psycopg 3) dialect for both the app and Alembic
- Alembic initialized (`backend/alembic/`, async template) with an empty baseline migration creating no product tables
- `backend/Dockerfile` and `backend/.dockerignore` — backend buildable/runnable as a container with only `DATABASE_URL` supplied
- Root `docker-compose.yml` with a `db` service (`postgres:16`, named volume, healthcheck)
- Frontend scaffolded with Vite + React + TypeScript; `src/api/`, `src/pages/`, `src/components/`, `src/hooks/` structure; single `HealthPage` showing loading/healthy/degraded/error states, distinguished by text

**`.claude/docs/PROJECT_STATUS.md`** — flip to `[x]` under `phase-00-skeleton-application`: the `GET /health` item, Dockerfile, local Postgres, Alembic baseline, and the React health page. Remove the now-resolved "Async Postgres driver" open question. Update "Done recently"/"Next up" to note the skeleton is built and verified, and that `phase-00-cloud-deployment` is the next spec to write.

**`.claude/docs/ARCHITECTURE.md`**:
- Current state: describe the backend/frontend running locally and in containers, `GET /health` checking API+DB with a bounded timeout and no leaked detail, local Postgres via compose, Alembic initialized with an empty baseline — still not deployed to AWS.
- Components table: Backend API, Database, Frontend rows → `Local only (not yet deployed)` with a short parenthetical.
- API surface: one row — `GET /health` — group `health` — "Returns API + database status; 200 when healthy, 503 when database unreachable."
- Data model: "Alembic initialized with one baseline migration creating no product tables — only Alembic's own `alembic_version` table exists."
- Decision log: add rows for psycopg 3, local Postgres via root `docker-compose.yml`, the dedicated health-check schema, and the unversioned `/health` path — each with why + alternatives considered.

## Revision history
| Date | Change |
|---|---|
| 2026-09-28 | EDD created against the approved PRD |
