---
name: va-pr-review-collab
description: Collaborative PR review. Writes a visual walkthrough of a checked-out PR, collects an independent agent review and the reviewer's review, and posts only the list the reviewer approves.
disable-model-invocation: true
---

# PR Review — Collaborative

## Task

Propose the walkthrough's sections in chat and write the walkthrough once the reviewer approves them (use `va-visualize` for structural views). Then two independent reviews — yours as a compact ledger in `agent_review.md`, theirs free-form in `reviewer_review.md` — merged into `review_queue.md` and decided in three steps by weight (reviewer rows as one table, agent majors as cards, agent minors as one keep-list). Each step's approved items are written to `final_review.json` in one call.

## Required Information

- `workspace_path` — directory for this review session. Ask — no default.
- PR branch checked out locally and current with its remote. Confirm before starting.

Ticket and PR intent come from `gh pr view`.

## Gates

1. **Sections.** The walkthrough is written from a section list the reviewer approved in chat.
2. **Blind review.** Write your findings without reading `reviewer_review.md`. They reach the reviewer in the reconcile steps, after the reviewer says their pass is done.
3. **Re-review.** On a later round, verify previous open items and inspect the delta diff independently in `agent_review.md` and `reviewer_review.md`. Read `references/phase-5-rereview.md` when new commits address a previous round.
4. **Sign-off.** The reviewer approves each item in the reconcile steps (listed in the table, card or keep-list), each posting batch separately (asked as counts), and the final verdict separately. An earlier yes does not cover a later batch or the verdict.
5. **Structured review data.** `final_review.json` is the sole source of truth (`new`, `unresolved`, and `resolved` items) used by post and resolve scripts, and `scripts/walk_item.py` is how items get into it.

## Workspace

```bash
python scripts/setup.py <workspace_path> [--exclude glob ...]
```

Round 1. Refuses to run if `meta.json` already exists. Machine-generated files and lockfiles are skipped automatically; use `--exclude` to scope out test files or fixtures.

```
<workspace_path>/
  meta.json                         pr_number, owner, repo, branch_name, baseRefName, current_round
  rounds/1/
    round.json                      {round, headRefOid}
    diff.patch                      full diff, base...HEAD
    walkthrough.md                  one file; a large PR adds walkthrough/<group>.md files (phase 1)
    review/agent_review.md              compact ledger: one row per finding, issue only
    review/reviewer_review.md           free-form notes
    review/review_queue.md              Phase 3: merged queue with a Decision per row
    review/queue_items.json             Phase 3: complete item per row number; the text that posts
    review/final_review.json            written per reconcile step
    review/verdict.md                   overall verdict body, drafted after posting
  rounds/N/                         see references/phase-5-rereview.md
```

`gh` reads and writes GitHub. Local `git` supplies the diff. A TLS error from `gh` (`x509: OSStatus -26276` or similar) inside the tool sandbox is a sandbox failure — rerun that command with the sandbox disabled.

## Workflow

Load the reference for the current phase. Leave the others unread.

| Phase | Trigger | Reference |
|---|---|---|
| **0 — Setup** | Start of session | `references/phase-0-setup.md` |
| **1 — Walkthrough** | After Phase 0 | `references/phase-1-walkthrough.md` |
| **2 — Independent Review** | Reviewer confirms after walkthrough | `references/phase-2-review.md` |
| **3 — Reconcile** | Reviewer says they're done reviewing | `references/phase-3-reconcile.md` |
| **4 — Post** | Reviewer approves the reconciled list | `references/phase-4-post.md` |
| **5 — Re-review** | New commits address a previous round | `references/phase-5-rereview.md` |

## Review Data (`final_review.json`)

Written in Phase 3 & 5, one item per `walk_item.py add`, as the single source of truth for posting and thread resolution.

```json
{
  "new": [
    {
      "title": "<summary>",
      "severity": "critical | major | minor",
      "file": "path/to/file",
      "line": 42,
      "issue": "<one line or snippet>",
      "why": "<rationale>",
      "suggestion": "Fix with:\n```dart\nfinal x = unwrap(y);\n```"
    }
  ],
  "unresolved": [
    {
      "title": "<original title>",
      "comment_id": 123456789,
      "status": "Not Fixed | Partially Fixed",
      "evidence": "<reason/snippet>",
      "reply": "<optional comment thread reply>"
    }
  ],
  "resolved": [
    {
      "title": "<original title>",
      "comment_id": 123456789,
      "status": "Fixed | Moot",
      "evidence": "<verification proof>",
      "reply": "<optional resolution note>"
    }
  ]
}
```

- Text fields (`suggestion`, `issue`, `why`, `evidence`, `reply`) support rich Markdown (fenced code blocks with language tags, lists, inline backticks).
- `line`: diff `+`-side line number, or `null` for deletion-only (posts file-level). Check with `scripts/diff_lines.py <workspace> <file>`.
- `severity`: `critical` (bug / data loss), `major` (behavioral gap), `minor` (non-blocking).
- `verdict` (optional, top level): `{event, review_id, url}`, written by `post_verdict.py` once the round's verdict is posted.
- `status`: `Fixed` (landed), `Moot` (code moved/gone), `Partially Fixed` (part remains), `Not Fixed` (unchanged).

## Scripts

All of these live in this skill's `scripts/` directory. They default to `current_round` in `meta.json`. Pass `--round N` when you mean another round.

- `scripts/setup.py <workspace> [--exclude glob ...]` — round 1.
- `scripts/setup.py <workspace> --round N [--exclude glob ...] [--include-base-merge]` — N = current + 1 starts the next round; base-branch merge changes are left out of the delta unless `--include-base-merge`. Pre-populates open items from previous round. N = current refreshes head and diff in place. Excludes from round 1 persist automatically.
- `scripts/diff_lines.py <workspace> <file> [--round N]` — `+`-side hunk ranges for `Line`.
- `scripts/walk_item.py add|discard <workspace> ...` — record decisions (`--row N` or `--rows 1,2,3`; `--from-queue` reads items from `queue_items.json`): validate them, write `final_review.json`, mark the `review_queue.md` rows. Usage in `references/phase-3-reconcile.md`.
- `scripts/post_all.py <workspace> [--round N] [--dry-run]` — posts unposted new items from `final_review.json`.
- `scripts/post_comment.py <workspace> [--round N]`
- `scripts/post_verdict.py <workspace> --draft | --event APPROVE|REQUEST_CHANGES|COMMENT [--round N] [--dry-run] [--force]` — drafts `review/verdict.md` (`--draft [--event X]`) and posts it as the overall PR review, after the comments are posted and the reviewer approves. See `references/phase-4-post.md`.
- `scripts/resolve_threads.py <workspace> [--round N] [--dry-run] [--force]` — resolves fixed threads and updates open threads with why they are not resolved from `final_review.json`. Run before `post_all.py`. See `references/phase-5-rereview.md`.
