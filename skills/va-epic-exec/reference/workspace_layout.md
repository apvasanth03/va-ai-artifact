# Workspace layout

Sessions start cold, so each file has one purpose.

## Layout

```
workspace/
├── spec.md
├── state.json
├── progress.md
├── retro.md
├── kickoff/
│   └── retro.md
└── tickets/
    └── {NN}_{name}/
        ├── {name}.md
        ├── retro.md
        └── plan/plan.md
```

## Files

- `spec.md`
  - The epic's source of truth: what and why, the epic-level DoD, and the
    decisions behind it. The other sections are in
    [`spec_template.md`](spec_template.md), which it is written from.

- `state.json`
  - Machine-readable status of the tickets, and the epic branch. Structure
    below.

- `progress.md`
  - The handoff between sessions, newest entry first.

- `retro.md`
  - The epic's final retro. The close stage merges the session retros into it.

- `kickoff/retro.md`
  - The friction the kickoff session hit, if any, written by that session
    before it ends, in the [`va-retro`](../../va-retro/SKILL.md) template.

- `tickets/{NN}_{name}/{name}.md`
  - One ticket: its outcome, acceptance criteria, verification and blockers.
    Written from [`ticket_template.md`](ticket_template.md).

- `tickets/{NN}_{name}/retro.md`
  - The friction the ticket's sessions hit, if any, written by each session
    before it ends, in the [`va-retro`](../../va-retro/SKILL.md) template.

- `tickets/{NN}_{name}/plan/plan.md`
  - The ticket's plan, created through
    [`va-task-exec`](../../va-task-exec/SKILL.md).

## state.json

```json
{
  "branch": "feature/x",
  "tickets": [
    {
      "id": 1,
      "name": "name",
      "status": "done",
      "blocked_by": [],
      "result": ["a1b2c3d"]
    }
  ]
}
```

- Status moves `todo → in_progress → review → done`; `dropped` is for a
  cancelled ticket. Only the user's approval moves `review` to `done`.
- `branch` is the epic branch; omit it if the user works without one. When the
  epic spans repos it is an object with one branch per repo.
- `id` is the ticket number; `{NN}` in paths is the zero-padded id and `{name}`
  is the `name`. `blocked_by` lists ids.
- `result` points to the outcome, set when the ticket is done: commit ids in the
  code repo (prefixed with the repo when the epic spans repos), and output files
  such as a findings file in the ticket folder.
