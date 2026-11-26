# Phase 4 Plan review · Phase 5 Fix

**Goal**: the approved fixes land as one verified commit, pushed to the PR
branch, with every reply still true to the code.

## Plan review

The sections were written during the walk. Review them as one plan and add:

- **Cross-fix notes** — fixes that touch the same files or must land in an
  order, and anything one fix changes for another.
- **Verification** — the checks for what this round touches (format, analyze,
  the affected tests and packages), worked out from the repo's own docs and
  tooling. Scoped to the change, not the whole suite.

Then point the user to it:

```markdown
Plan ready: `rounds/<N>/plan.md` — approve?
```

Questions and edits come after they read it; edit the plan in place. On the
yes:

```bash
python scripts/round.py plan-approved <workspace>
```

## Fix

Implement the plan, then run its Verification until it is green. Then
self-review the diff against the plan: every planned fix delivered, nothing
unplanned, and each `fix` reply still describes what changed.

When the code ends up differing from what a reply says, re-record that row
with the corrected reply (`walk_item.py add`); after plan approval the script
marks it as a deviation. A verification that stays red, or a fix the plan
didn't foresee, goes to the user before anything is committed.

### Commit gate

```markdown
Verified ✓ <checks, one line> · Self-review ✓ <n>/<n> planned fixes, nothing unplanned
Deviations: #5 reply updated — only if any
Commit `fix: address PR review comments (round <N>)` (<n> files) — approve?
```

On the yes, commit everything as one commit, then record it:

```bash
python scripts/round.py commit <workspace> <sha>
```

### Push gate

```markdown
Committed `<sha7>`. Push `<branch>` to origin — approve?
```

On the yes, push the branch.

## Resume

`round.py status` gives `plan` (review not approved), `fix` with
`uncommitted_changes` (implementing or verifying when true, ready to commit when
false) or `push`.

**Done when**: `round.py status` shows `post`: the plan is approved, the round
commit is recorded and on origin.
