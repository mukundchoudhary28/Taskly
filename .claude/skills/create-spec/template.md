# PRD: <Feature name>

| | |
|---|---|
| **Phase** | Phase N — <name> (see `.claude/constitution/ROADMAP.md`) |
| **Status** | Draft / Approved / Superseded |
| **Owner** | Shubham Choudhary |
| **Created** | YYYY-MM-DD |
| **Last updated** | YYYY-MM-DD |
| **Related specs** | `.claude/specs/...` or None |
| **EDD** | `.claude/specs/phase-NN-<slug>-edd.md` (once written) |

## 1. Summary
Two or three sentences: what this feature is and what the user gets from it.

## 2. Problem and why now
What the user can't do today, and why this is the next thing to build.

## 3. Goals
- What must be true when this ships.

## 4. Non-goals
- What this feature does **not** do, especially things a reader might assume it does.

## 5. User stories
- **US-1:** As a <user>, I want <action>, so that <benefit>.

## 6. Functional requirements
| ID | Requirement | Priority |
|---|---|---|
| FR-1 | The system shall … | Must / Should / Could |

## 7. Business rules
Rules that must hold regardless of the UI (enforced by the system, not only hidden in the interface).

| ID | Rule | Source |
|---|---|---|
| BR-1 | … | `MISSION.md` § … / decided in this spec |

## 8. User experience
- **Where it appears:** screens or sections affected.
- **Main flow:** step by step, in words.
- **States:** empty, loading, error, success.
- **Mobile:** anything different on small screens.
- **Copy:** key labels, messages and badges.

## 9. Edge cases
| Case | Expected behaviour |
|---|---|
| Around the user's midnight | … |
| Another user's data | Not visible or changeable; treated as not found |

## 10. Non-functional requirements
- **Security and privacy:** …
- **Performance:** measurable targets, if any.
- **Accessibility:** keyboard use, labels, colour not the only signal.
- **Observability:** what should be logged or measured.
- **Cost:** any new recurring AWS cost (or "None").

## 11. Acceptance criteria
| ID | Covers | Given / When / Then |
|---|---|---|
| AC-1 | FR-1 | **Given** … **When** … **Then** … |

## 12. Dependencies and assumptions
- **Depends on:** earlier phases or specs.
- **Assumptions:** anything taken as true that should be checked.

## 13. Out of scope / future
- Ideas deliberately left for later.

## 14. Open questions
| # | Question | Recommended answer | Status |
|---|---|---|---|
| 1 | … | … | Open / Resolved |

## 15. Definition of done
- All acceptance criteria pass in staging and prod.
- Phase DoD from `.claude/constitution/ROADMAP.md` is met.
- `.claude/docs/CHANGELOG.md`, `.claude/docs/PROJECT_STATUS.md` and `.claude/docs/ARCHITECTURE.md` are updated.

## Revision history
| Date | Change |
|---|---|
| YYYY-MM-DD | Draft created |
