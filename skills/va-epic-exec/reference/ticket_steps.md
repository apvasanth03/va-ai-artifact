# Ticket

Deliver one ticket per session, with the user approving before it counts as done.

- **Orient**
  - Read `spec.md`, `state.json`, and `progress.md` as far back as still
    matters. If `state.json` records a branch that differs from that repo's
    current one, tell the user.

- **Pick**
  - Propose the next ticket, and a ticket left `in_progress` or `review` comes
    first as a resume. The user may name another. Execute only after the user
    approves the pick. A `review` ticket goes straight to the close-out once the
    user approves its work.

- **Execute**
  - Set the ticket `in_progress`; for a resume, first read its `plan/plan.md`
    and the current diff. Then follow
    [`va-task-exec`](../../va-task-exec/SKILL.md) with these overrides:
    - The ticket is the story and its acceptance criteria are the DoD; grill
      only what the ticket leaves open.
    - The workspace is the ticket's folder.
    - Stop at its summary, set the ticket `review`, and wait for the user.
  - A POC or research ticket also writes its finding in the ticket folder.
  - Done when every acceptance criterion has evidence in the summary.

- **Close out**
  - After the user approves, commit the ticket's code as one commit per repo
    touched. Set the ticket `done` with its `result`, and prepend a handoff
    entry to `progress.md` if it has lines worth keeping. Write the session
    retro in the ticket folder's `retro.md` with
    [`va-retro`](../../va-retro/SKILL.md), if the session had friction.

If the user rejects the work, keep the ticket `in_progress` and continue it. A
session that ends before approval prepends a handoff so the next one can resume,
and writes its session retro if it hit friction.
