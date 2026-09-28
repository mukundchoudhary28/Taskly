# Taskly — Roadmap

We build Taskly the way software companies do: **ship a minimal deployed version first, then add one feature at a time.** Every phase ends with the change **merged, deployed to staging, tested and promoted to prod.**

Each phase lists its **goal**, **scope** and **definition of done (DoD)**.

---

## Phase 0: Minimal deployed version
**Goal:** a trivial app running end to end on AWS, deployed only through CI/CD.

**Scope**
- Monorepo layout (`frontend/`, `backend/`, `infra/`, `.github/workflows/`), with project docs under `.claude/` (`constitution/`, `docs/`, `specs/`)
- FastAPI `GET /health` that also checks the database connection; Dockerfile; uv project
- A React + TS + Vite page that calls `/health` and shows the result
- Terraform:
  - S3 bucket for Terraform's own state
  - VPC (public and private subnets, **no NAT gateway**), security groups
  - ECR, ECS cluster and service (Fargate), Application Load Balancer
  - RDS PostgreSQL (private)
  - S3 + CloudFront for the frontend
  - Route 53 zone for `taskly.mukundchoudhary.space`, ACM certificates
  - CloudWatch log groups, AWS Budgets alerts
- NS records for `taskly.` added at the domain registrar
- GitHub Actions:
  - CI: lint, type-check and test the backend and frontend
  - CD: build the image → push to ECR → deploy to ECS; build the frontend → upload to S3 → clear the CloudFront cache
  - OIDC login to AWS; manual approval step before prod
- Alembic set up with an empty first migration

**DoD:** `https://taskly.mukundchoudhary.space` loads over HTTPS and shows "API: healthy". A merge to `main` deploys to staging automatically, and prod deploys after approval.

---

## Phase 1: Authentication
**Goal:** users can sign up and sign in.

**Scope**
- Cognito user pool (in Terraform): email + password, email verification, password reset
- Custom sign-up, sign-in and forgot-password screens in React
- FastAPI: JWT verification, a `users` table, create the user on first login (from the token's `sub`), and a `GET /me` endpoint
- Capture the user's timezone from the browser and store it
- Add Google as a login option in Cognito; "Continue with Google" button

**DoD:** a new user can sign up with email or Google, log in, log out and reset their password. Protected endpoints reject requests without a valid token.

---

## Phase 2: Core tasks
**Goal:** basic to-do list for today.

**Scope**
- `tasks` table and migration
- API: create, list for a date, update, delete, and tick/untick
- UI: today's list with checkboxes, add a task (title + notes), edit, delete
- Every query checks the task belongs to the current user

**DoD:** a user can manage today's tasks, and they are still there after refreshing or logging in again.

---

## Phase 3: Dates
**Goal:** view and plan any day.

**Scope**
- Date picker
- Future dates: add and manage tasks
- Past dates: tick, untick, edit and delete one-off tasks; creating new ones is blocked (in both the API and the UI)
- "Today" worked out in the user's timezone

**DoD:** a user can plan tomorrow's tasks, and the past-date rules are enforced by the API, not just hidden in the UI.

---

## Phase 4: Priority and ordering
**Goal:** a prioritised, reorderable list.

**Scope**
- `priority` and `position` fields
- UI groups: High → Medium → Low
- Drag to reorder within a group; dragging into another group changes the priority
- A reorder endpoint that saves positions in one database transaction

**DoD:** the order and priorities a user sets are kept across sessions and devices.

---

## Phase 5: Carry-over
**Goal:** the user sees and acts on unfinished work.

**Scope**
- A "Pending from the last 7 days" section in a different color
- A "Move to today" action that sets `original_date` and moves the task to today
- A "Moved from earlier" section pinned to the top with an "Originally <date>" badge
- A moved task that is still unfinished shows as pending again the next day and keeps its badge

**DoD:** the home page shows all three sections in the right order, following the rules in MISSION.md.

---

## Phase 6: Recurring tasks
**Goal:** tasks that repeat.

**Scope**
- `recurring_rules` and `occurrence_completions` tables
- Patterns: daily, weekdays, weekly on chosen days
- Each day's occurrences are worked out when a day is viewed and appear in the today and date views
- Ticking allowed only on the occurrence's own day, locked after the user's midnight (enforced by the API)
- Missed occurrences are not carried forward
- Edit the pattern; delete the series

**DoD:** a "weekly Mon/Wed/Fri" task appears only on those days, can only be ticked on the day, and never shows up in the pending section.

---

## Phase 7: Streaks
**Goal:** reward consistency.

**Scope**
- Streak calculation: completed scheduled occurrences in a row; days the task isn't scheduled don't count; today's open occurrence doesn't break it
- Current and best streak for each rule
- A streak cards view (one card per recurring task)
- Edits to the pattern keep the streak; deleting the series removes its history

**DoD:** streak numbers match a set of test cases (missed day, day not scheduled, pattern edit, timezone near midnight).

---

## Phase 8: Hardening
**Goal:** confidence to run it for real.

**Scope**
- Better test coverage: backend unit and integration tests against a real Postgres; frontend component tests; a few end-to-end tests (e.g. Playwright)
- CloudWatch alarms: 5xx rate, ECS task restarts, RDS CPU and storage; notifications sent by email
- Structured JSON logs with request IDs
- A tested **backup and restore drill** for RDS
- A basic load test
- Rate limiting and security headers
- Write-up of each technology decision in `.claude/docs/`

**DoD:** alarms have been triggered on purpose and received; the database has been restored from a backup; the load test results are written down.

---

## Later (v1 / v2)
- Reminders and notifications (email with SES, or push)
- Billing and plans
- Installable app (PWA) or a mobile app
- Shared lists and collaboration
- Stats and history dashboard

---

## Working agreements
- **Branching:** short-lived feature branches → pull request → CI must pass → merge to `main`
- **Every phase ends deployed to prod.** Nothing is deployed by hand.
- **Infrastructure changes go through Terraform only.** Never make changes in the AWS console.
- **Database changes go through Alembic migrations only**, run as a step in the pipeline
- **Check the AWS bill weekly** against the budget alerts
