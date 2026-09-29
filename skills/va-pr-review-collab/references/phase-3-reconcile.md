# Phase 3 — Reconcile

**Goal**: one final list, item by item, with the reviewer as tiebreaker — the agent's review is input, not a veto. This is round 1's reconcile; a re-review round's reconcile is Phase 5's job.

- Combine `rounds/1/review/agent_review.md` and `rounds/1/review/reviewer_review.md` into one ordered set — interleaved, not reviewer-list-then-agent-list, so neither feels like an afterthought. Where an agent item and a reviewer item clearly describe the same thing, merge them into one entry.
- Present the combined set to the reviewer as a consolidated review table:
  | # | Severity | File:Line | Source (Agent / Reviewer / Both) | Issue Summary | Recommendation (Keep / Discard) |
  The reviewer can review the entire set at a glance and approve/adjust in a single turn (e.g. "Discard #3, others LGTM"). If discussion is needed on specific items, address those directly.
- Write the approved items to `rounds/1/review/final_review.json` as the sole source of truth (`{"new": [...], "unresolved": [], "resolved": []}`). Discarded items are not written.
- `Line:` is one number (`42`), or `null` / `—` for a deletion-only finding. A finding spanning several lines or spots still gets one anchor line (its most relevant/primary one); say the rest ("whole file", other line numbers) in the Issue/Why text instead. Re-check with `scripts/diff_lines.py <workspace_path> <file>` for any item carried over from a reviewer note that didn't already cite a verified line.
- Never add a `comment_id` field by hand — it doesn't exist until Phase 4 posts the item.
- Once every item is decided, summarize the counts and ask whether to post.

**Done when**: every item from both files has a keep/discard decision, `final_review.json` is written, and the reviewer has said yes or no to posting.
