# Phase 4 — Post

**Goal:** get the reviewer's approved list onto the PR, nothing more.

## Post the comments

1. **Ask first.** Post only after the reviewer's explicit "yes", never on your own initiative, even when the reconcile is obviously finished. Ask with counts only (items to post, discarded); the reviewer already approved each item in the reconcile steps.
2. **Post everything in one call.** The script reads `rounds/<round>/review/final_review.json` and builds each comment body from Issue, Why and Suggestion.
   ```bash
   python scripts/post_all.py <workspace_path> [--dry-run]
   ```
3. **Report** the printed URLs to the reviewer.

How `post_all.py` behaves:

- **Deletion-only items** (`line: null` or `—`) post file-level automatically (`subject_type: file`, attached to the file with no line), never as a bare PR-level comment.
- **Idempotent:** an entry that already has a `comment_id` is skipped. Each successful post writes its `comment_id` and `url` back into `final_review.json` at once, so a re-run after a partial failure is safe.
- **`--dry-run`** prints file, line and title per entry and sends nothing; use it to sanity-check first.

`scripts/post_comment.py` is for a genuine one-off, such as one extra comment outside the reconciled list. The normal path is `post_all.py`, not a per-item loop. A one-off posted this way is never recorded anywhere.

## Verdict

After the comments are posted (and in a re-review, after `resolve_threads.py`), the PR gets one overall verdict. Never post it on your own initiative.

1. **Draft.** `python scripts/post_verdict.py <workspace_path> --draft` writes `review/verdict.md` and prints a suggested event:

   | Event | When |
   |---|---|
   | `REQUEST_CHANGES` | any new or still-open item is critical or major |
   | `COMMENT` | only minor items are new or still open |
   | `APPROVE` | nothing new, nothing open |

2. **Fill the summary.** Replace the `<summary>` line with one plain sentence on the PR's state. Keep the rest of the template as is: header, summary, one `Posted:` counts line, and a `Blocking` (request changes) or `Still open` list only when it applies.
3. **Get approval.** Show the reviewer the suggested verdict and the exact body. The reviewer may change the verdict or the text; if the verdict changes, re-run `--draft --event <EVENT>` (it rewrites the header and lists; re-add the summary sentence). Wait for an explicit yes; this approval is separate from the comment batch.
4. **Post.** `python scripts/post_verdict.py <workspace_path> --event <EVENT>` (`--dry-run` first if unsure). It refuses a leftover `<summary>`, a header that doesn't match the event, a moved PR head, and a second verdict for the same round. It records `verdict` {event, review_id, url} in `final_review.json`.
5. **Share the URL.** On your own PR, GitHub rejects approve and request-changes; post `COMMENT` instead.

**Done when:** every unposted entry in `final_review.json` (`"new"`) has a `comment_id`, the URLs are shared, and the approved verdict is posted.
