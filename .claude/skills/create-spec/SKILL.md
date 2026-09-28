---
name: create-spec
description: Create a feature branch and a PRD (product spec) in .claude/specs/ for the next Taskly feature. Use when the user runs /create-spec or asks to write a spec or PRD for a feature or roadmap phase. The spec describes what and why, not how, and is the input to plan mode for the implementation plan (EDD).
argument-hint: "<phase number> <feature name>  e.g. 5 carry-over"
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Agent, Bash(git status:*), Bash(git branch:*), Bash(git checkout:*), Bash(git switch:*), Bash(git pull:*)
---

# Create spec (PRD)

Create a feature branch and a product requirements document for: **$ARGUMENTS**

The PRD answers *what* the feature must do and *why*. It deliberately leaves *how* (endpoints, schemas, tables, files, libraries, components) to the implementation plan (EDD) produced afterwards in plan mode. A good PRD lets someone write the EDD and the tests without asking the product owner anything.

## Step 1 — Check the working tree
Run `git status`. If there are uncommitted, unstaged or untracked changes, **stop** and tell the user what's there. Don't stash, commit or discard anything yourself.

## Step 2 — Parse the arguments
From `$ARGUMENTS`, derive:
- `phase_number` — two digits, e.g. `05`
- `feature_title` — Title Case, e.g. `Carry-Over`
- `feature_slug` — lowercase kebab-case, max 40 characters, e.g. `carry-over`
- `spec_path` — `.claude/specs/phase-<phase_number>-<feature_slug>.md`
- `branch_name` — `feat/phase-<phase_number>-<feature_slug>`

If the phase number or feature name is missing, ask for it.

## Step 3 — Validate against the roadmap
- Find the feature in `.claude/constitution/ROADMAP.md` and note the phase's scope and definition of done.
- If it isn't in the roadmap, or it belongs to a later phase than the current one in `.claude/docs/PROJECT_STATUS.md`, say so and ask whether to continue. Anything outside `.claude/constitution/MISSION.md` needs the user's approval before a spec is written.
- If `spec_path` already exists, you are **updating** that spec: switch to its branch if it exists and skip Step 4.

## Step 4 — Create the feature branch
- Check `git branch` for `branch_name`. If it's taken, append `-2`, `-3`, … until it's free.
- `git checkout main` and `git pull`.
- `git checkout -b <branch_name>`.

The PRD, the EDD and the feature's code all go on this branch and ship as one PR.

## Step 5 — Gather context
Read before writing:
- `.claude/CLAUDE.md`
- `.claude/docs/PROJECT_STATUS.md` and `.claude/docs/ARCHITECTURE.md` (what exists today)
- The relevant sections of `.claude/constitution/MISSION.md` (feature rules) and this phase in `.claude/constitution/ROADMAP.md`
- Other files in `.claude/specs/` this feature depends on or affects

If application code exists, use an Explore subagent to find how related behaviour currently works. Summarise; don't paste code into the spec.

## Step 6 — Find the gaps and ask
List everything the source documents leave unclear. For Taskly, check these every time:
- **Time:** the user's timezone, midnight rollover, past vs today vs future dates
- **Carry-over:** the 7-day window, moved tasks, original-date badges
- **Recurring tasks and streaks:** schedules, locking, what resets or keeps a streak
- **Ownership:** another user's data, deleted data
- **UI states:** empty, loading, error, mobile layout
- **Limits:** lengths, counts, validation messages

Ask in batches of at most 4 questions, each with your recommended answer (use AskUserQuestion). **Never invent a product rule.** Anything still unresolved goes under Open questions.

## Step 7 — Write the spec
Copy `template.md` (in this skill's folder) to `spec_path` and fill in every section. Write "None" rather than leaving a section empty.

Writing rules:
- Number everything (`FR-1`, `BR-1`, `AC-1`) so the EDD, tests and PRs can refer to it.
- Every requirement is testable. No "fast", "intuitive" or "should handle" without a measurable meaning.
- Every FR is covered by at least one acceptance criterion in Given / When / Then form.
- Describe behaviour from the user's and the system's point of view. **No endpoint paths, table names, code, file names or library choices** — those belong in the EDD.
- Quote rules from `MISSION.md` rather than rephrasing them loosely. If this spec changes a mission rule, flag it clearly.

## Step 8 — Self-check
- [ ] Every FR has at least one AC, and every AC traces to an FR or BR
- [ ] Edge cases cover timezone/midnight, date boundaries, other users' data and empty states
- [ ] Non-goals list what a reader might wrongly assume is included
- [ ] No implementation details slipped in
- [ ] Consistent with `MISSION.md` and the phase's DoD in `ROADMAP.md`
- [ ] Open questions listed (or "None")

## Step 9 — Review, approve and report
- Save with **Status: Draft** and show the user a short summary: goal, number of requirements, key decisions, open questions.
- Revise until the user approves. Then set **Status: Approved** and add a line to the spec's revision history.
- Update `.claude/docs/PROJECT_STATUS.md` (link the spec under the current phase) and add to `.claude/docs/CHANGELOG.md` under `[Unreleased]` → Added.
- Don't commit unless the user asks.
- Finish with a report:
  - **Branch:** `<branch_name>`
  - **Spec:** `<spec_path>` (Draft / Approved)
  - **Feature:** `<feature_title>` — Phase `<phase_number>`
  - **Open questions:** count, or None
  - **Next step** — paste into plan mode:

    > Read `<spec_path>` and `.claude/CLAUDE.md`. Produce an implementation plan (EDD) covering API endpoints and schemas, data model and migrations, services and business logic, frontend screens and components, infra changes, tests mapped to each AC, rollout steps, and doc updates. Save it as `.claude/specs/phase-<phase_number>-<feature_slug>-edd.md`.
