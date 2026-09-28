# Taskly — Tech Stack & Architecture

## Stack at a glance

| Layer | Choice |
|---|---|
| Frontend | React + TypeScript + Vite |
| Frontend hosting | Amazon S3 (private bucket) + CloudFront |
| Backend | Python + FastAPI, in a Docker container |
| Backend hosting | Amazon ECS on Fargate, behind an Application Load Balancer |
| Container registry | Amazon ECR |
| Database | Amazon RDS for PostgreSQL |
| Migrations | Alembic (with SQLAlchemy) |
| Auth | Amazon Cognito user pool (email + password, Google login) |
| DNS | Route 53 hosted zone for `taskly.mukundchoudhary.space` |
| TLS certificates | AWS Certificate Manager (ACM) |
| Secrets | AWS Secrets Manager / SSM Parameter Store |
| Monitoring | Amazon CloudWatch (logs, metrics, alarms) |
| Cost control | AWS Budgets alerts |
| Infrastructure as code | Terraform (state stored in S3) |
| CI/CD | GitHub Actions, authenticating to AWS through OIDC |
| Python packaging | uv |

## Architecture

```
                         Users (browser)
                               │
                  taskly.mukundchoudhary.space
                               │
                        Route 53 (subdomain zone)
                 ┌─────────────┴──────────────┐
                 │                            │
        taskly.mukundchoudhary.space   api.taskly.mukundchoudhary.space
                 │                            │
          CloudFront (ACM cert)      Application Load Balancer (ACM cert)
                 │                            │
          S3 bucket (React build)     ECS Fargate service (FastAPI)
                                              │
                                   ┌──────────┼───────────┐
                                   │          │           │
                           RDS PostgreSQL  Secrets     CloudWatch
                                           Manager     Logs/Alarms

          Amazon Cognito (user pool + Google login)
          ├── Frontend: signs users in and receives JWTs
          └── FastAPI: verifies each JWT against Cognito's public keys
```

### How a request flows
1. The browser loads the React app from CloudFront.
2. The user signs in with Cognito (email/password or Google) and receives JWTs.
3. The React app calls the API with `Authorization: Bearer <token>`.
4. FastAPI checks the token's signature, expiry and audience against Cognito's public keys, then maps the token's `sub` to a row in `users`.
5. FastAPI reads and writes PostgreSQL. All times are stored in UTC, and "which day it is" is worked out using the user's timezone.

### Domains
- `taskly.mukundchoudhary.space`: frontend (prod)
- `api.taskly.mukundchoudhary.space`: API (prod)
- `staging.taskly.mukundchoudhary.space` / `api.staging.taskly.mukundchoudhary.space`: staging

Only the `taskly.` subdomain is handed to Route 53, by adding NS records at the current registrar. The root domain stays where it is.

## Decisions and alternatives

### Backend hosting: ECS Fargate
- **Chosen because:** container skills carry over to Kubernetes, Azure, GCP and plain VMs. Containers also suit AI and LLM workloads (long requests, streaming, large dependencies), and containerised services on private networks are standard in enterprise and regulated finance.
- **Alternatives:**
  - *Lambda + API Gateway:* far cheaper when idle, but specific to AWS, with cold starts, a 15-minute limit and package size limits. Worth learning later for event-driven jobs.
  - *EC2:* more for us to manage (patching, scaling) and teaches less of the modern deployment workflow.
  - *EKS:* overkill for one service, and the control plane costs money on its own.

### Auth: Amazon Cognito
- **Chosen because:** it's managed and secure. It handles password hashing, email verification, password reset, token refresh and Google login, so FastAPI only has to verify JWTs.
- **Alternatives:**
  - *Build it in FastAPI:* the part most likely to be done wrong for security.
  - *Auth0 / Clerk:* nicer to develop with, but outside AWS and paid at scale.
- **Trade-off:** Cognito's hosted UI is clunky, so we build our own sign-in screens against its API. It also ties us to AWS.

