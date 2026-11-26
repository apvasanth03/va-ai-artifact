---
name: va-epic-exec
description: Run an epic too big for one session across kickoff, design, ticket and close stages, with the user approving every change of course.
disable-model-invocation: true
---

Deliver an epic over many fresh sessions. The workspace files carry the memory,
and the user approves every change of course. Kickoff settles the what
(`story.md`), design settles the how (`hld.md`) and splits the tickets, and
each ticket is planned and built in its own session. Issues the user finds
while testing are fixed in groups, apart from the tickets, and the epic's one
PR has its review comments addressed in rounds.

Read [`workspace_layout.md`](reference/workspace_layout.md) before any stage or
entry.

## Inputs

- **Workspace**: the folder holding the epic's files.
- **Epic detail**: what the user wants delivered. Needed for kickoff only.

Work only in the folder the user names; ask if the workspace is missing.

## Stage

Infer the stage from `state.json`; state it and confirm it before acting. The
user can override by naming one ("execute this ticket"). The first row that
matches wins.

| `state.json` | Stage | Follow |
|---|---|---|
| Missing, or `kickoff` not `done` | Kickoff | [`kickoff_steps.md`](reference/kickoff_steps.md) |
| `design` not `done` | Design | [`design_steps.md`](reference/design_steps.md) |
| Tickets or issue groups still `todo`, `in_progress` or `review` | Ticket | [`ticket_steps.md`](reference/ticket_steps.md) |
| Every ticket and issue group `done` or `dropped`, `close` not `done` | Close | [`close_steps.md`](reference/close_steps.md) |
| `close` is `done` | Finished | Tell the user the epic is closed |

Two entries skip the table, at any stage once there is code:

- **Testing issues**: when the user shares issues from testing finished work,
  follow [`issue_steps.md`](reference/issue_steps.md) from its triage.
- **PR comments**: when the user asks to address the review comments on the
  epic's PR, follow [`pr_steps.md`](reference/pr_steps.md).

## Principles

- **Pointer, not fact**
  - What git or the code already says is referenced by commit id or path.

- **Progress holds gotchas**
  - A *gotcha* is a fact the next session would act wrongly without, and
    cannot get from git, the code, `state.json`, the story, the HLD, a ticket
    or an issue group: a constraint, a short-lived user choice with its
    reason, a deliberate oddity. Example: "Hardware goes out with its subtype,
    or the server returns 500."
  - A choice that shapes the rest of the epic, one that outlives its ticket,
    leaves `progress.md` with the user's approval: a technical choice goes to
    the HLD's Key Decisions, a behaviour or domain choice to the story's
    Decisions. Traps and to-dos stay.

- **Changes to the story, HLD or tickets need approval**
  - When work shows that `story.md`, `hld.md` or a ticket is wrong or needs
    correcting, including adding or dropping a ticket, propose the change to
    the user and update it only after the user approves.

- **Session retro**
  - A session that hit friction writes its retro with
    [`va-retro`](../va-retro/SKILL.md) before it ends, in the `retro.md` of
    the folder it worked in: `kickoff/`, `design/`, the ticket's folder,
    `issues/` or `pr_comments/`.

- **PR threads close the loop**
  - A ticket or issue group that records a PR thread URL tells the user, when
    it is `done`, the thread and the fixing commit to reply with.

- **Fixes need approval**
  - Propose each retro fix to the user as you write it, and apply it only after
    the user approves.

- **Templates are guidelines**
  - Adapt each template to the task: add, merge or drop sections to fit the
    work.
