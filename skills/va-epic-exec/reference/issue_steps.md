# Issues

Fix the issues the user finds while testing finished work. The user shares
them in a batch; the agent groups them by root cause, and each fix group is
fixed, reviewed and committed on its own.

- **Triage**
  - Read `state.json` and all of `progress.md`, unless this session already
    has. For each issue, find its suspected root cause from the user's steps
    and the code, then route it:
    - Inside a ticket not yet `done`: rework for that ticket; note it in
      `progress.md` under the ticket's id.
    - Already in a group, or already fixed: add it to that group, or point to
      the fixing commit.
    - A missing requirement, not a bug: propose a story change and a build
      ticket, per the approval principle.
    - Otherwise: a fix group, with the issues that share its suspected root
      cause or component.
  - Size each group. *Small*: the fix changes no HLD contract and no story
    behaviour, and fits in a session. Otherwise *large*.
  - Propose the groups as a table of id, name, issues, suspected root cause
    and size. **Approval required.**
  - Write each small group to `issues/I{NN}_{name}.md` from the template below
    and add it to `state.json`'s `issues` as `todo`. A large group becomes a
    `fix` ticket from [`ticket_template.md`](ticket_template.md) instead,
    with a regression test in its DoD, added to `state.json`'s `tickets` as
    `todo`. New ids continue from the highest existing ticket or group id. If
    `close` is `done`, set it `todo`.

- **Fix**, one small group at a time
  - Set the group `in_progress`. Confirm the root cause with a failing test
    where feasible; otherwise mark it an assumption. When the group's issues
    turn out to have different causes, split the group and tell the user.
  - Fix it, add the regression test, and run what you can (tests, build,
    lint) until nothing is red. A check you can't run, such as on a device,
    becomes manual check steps for the user.
  - Fill in the group file, set it `review`, and show the user the root cause,
    the fix, the verification results and the manual check steps. Wait for the
    user.
  - After the user approves, commit the group as one commit per repo touched
    and set it `done` with its `result`. Take the next small group if the
    session has room. If the user rejects the fix, keep the group
    `in_progress` and continue it.

- **Wrap up**
  - Update `progress.md` per the Progress principle, including what the next
    session needs to resume a group left `in_progress`, and write the session
    retro.

## Group template

```markdown
# I{NN}: [Group name]

## Issues
- [Symptom and steps to reproduce, as the user reported it]

## Root cause
[One or two lines; marked an assumption when no failing test confirms it.]

## Fix
[What changed.]

## Verification
- Regression test: [test name, or why there is none]
- Manual checks: [steps for the user, or none]
```
