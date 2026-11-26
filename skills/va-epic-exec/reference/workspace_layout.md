# Workspace layout

Sessions start cold, so each file has one purpose.

## Layout

```
workspace/
├── story.md
├── hld.md
├── state.json
├── progress.md
├── retro.md
├── kickoff/
│   └── retro.md
├── design/
│   └── retro.md
├── tickets/
│   └── {NN}_{name}/
│       ├── {name}.md
│       ├── retro.md
│       └── plan.md (or plan/plan.md)
├── issues/
│   ├── I{NN}_{name}.md
│   └── retro.md
└── pr_comments/
    ├── ...
    └── retro.md
```

## Files

- `story.md`
  - The epic's what and why: deliverables, ACs (the epic's DoD), out of scope
    and behaviour decisions. Written in kickoff with the `va-sdlc-template`
    skill (story) and the epic changes in
    [`kickoff_steps.md`](kickoff_steps.md).

- `hld.md`
  - The epic's how: the design that spans tickets, its key technical decisions,
    contracts and unknowns. Written in design with the `va-sdlc-template` skill
    (HLD).

- `state.json`
  - Machine-readable status of the stages, tickets and issue groups, and the
    epic branch. Created at the start of kickoff. Structure below.

- `progress.md`
  - What the next session needs, edited in place and read whole by every
    session, so it stays short (about 40 lines; past that, prune). Three
    headings:
    - **Next**: what to do next.
    - **Gotchas**: one line each, ending with its ticket or issue group id,
      e.g. `(04)`, `(I03)`.
    - **Open questions**: what the user still has to decide.

- `retro.md`
  - The epic's final retro. The close stage merges the session retros into it.

- `kickoff/retro.md`, `design/retro.md`
  - The friction that stage's session hit, per the Session retro principle.

- `tickets/{NN}_{name}/{name}.md`
  - One ticket: why, what, DoD and context. Written from
    [`ticket_template.md`](ticket_template.md).

- `tickets/{NN}_{name}/retro.md`
  - The friction the ticket's sessions hit, per the Session retro principle.

- `tickets/{NN}_{name}/plan.md` or `plan/plan.md`
  - The ticket's plan, created through
    [`va-task-exec`](../../va-task-exec/SKILL.md): `plan.md` for a simple plan,
    `plan/` for a complex one.

- `issues/I{NN}_{name}.md`
  - One fix group: the issues the user reported from testing, their root
    cause, the fix and its verification. Written from the template in
    [`issue_steps.md`](issue_steps.md).

- `issues/retro.md`
  - The friction the issue-fixing sessions hit, per the Session retro
    principle; each session adds its own.

- `pr_comments/`
  - The [`va-pr-address-comments`](../../va-pr-address-comments/SKILL.md)
    workspace for the epic's PR, set up by [`pr_steps.md`](pr_steps.md): it
    owns the PR's identity and round state. The epic adds only `retro.md`, the
    friction of the comment-round sessions.

## state.json

```json
{
  "branch": "feature/x",
  "stages": {
    "kickoff": "done",
    "design": "done",
    "close": "todo"
  },
  "tickets": [
    {
      "id": 1,
      "name": "name",
      "status": "done",
      "blocked_by": [],
      "result": ["a1b2c3d"]
    }
  ],
  "issues": [
    {
      "id": "I01",
      "name": "name",
      "status": "review",
      "result": []
    }
  ]
}
```

- A stage moves `todo → in_progress → done`; only the user's approval of its
  last gate sets it `done`. Approving a follow-up ticket in close, or new
  issue groups after it, sets `close` back to `todo`.
- A ticket moves `todo → in_progress → review → done`; `dropped` is for a
  cancelled ticket. Only the user's approval moves `review` to `done`. An
  issue group moves the same way.
- `branch` is the epic branch, set in design; omit it if the user works
  without one. When the epic spans repos it is an object with one branch per
  repo.
- `id` is the ticket number; `{NN}` in paths is the zero-padded id and `{name}`
  is the `name`. `blocked_by` lists ids. An issue group's id is `I{NN}`, also
  used in its file name.
- `result` points to the outcome, set when the ticket is done: commit ids in the
  code repo (prefixed with the repo when the epic spans repos), and output files
  such as a findings file in the ticket folder. An issue group's `result` is
  its commit ids.
