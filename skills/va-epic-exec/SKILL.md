---
name: va-epic-exec
description: Run an epic too big for one session across kickoff, ticket and close stages, with the user approving every change of course.
disable-model-invocation: true
---

Deliver an epic over many fresh sessions. The workspace files carry the memory,
and the user approves every change of course.

Read [`workspace_layout.md`](reference/workspace_layout.md) before any stage.

## Inputs

- **Workspace**: the folder holding the epic's files.
- **Epic detail**: what the user wants delivered. Needed for kickoff only.

Work only in the folder the user names; ask if the workspace is missing.

## Stage

Infer the stage from the workspace; state it and confirm it before acting. The
user can override by naming one ("execute this ticket").

| Workspace | Stage | Follow |
|---|---|---|
| No `state.json` | Kickoff | [`kickoff_steps.md`](reference/kickoff_steps.md) |
| Tickets still `todo`, `in_progress` or `review` | Ticket | [`ticket_steps.md`](reference/ticket_steps.md) |
| Every ticket `done` or `dropped` | Close | [`close_steps.md`](reference/close_steps.md) |

## Principles

- **Pointer, not fact**
  - What git or the code already says is referenced by commit id or path.

- **Handoff holds what can't be derived**
  - Each `progress.md` line is something the next session cannot derive from git
    or the code: a surprise against the spec or a ticket, a mid-flight decision
    with its reason, an open question, or what comes next.

- **Changes to the spec or tickets need approval**
  - When work shows that `spec.md` or a ticket is wrong or needs correcting,
    including adding or dropping a ticket, propose the change to the user and
    update it only after the user approves.

- **Fixes need approval**
  - Propose each retro fix to the user as you write it, and apply it only after
    the user approves.

- **Templates are guidelines**
  - Adapt each template to the task: add, merge or drop sections to fit the
    work.