### Database: RDS PostgreSQL
- **Chosen because:** it's relational data (users, tasks, rules, completions), and RDS gives managed backups, point-in-time restore and patching.
- **Alternatives:**
  - *Aurora Serverless v2:* scales better but costs more at this size.
  - *PostgreSQL on EC2 or in a container:* we'd have to run backups ourselves.
  - *DynamoDB:* a poor fit for relational queries like date ranges and streaks.

### Frontend hosting: S3 + CloudFront
- **Chosen because:** a Vite build is static files. S3 + CloudFront is cheap, fast and a standard pattern.
- **Alternative:** *AWS Amplify Hosting:* simpler, but hides the pieces we want to learn.

### Infrastructure as code: Terraform
- **Chosen because:** it works across clouds and appears widely in job listings.
- **Alternative:** *AWS CDK:* write infrastructure in Python, but it only works for AWS.

### CI/CD: GitHub Actions + OIDC
- **Chosen because:** it sits next to the code, and OIDC means no AWS access keys are stored in GitHub.

## Data model (sketch)

```
users
  id (uuid, PK), cognito_sub (unique), email, name,
  timezone (IANA, e.g. "Asia/Kolkata"), created_at

tasks                     -- one-off tasks
  id, user_id → users,
  title, notes, priority (high|medium|low),
  task_date (date),       -- the day it's currently planned for
  original_date (date),   -- set when moved; drives the "Originally …" badge
  position (int),         -- order within its priority group
  completed_at (timestamptz, null),
  created_at, updated_at, deleted_at

recurring_rules
  id, user_id → users,
  title, notes, priority,
  pattern (daily|weekdays|weekly), days_of_week (int[]),
  start_date, created_at, updated_at, deleted_at

occurrence_completions
  id, rule_id → recurring_rules,
  occurrence_date (date), completed_at,
  UNIQUE (rule_id, occurrence_date)
```

**Recurring tasks** are stored as rules, not as copies of the task. Each day's occurrences are worked out when a day is viewed. Completions are stored one row per rule per day.

**Streaks** are calculated from the rule's schedule and its completions. Current and best streak can be cached on the rule later if needed.

**Key queries:**
- The 7-day pending section: one-off tasks where `task_date` is between today − 7 and today − 1, not completed, not deleted
- Today's view: tasks where `task_date` is today, plus today's recurring occurrences

## Environments
| | Staging | Prod |
|---|---|---|
| Trigger | Merge to `main` | Manual approval in GitHub Actions |
| Lifetime | Created on demand, torn down after testing | Always on |
| Data | Test data | Real users |

## Cost controls ($100 credit + free tier)
- **No NAT gateway:** Fargate tasks run in public subnets with tight security groups, or use VPC endpoints
- RDS is private, with no public access
- Smallest instance and task sizes to start
- Staging is torn down (`terraform destroy`) when not in use
- AWS Budgets alerts at $10, $25 and $50
- Confirm current AWS prices and free-tier terms before provisioning

## Security baseline
- HTTPS everywhere (ACM)
- RDS reachable only from the ECS tasks' security group
- Secrets in Secrets Manager or SSM, never in the repo or plain environment files
- The ECS task role has only the permissions it needs
- JWT verification on every protected endpoint
- Users can only read and write their own rows (enforced in every query)
- CORS restricted to the frontend's domains

## Repo layout (monorepo)
```
taskly/
├── frontend/          # React + TS + Vite
├── backend/           # FastAPI app, Alembic migrations, Dockerfile, uv project
├── infra/             # Terraform (modules + envs/staging, envs/prod)
├── .github/workflows/ # CI/CD pipelines
└── .claude/
    ├── CLAUDE.md          # How to work on this project
    ├── constitution/      # MISSION.md, TECH_STACK.md, ROADMAP.md (intent — changes need approval)
    ├── docs/              # ARCHITECTURE.md, CHANGELOG.md, PROJECT_STATUS.md (living, updated every change)
    ├── specs/             # PRDs and EDDs (phase-NN-<slug>.md, phase-NN-<slug>-edd.md)
    └── skills/            # Project skills (e.g. create-spec)
```
