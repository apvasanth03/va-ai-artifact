# Phase 3 — Reconcile

**Goal**: one final list, decided one item at a time, with the reviewer as tiebreaker — the agent's review is input, not a veto. This is round 1's reconcile; Phase 5 reuses the queue and the walk below.

## Build the queue

Read `reviewer_review.md` and `agent_review.md`. Resolve anything ambiguous in a reviewer note (intent or location) with the reviewer first. Then write `rounds/1/review/review_queue.md`: one ordered table, reviewer items first, items describing the same thing merged into one row with source `Both`.

| # | Source | Severity | File:Line | Title | Issue | Decision | Note |
|---|---|---|---|---|---|---|---|

- `Decision` starts `Pending` and `walk_item.py` updates it; `Note` holds a discard reason.
- `Severity` is a proposal the reviewer confirms. `File:Line` is a real file and one `+`-side line per `scripts/diff_lines.py` (`null` for deletion-only); a reviewer-given anchor is a hint to verify.
- `Issue` is the short problem statement, as in the agent ledger; for a reviewer note, the reviewer's intent.
- Split a note per location, or anchor once and name the other places in the body — whichever the author reads best.

## Walk

Show the first `Pending` row as one card:

> **#3 · major · `path/File.kt:84`** · Title · Issue · Source
> approve · edit · discard · expand

- **expand**: give the why, the evidence and the proposed fix in chat, then wait for the next decision.
- **approve** / **edit**: write the item the moment it is decided (edit applies the reviewer's change first and adds `--edited`), then show the next card.
- **discard**: mark the row with a few words of reason, then show the next card.

The item's reader is the PR author, cold: the comment carries the reason and the fix they need to act without asking anyone. Expand the reviewer's intent; stay inside it.

```bash
python scripts/walk_item.py add <workspace_path> --section new --row 3 [--edited] <<'EOF'
{"title": "...", "severity": "major", "file": "...", "line": 84,
 "issue": "...", "why": "...", "suggestion": "..."}
EOF
python scripts/walk_item.py discard <workspace_path> --row 4 --reason "user is never null"
```

The script validates the item, creates `final_review.json` on first use and marks the row. `comment_id` comes from Phase 4.

A new session, or one after a compaction, resumes at the first `Pending` row of `review_queue.md`.

**Done when**: no row is `Pending`, every approved item is in `final_review.json`, and the reviewer has answered whether to post.
