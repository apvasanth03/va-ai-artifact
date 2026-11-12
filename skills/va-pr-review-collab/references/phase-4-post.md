# Phase 4 — Post

**Goal**: get the reviewer's approved list onto the PR, nothing more.

- Only runs after the reviewer's explicit "yes" — never post on your own initiative, even if the walk is obviously finished. Ask with counts only (items to post, discarded); the reviewer approved each item during the walk.
- Post everything in one call — the script parses `rounds/<round>/review/final_review.json` directly and builds each comment body from Issue/Why/Suggestion:
  ```bash
  python scripts/post_all.py <workspace_path>
  ```
  A deletion-only item (`line: null` or `—`) posts file-level (`subject_type: file`, attached to the file, no line — never a bare PR-level comment) automatically, no per-item flag needed. The script is idempotent: an entry that already has a `comment_id` (from a previous run) is skipped, not re-posted, and each successful post writes its `comment_id` and `url` back into `final_review.json` immediately — safe to re-run after a partial failure.
- Run with `--dry-run` first if you want to sanity-check what would post (file/line/title per entry, nothing sent) before doing it for real.
- Report the printed URLs to the reviewer.
- `scripts/post_comment.py` still exists for a genuine one-off — e.g. a single extra comment outside the reconciled list — but the normal Phase-4 path is `post_all.py`, not a per-item loop. Unlike `post_all.py`, a one-off posted this way is never recorded anywhere.

## Verdict

After the comments are posted (and, in a re-review, after `resolve_threads.py`), the PR gets one overall verdict. Never post it on your own initiative.

1. `python scripts/post_verdict.py <workspace_path> --draft` writes `review/verdict.md` and prints a suggested event:
   - `REQUEST_CHANGES` — any new or still-open item is critical or major.
   - `COMMENT` — only minor items are new or still open.
   - `APPROVE` — nothing new, nothing open.
2. Replace the `<summary>` line with one plain sentence on the PR's state. Keep the rest of the template as is: header, summary, one `Posted:` counts line, and a `Blocking` (request changes) or `Still open` list only when it applies.
3. Show the reviewer the suggested verdict and the exact body. The reviewer may change the verdict or the text; if the verdict changes, re-run `--draft --event <EVENT>` (it rewrites the header and lists; re-add the summary sentence). Wait for an explicit yes — this is its own approval, separate from the comment batch.
4. `python scripts/post_verdict.py <workspace_path> --event <EVENT>` (`--dry-run` first if unsure). It refuses a leftover `<summary>`, a header that doesn't match the event, a moved PR head, and a second verdict for the same round. It records `verdict` {event, review_id, url} in `final_review.json`.
5. Share the URL. On your own PR GitHub rejects approve and request-changes; post `COMMENT` instead.

**Done when**: every unposted entry in `final_review.json` (`"new"`) has a `comment_id`, the URLs are shared, and the approved verdict is posted.
