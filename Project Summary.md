Taskly: Final Summary

What it is: a production-grade daily to-do app, built for learning and your portfolio, the way a software company would build it. No billing in the MVP.

Features (MVP)

Accounts

Sign up with name, email and password, or with Google (Amazon Cognito)
Each user's timezone is stored, and "today" and midnight follow the user's own time

Tasks

Each task has a title, optional notes and a priority (High / Medium / Low), plus a checkbox to mark it done
Home page is today's list, in this order:
Moved from earlier: pinned at the top, with an "Originally Sep 26" badge
Today's tasks, grouped by priority. Dragging reorders within a group; dragging into another group changes the priority.
Pending from the last 7 days: shown in a different color, each with a "Move to today" action
A moved task that is still unfinished shows as pending again the next day and keeps its original-date badge
A date picker lets users plan future days and view past ones
Past one-off tasks can be ticked, edited and deleted. New tasks can't be created on past dates.

Recurring tasks and streaks

Patterns: daily, weekdays, or weekly on chosen days
Missed occurrences are not carried forward; a miss resets the streak
An occurrence can only be ticked on its own day, then it locks
The streak counts completed scheduled occurrences in a row, so days the task isn't scheduled never break it
Each recurring task gets a card showing its current streak and best streak
Editing the pattern keeps the streak; deleting the series removes its history

Later (v1/v2): reminders and notifications, billing.

Architecture
Layer	Choice
Frontend	React + TypeScript + Vite, served from S3 through CloudFront
Backend	FastAPI in Docker, running on ECS Fargate behind a load balancer, using uv for Python packages
Database	RDS PostgreSQL, with schema changes managed by Alembic migrations
Auth	Cognito user pool with Google login; FastAPI checks the login tokens Cognito issues
DNS / HTTPS	A Route 53 zone for taskly.mukundchoudhary.space with free HTTPS certificates from ACM
Secrets	AWS Secrets Manager or SSM Parameter Store
Monitoring	CloudWatch logs, metrics and alarms, plus AWS Budgets alerts
Infrastructure as code	Terraform, with its state stored in S3
CI/CD	GitHub Actions, logging into AWS without stored keys (OIDC). Merges auto-deploy to staging; prod deploys after approval.
Environments	Staging (created on demand, torn down after) and prod

Data model (sketch): users → tasks (a date, priority, position, done time, original date if moved) and recurring_rules (the pattern and chosen days) → occurrence_completions (one row per rule per day completed). Streaks are calculated from the rule's schedule and its completions.

Build order: one deployable increment at a time
Minimal deployed version: a monorepo with a "hello world" React page, a FastAPI health check and a database connection, running on AWS through Terraform and GitHub Actions, served over HTTPS on your subdomain, with logs and budget alerts
Auth: Cognito email sign-up and login, then Google
Core tasks: create, tick, edit and delete tasks for today
Dates: the date picker, planning future days, and the past-date editing rules
Ordering: priority groups and drag-to-reorder
Carry-over: the 7-day pending section, "Move to today" and the original-date badge
Recurring tasks: patterns, generating each day's occurrences, and locking past ones
Streaks: the streak cards with current and best
Hardening: tests, alarms, a backup and restore drill, load testing

Each step ends deployed to prod.