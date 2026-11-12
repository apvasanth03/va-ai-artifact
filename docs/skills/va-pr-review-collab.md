# va-pr-review-collab

Collaborative PR review — you and the agent review independently, then merge and post together.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Workflow](#workflow)
- [Output layout](#output-layout)
- [Related skills](#related-skills)

## What it does

- Writes a scannable visual walkthrough of a checked-out PR, from sections you approve first
- Runs an independent agent review alongside your own review, then merges both into one list
- Walks you through that list one item at a time, saving each decision as you make it
- Posts, replies, or resolves comments only on the batch you explicitly approve
- Suggests an overall verdict (approve, request changes, comment) and posts it only after you approve it

## When to reach for it

- Reviewing a checked-out PR and want a second, independent pass before posting comments
- Re-reviewing a PR after new commits address prior feedback

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)
- PR branch checked out locally and current with its remote

## Input

- `workspace_path` — a directory to store this review session's state (asked for, no default)
- Ticket/PR intent — pulled automatically from `gh pr view`

## Workflow

| Phase | Trigger | What happens |
|---|---|---|
| **0. Setup** | Start of session | Collect workspace path, generate diff, initialize round |
| **1. Walkthrough** | After setup | Agent proposes the walkthrough sections in chat; you adjust and approve them; then a scannable walkthrough is written. Large PRs split into grouped files |
| **2. Independent review** | You confirm you've read the walkthrough | Agent reviews without seeing your notes and records short findings; you review independently in parallel. Agent shares nothing until you say you're done |
| **3. Reconcile** | You say you're done reviewing | Both reviews merged into one queue. You go through it item by item: approve, edit, discard, or ask for more detail. Each decision is saved immediately, so a session can be resumed |
| **4. Post** | You approve the reconciled list | Approved items posted as inline PR comments; then the agent drafts a short verdict (suggested outcome, one-line summary, counts, blocking or still-open items) and posts it as the PR review once you approve it |
| **5. Re-review** | New commits address a previous round | Walkthrough of the new changes; both of you check earlier items as fixed/not fixed, with the author's replies on each comment shown alongside, and look for new issues; you confirm statuses in one pass, then walk new findings one at a time; threads resolved or replied to, then new comments posted |

### Sign-off rules

- You approve the walkthrough sections before it is written
- The agent's findings stay hidden until you finish your own review
- You approve each item during the walk
- Posting is asked per batch, as counts only (e.g. items to post, items discarded); an earlier yes doesn't cover a later batch
- The verdict is approved separately, after the comments are posted; it is suggested by rule (any critical/major open or new item → request changes; only minor → comment; nothing open → approve) and you can change it

## Output layout

```text
<workspace_path>/
  meta.json                         pr_number, owner, repo, branch_name, baseRefName, current_round
  rounds/1/
    round.json                      round, headRefOid
    diff.patch                      full diff, base...HEAD
    walkthrough.md                  the walkthrough (overview only when a large PR is split)
    walkthrough/<group>.md          large PRs only: one file per group of sections
    review/agent_review.md          agent's findings, one row each
    review/reviewer_review.md       your free-form notes
    review/review_queue.md          merged list, with a decision per item
    review/final_review.json        approved items, source of truth for posting/resolving
    review/verdict.md               overall verdict body
  rounds/N/                         round 2+, incremental
```

## Related skills

- [va-visualize](va-visualize.md) — used to render the walkthrough's structural views
