# Ticket

Deliver one ticket per session, with the user approving before it counts as
done.

- **Orient**
  - Read `state.json` and all of `progress.md`. If `state.json` records a
    branch that differs from that repo's current one, tell the user.

- **Pick**
  - Propose the next item: a ticket or issue group left `in_progress` or
    `review` first, as a resume; then open issue groups; then a `todo` ticket
    whose blockers are all `done`. The user
    may name another. Execute only after the user approves the pick. Then read
    the ticket and the `story.md` and `hld.md` sections its Context points to.
    A `review` ticket goes straight to the close-out once the user approves
    its work. An issue group follows the Fix step of
    [`issue_steps.md`](issue_steps.md) instead.

- **Execute**
  - Set the ticket `in_progress`; for a resume, first read its plan
    (`plan.md` or `plan/plan.md`) and the current diff. Then follow
    [`va-task-exec`](../../va-task-exec/SKILL.md) with these overrides:
    - The workspace is the ticket's folder; the context is the ticket and the
      sections it points to.
    - Requirement: the ticket is the requirement and its DoD is the plan's
      DoD. Grill only what the ticket leaves open, and propose any ticket
      change per the approval principle. Step 2 writes nothing and needs no
      approval: the plan's Requirement section is a link to the ticket file,
      `Scope` is written with the rest of the plan, and the first approval is
      the plan.
    - HLD: design that spans tickets is proposed as an `hld.md` update; design
      only this ticket needs goes in the plan's `Why this shape`.
    - A `fix` ticket is a bug fix in `va-task-exec`'s terms.
    - PR comments go through the epic's PR comments entry, not
      `va-task-exec`'s.
    - Stop at its summary, set the ticket `review`, and wait for the user.
  - A POC ticket also writes its finding in the ticket folder and proposes the
    `hld.md` update it implies.
  - Done when every DoD item has evidence in the summary.

- **Close out**
  - After the user approves, commit the ticket's code as one commit per repo
    touched. Set the ticket `done` with its `result`, then leave
    `progress.md` with only next steps, open questions and gotchas (a choice
    that outlives the ticket is proposed for the story or HLD instead, per
    the Progress principle): add the ticket's, drop what it made obsolete.
    Show the user the `progress.md` diff, and write the session retro.

If the user rejects the work, keep the ticket `in_progress` and continue it. A
session that ends before approval records in `progress.md` what the next one
needs to resume, and writes its session retro.
