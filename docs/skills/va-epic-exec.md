# va-epic-exec

Deliver an epic too big for one session, across kickoff, design, ticket, and close stages, with you approving every change of course.

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

- Kickoff settles **what**: an approved `story.md` (deliverables, acceptance criteria, behaviour decisions)
- Design settles **how**, in a fresh session: an approved `hld.md`, then a split into single-session tickets
- Delivers one ticket per session (plan, implement, verify, review); workspace files carry the memory between sessions
- Fixes the issues you find while testing, grouped by root cause, apart from the tickets
- Addresses the review comments on the epic's single PR in rounds, via `va-pr-address-comments`
- Judges the finished epic against its story and HLD, and merges the session retros into one
- Asks for your approval before changing the story, HLD, or tickets, adding or dropping a ticket, or applying a retro fix

## When to reach for it

- The work spans many sessions and needs durable state between them
- You want each ticket reviewed and approved before it counts as done

> ⚠️ For a task that fits one session, use [va-task-exec](va-task-exec.md) instead.

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `grilling` skill installed from [mattpocock/skills](https://github.com/mattpocock/skills)
- Installed alongside it: `va-task-exec`, `va-sdlc-template`, `va-retro`, `va-pr-address-comments`

## Input

- **Workspace** — the folder holding the epic's files (asked for if missing)
- **Epic detail** — what you want delivered; needed for kickoff only

## Workflow

The agent infers the stage from `state.json`, states it, and confirms it with you before acting. You can override by naming a stage ("execute this ticket"). Two entries work at any stage once there's code: [issues from dev testing](#issues-from-dev-testing) and [PR review comments](#pr-review-comments).

| Stage | When | What happens |
|---|---|---|
| **Kickoff** | No `state.json`, or `kickoff` not done | Creates `state.json` and `progress.md`, explores lightly (only today's behaviour), grills the epic detail, writes `story.md`. Approval on the story |
| **Design** | `design` not done | Explores the code, writes or validates `hld.md`, proposes the tickets, then creates the ticket files. Approval on the HLD and on the split |
| **Ticket** | Tickets or issue groups still `todo`, `in_progress`, or `review` | One ticket per session: orient from `state.json` and progress notes, propose the next item (a resume first, then open issue groups, then a `todo` ticket whose blockers are done), execute it via `va-task-exec` from the plan onward, stop for your review, then commit and close it out once you approve |
| **Close** | Every ticket and issue group `done` or `dropped` | Checks the story's acceptance criteria with evidence, checks the code against the HLD, proposes follow-up tickets, writes the final retro |
| **Finished** | `close` done | Tells you the epic is closed |

### Splitting tickets

- Each ticket fits one session, can be verified on its own, and names its blockers
- Default is component by component, in dependency order, following the HLD; vertical slices when you ask for them
- Each story acceptance criterion is served by the ticket that completes it; each blocking technical unknown gets a POC ticket

### Per-ticket execution

- The ticket is the requirement: the plan's `Requirement` links to the ticket file instead of copying it, and no `story.md` is written per ticket
- Design that spans tickets is proposed as an `hld.md` update; design only one ticket needs goes in its plan
- A `fix` ticket runs as a bug fix: reproduce, root cause, regression test
- Checks the agent can't run, such as on a device, come back to you as manual check steps in the summary

### Issues from dev testing

Share the issues you find while testing finished work, at any stage, as a list, notes, screenshots, or logs.

| Step | What happens |
|---|---|
| **Triage** | The agent finds each issue's suspected root cause and routes it: rework for an unfinished ticket, an existing group, a story change for a missing requirement, or a fix group. It proposes the groups with their size. Approval on the groups |
| **Fix** | One small group at a time: confirm the root cause (a failing test where feasible), fix, add a regression test, run tests, build, and lint. Checks the agent can't run, such as on a device, come back to you as manual check steps |
| **Review** | You approve each group; the agent commits it as one commit, then takes the next small group if the session has room |

- **Small** groups change no HLD contract or story behaviour and fit a session; **large** ones become a `fix` ticket with the full ticket flow
- New issue groups after close reopen the close stage

### PR review comments

The epic has one PR. Ask to address its review comments at any stage once there's code; the agent runs [va-pr-address-comments](va-pr-address-comments.md) round by round.

- **Workspace**: `pr_comments/` in the epic workspace
- **Context**: `story.md` and `hld.md`; for a comment that needs it, the plan or issue file of the work that changed that code
- **Beyond the round**: a comment that needs more work becomes a proposed issue group (bug) or story change plus ticket (new requirement). The reply tells the reviewer in plain words that a later commit on this PR will fix it; once that fix is done, the agent gives you the thread and the commit to reply with
- **Close**: checks the last round is done (or asks whether to close anyway) and merges the round retros

### Status

- Stages: `todo` → `in_progress` → `done`; approving a follow-up ticket at close, or new issue groups after it, sets `close` back to `todo`
- Tickets and issue groups: `todo` → `in_progress` → `review` → `done` (`dropped` for a cancelled one). Only your approval moves one from `review` to `done`

### Handoffs

- `progress.md` is edited in place and kept short, under three headings: Next, Gotchas, Open questions
- It holds only what can't be derived from git, the code, or the other files; a decision that outlives its ticket moves to the story (behaviour) or the HLD (technical), with your approval
- A session that hit friction writes its retro in the folder it worked in; close merges them all

## Output layout

```text
<workspace>/
├── story.md          # What and why: deliverables, acceptance criteria, decisions
├── hld.md            # How: design that spans tickets, decisions, contracts
├── state.json        # Stage, ticket, and issue statuses, blockers, results, epic branch
├── progress.md       # Handoffs between sessions
├── retro.md          # Final epic retro (written at close)
├── kickoff/retro.md  # Friction from kickoff, if any
├── design/retro.md   # Friction from design, if any
├── tickets/
│   └── 01_<name>/
│       ├── <name>.md     # Why, what, DoD, context
│       ├── retro.md      # Friction from this ticket's sessions, if any
│       └── plan.md       # The ticket's plan (plan/plan.md when complex)
├── issues/
│   ├── I01_<name>.md     # One fix group: issues, root cause, fix, verification
│   └── retro.md          # Friction from issue-fixing sessions, if any
└── pr_comments/          # va-pr-address-comments workspace for the epic's PR
    └── retro.md          # Friction from comment rounds, if any
```

## Related skills

- [va-task-exec](va-task-exec.md) — executes each ticket, from the plan onward
- [va-sdlc-template](va-sdlc-template.md) — used for the story and the HLD
- [va-pr-address-comments](va-pr-address-comments.md) — addresses the PR's review comments
- [va-retro](va-retro.md) — writes the session and final retros
