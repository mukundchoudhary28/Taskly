# Taskly — Mission

## What Taskly is

Taskly is a daily to-do list web app. A user signs in, sees what they need to get done **today**, ticks tasks off as they finish them, and keeps track of anything left over from previous days. It is meant for anyone who wants a simple, focused way to plan and finish their day.

## Why we're building it

Taskly is a **production-grade learning project**. The app logic is deliberately small so the real focus can be on how software is built and run in a company:

- Authentication and user management
- A relational database with migrations
- Containerised deployment on AWS
- Infrastructure as code
- CI/CD with separate staging and production environments
- Monitoring, alerting and cost control

It is not a commercial SaaS yet. There is no billing in the MVP. Billing may come in v1 or v2.

## Guiding principles

1. **Production-grade, not tutorial-grade.** Real domain, HTTPS, managed auth, backups, alerts and reproducible infrastructure.
2. **Ship small, ship often.** Start with a minimal version that is fully deployed, then add one feature at a time. Every increment ends deployed to prod.
3. **Managed services where they reduce risk.** Use AWS-managed services where they make things more secure or reliable, especially auth and the database.
4. **Document the why.** Every major technology choice records the alternatives considered and the reason for the choice.
5. **Stay within budget.** Design around the AWS free tier and $100 of credit.

## Who it's for

Anyone who wants to plan their day and see what's left undone. Users sign up with name, email and password, or with Google.

## MVP feature scope

### Accounts
- Sign up with **name, email and password**; log in with email and password
- **Sign in with Google**
- Each user's **timezone** is stored. "Today" and the midnight rollover follow the user's local time.

### Today view (home page)
The home page is the list of tasks for today, in three sections from top to bottom:

1. **Moved from earlier:** tasks moved from a previous day. They are pinned to the top with a badge such as *"Originally Sep 26"*, because they should be the first thing done today.
2. **Today's tasks:** grouped by priority (High → Medium → Low). Dragging reorders tasks within a priority group; dragging a task into a different group changes its priority.
3. **Pending from the last 7 days:** unfinished one-off tasks from the past 7 days, shown in a **different color**, each with a **"Move to today"** action.

If a moved task is still unfinished at the end of the day, it shows as pending again the next day and keeps its original-date badge.

### Tasks
- Each task has a **title**, optional **notes** and a **priority** (High / Medium / Low), shown with a **checkbox** to mark it done
- Tasks can be created, edited, deleted and reordered

### Dates
- A **date picker** lets the user view any day
- **Future dates:** users can plan ahead and add tasks
- **Past dates:** one-off tasks can be ticked, unticked, edited and deleted. New tasks cannot be created on past dates.

### Recurring tasks and streaks
- Patterns: **daily**, **weekdays**, or **weekly on chosen days**
- **Missed occurrences are not carried forward.** A missed occurrence resets that task's streak.
- An occurrence can only be ticked **on its own day**. After the user's midnight it locks and the outcome is final.
- The **streak** counts completed scheduled occurrences in a row. Days on which the task isn't scheduled never break the streak.
- Each recurring task has a **streak card** showing its **current streak** and **best streak**
- Editing the pattern (e.g. daily → weekdays) keeps the streak; deleting the series removes its history

### Platform
- **Responsive web app** that works on phone browsers. There is no native mobile app in the MVP.

## Out of scope for the MVP (v1 / v2)
- Reminders and notifications (email or push)
- Billing and plans
- Native mobile or installable app
- Shared lists or collaboration

## What success looks like
- A stranger can visit `taskly.mukundchoudhary.space`, sign up (email or Google), and use every MVP feature
- Every change reaches production through CI/CD. Nothing is deployed by hand.
- The whole AWS environment can be rebuilt from Terraform
- Logs, alarms and budget alerts are in place, and a database restore has been tested
- Each technology decision is documented with its alternatives and reasoning
