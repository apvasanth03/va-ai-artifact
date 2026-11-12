# va-epic-exec

Deliver an epic too big for one session, across kickoff, ticket, and close stages, with you approving every change of course.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Workflow](#workflow)
- [Output layout](#output-layout)
- [Related skills](#related-skills)

## What it does

- Turns an epic into an approved spec and a set of single-session tickets
- Delivers one ticket per session; workspace files carry the memory between sessions
- Judges the finished epic against its spec and merges the session retros into one
- Asks for your approval before changing the spec, adding or dropping a ticket, or applying a retro fix

## When to reach for it

- The work spans many sessions and needs durable state between them
- You want each ticket reviewed and approved before it counts as done

> ⚠️ For a task that fits one session, use [va-task-exec](va-task-exec.md) instead.

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `grilling` skill installed from [mattpocock/skills](https://github.com/mattpocock/skills)

## Input

- **Workspace** — the folder holding the epic's files (asked for if missing)
- **Epic detail** — what you want delivered; needed for kickoff only

## Workflow

The agent infers the stage from the workspace, states it, and confirms it with you before acting. You can override by naming a stage ("execute this ticket").

| Stage | When | What happens |
|---|---|---|
| **Kickoff** | No `state.json` yet | Explore the code, grill the epic detail, write `spec.md`, propose the tickets, then create the ticket files. Approval on the spec and on the ticket split |
| **Ticket** | Tickets still `todo`, `in_progress`, or `review` | One ticket per session: orient from the spec and progress notes, propose the next ticket, execute it (via `va-task-exec`), stop for your review, then commit and close it out once you approve |
| **Close** | Every ticket `done` or `dropped` | Review the epic against the spec's definition of done, report met/unmet with evidence, propose tickets for unmet items, write the final retro |

### Ticket status

`todo` → `in_progress` → `review` → `done` (`dropped` for a cancelled ticket). Only your approval moves a ticket from `review` to `done`.

### Handoffs

- A session that ends early leaves a short handoff in `progress.md` so the next one can resume
- Handoffs hold only what can't be derived from git or the code: surprises, decisions with reasons, open questions, next steps

## Output layout

```text
<workspace>/
├── spec.md          # What and why, epic-level definition of done, decisions
├── state.json       # Ticket statuses, blockers, results, epic branch
├── progress.md      # Handoffs between sessions, newest first
├── retro.md         # Final epic retro (written at close)
├── kickoff/retro.md # Friction from kickoff, if any
└── tickets/
    └── 01_<name>/
        ├── <name>.md    # Outcome, acceptance criteria, verification
        ├── retro.md     # Friction from this ticket's sessions, if any
        └── plan/plan.md # The ticket's plan
```

## Related skills

- [va-task-exec](va-task-exec.md) — executes each ticket
- [va-retro](va-retro.md) — writes the session and final retros
