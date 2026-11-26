# Phase 3 — Reconcile

**Goal**: one final list, decided in three steps by weight, with the reviewer as tiebreaker — the agent's review is input, not a veto. This is round 1's reconcile; Phase 5 reuses the queue and the decision steps below.

## Build the queue

Read `reviewer_review.md` and `agent_review.md`. Resolve anything ambiguous in a reviewer note (intent or location) with the reviewer first. Then write two files:

`rounds/1/review/review_queue.md`: one ordered table, reviewer items first, items describing the same thing merged into one row with source `Both`.

| # | Source | Severity | File:Line | Title | Issue | Fix | Decision | Note |
|---|---|---|---|---|---|---|---|---|

- `Decision` starts `Pending` and `walk_item.py` updates it; `Note` holds a discard reason.
- `Severity` is a proposal the reviewer confirms. `File:Line` is a real file and one `+`-side line per `scripts/diff_lines.py` (`null` for deletion-only); a reviewer-given anchor is a hint to verify.
- `Issue` and `Fix` are one short line each: the problem, and the fix in words. For a reviewer note, `Issue` is the reviewer's intent.
- Split a note per location, or anchor once and name the other places in the body — whichever the author reads best.

`rounds/1/review/queue_items.json`: the complete item (below) for every row, keyed by row number, except agent-only minor rows. The text the reviewer approves is the text that posts.

The complete item has no ambiguity left: its reader is the PR author, cold, and acts without asking anyone. It carries the row's finding, severity and fix direction, and adds the detail: the symbols and places involved in `issue` and `why`, and in `suggestion` the fix with a code snippet and every other place to change.

```json
{"3": {"title": "...", "severity": "major", "file": "...", "line": 84,
       "issue": "...", "why": "...", "suggestion": "..."}}
```

## Decide

Each step ends when its rows have a decision and the reviewer's reply is recorded.

1. **Reviewer rows** (source `Reviewer` or `Both`): show these rows of the table, with `Fix`, and name `queue_items.json` as the full text that posts. The reviewer replies with exceptions ("approve all except 4, 7"). Record the rest in one call.
2. **Agent-only critical and major rows**: one card each.

   > **#12 · major · `path/File.dart:47`** · Agent
   > **Why:** …
   > **Suggestion:** …
   > **My take:** one sentence, then `agree`, `agree, with a change` or `disagree`
   > approve · edit · discard · expand

3. **Agent-only minor rows**: one list, one line per row stating its impact. The reviewer names the rows to keep; every other row is discarded. Add the complete item of each kept row to `queue_items.json`, then record them with `--from-queue`.

Reviewer answers on a card or an exception:

- **expand**: give the evidence and the full text that would be written, then wait for the next decision.
- **approve**: record the row.
- **edit**: the reviewer names a field or the severity and the change; apply it to the item, record it with `--edited`.
- **discard**: record the row with a few words of reason.

## Record

`walk_item.py` validates each item, creates `final_review.json` on first use and marks the rows. `comment_id` comes from Phase 4.

```bash
# approved rows: items come from queue_items.json
python scripts/walk_item.py add <workspace_path> --section new --rows 1,2,3 --from-queue
# a changed or newly written item: JSON on stdin
python scripts/walk_item.py add <workspace_path> --section new --row 3 [--edited] <<'EOF'
{"title": "...", "severity": "major", "file": "...", "line": 84,
 "issue": "...", "why": "...", "suggestion": "..."}
EOF
python scripts/walk_item.py discard <workspace_path> --rows 4,5 --reason "user is never null"
```

A new session, or one after a compaction, resumes at the first `Pending` row of `review_queue.md`.

**Done when**: no row is `Pending`, every approved item is in `final_review.json`, and the reviewer has answered whether to post.
