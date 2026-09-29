# Phase 4 — Post

**Goal**: get the reviewer's approved list onto the PR, nothing more.

- Only runs after the reviewer's explicit "yes" from Phase 3 — never post on your own initiative, even if reconciliation is obviously finished.
- Post everything in one call — the script parses `rounds/<round>/review/final_review.json` directly and builds each comment body from Issue/Why/Suggestion:
  ```bash
  python scripts/post_all.py <workspace_path>
  ```
  A deletion-only item (`line: null` or `—`) posts file-level (`subject_type: file`, attached to the file, no line — never a bare PR-level comment) automatically, no per-item flag needed. The script is idempotent: an entry that already has a `comment_id` (from a previous run) is skipped, not re-posted, and each successful post writes its `comment_id` and `url` back into `final_review.json` immediately — safe to re-run after a partial failure.
- Run with `--dry-run` first if you want to sanity-check what would post (file/line/title per entry, nothing sent) before doing it for real.
- Report the printed URLs to the reviewer.
- `scripts/post_comment.py` still exists for a genuine one-off — e.g. a single extra comment outside the reconciled list — but the normal Phase-4 path is `post_all.py`, not a per-item loop. Unlike `post_all.py`, a one-off posted this way is never recorded anywhere.

**Done when**: every unposted entry in `final_review.json` (`"new"`) has a `comment_id` and the URLs are shared.
