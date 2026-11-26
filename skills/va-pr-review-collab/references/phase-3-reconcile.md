# Phase 3 — Reconcile

**Goal:** one final list, decided in two steps by source, with the reviewer as tiebreaker — the agent's review is input, not a veto. This is round 1's reconcile; Phase 5 reuses the queue and the decision steps below.

## Build the queue

Read `reviewer_review.md` and `agent_review.md`. Resolve anything ambiguous in a reviewer note (intent or location) with the reviewer first. Then write `rounds/1/review/review_queue.md`: one ordered table, reviewer items first, items describing the same thing merged into one row with source `Both`, agent rows ordered critical → major → minor.

| # | Source | Severity | File:Line | Title | Issue | Fix | Decision | Note |
|---|---|---|---|---|---|---|---|---|

- `Decision` starts `Pending` and `walk_item.py` updates it; `Note` holds a discard reason.
- `Severity` is a proposal the reviewer confirms. `File:Line` is a real file and one `+`-side line per `scripts/diff_lines.py` (`null` for deletion-only); a reviewer-given anchor is a hint to verify.
- `Issue` and `Fix` are one short line each: the problem, and the fix in words. For a reviewer note, `Issue` is the reviewer's intent.
- Split a note per location, or anchor once and name the other places in the body — whichever the author reads best.

The queue is the only file written before the reviewer decides.

## Decide

Each step shows one **decision table**, its cells taken from the queue rows:

| # | Severity | Title | Issue | Fix |
|---|---|---|---|---|

1. **Reviewer rows** (source `Reviewer` or `Both`), **approve-by-exception**: the reviewer replies with exceptions ("approve all except 3"); every row not named is approved.
2. **Agent-only rows**, all severities, as a **keep-list**: the reviewer names the rows to keep; every row not named is discarded.

Within either reply, the reviewer can name a row with:

- **edit**: a field or the severity and the change; the item is written with it applied, and recorded with `--edited`.
- **discard**: a few words of reason.
- **expand**: write that row's full item in chat with its evidence, then wait for that row's decision.

A step is done when every row in it is out of `Pending`: each approved, kept or edited row has its item in `final_review.json`, and each other row is discarded.

## Write the items

Write the items in the same turn as the reviewer's reply. `walk_item.py` marks a row only when its item is written, so a session resumed after a compaction restarts at the first `Pending` row, and a reply whose items were never written is asked again.

Each item is complete, with no ambiguity left: its reader is the PR author, cold, and acts without asking anyone. It keeps the queue row's finding, severity and fix direction, and adds the detail — every symbol and place involved in `issue` and `why`, and in `suggestion` the fix with a code snippet and every other place to change. Fields are the `new` item in `SKILL.md`'s Review Data.

```bash
# items for the step, keyed by queue row; --edited lists the edited rows (or alone: all of them)
python scripts/walk_item.py add <workspace_path> --section new [--edited 3,5] <<'EOF'
{"1": {"title": "...", "severity": "major", "file": "...", "line": 84,
       "issue": "...", "why": "...", "suggestion": "..."},
 "3": {...}}
EOF
python scripts/walk_item.py discard <workspace_path> --rows 4,5 --reason "user is never null"
# a later change to a written item: short fields with --set, long text on stdin with --field
python scripts/walk_item.py edit <workspace_path> --row 3 --set severity=minor
python scripts/walk_item.py edit <workspace_path> --row 3 --field suggestion <<'EOF'
...
EOF
```

`comment_id` comes from Phase 4.

**Done when:** no row of `review_queue.md` is `Pending`, every approved, kept or edited row has its item in `final_review.json`, and the reviewer has answered whether to post.
