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

- Writes a scannable visual walkthrough of a checked-out PR
- Runs an independent agent review alongside your own review, then merges both into one list
- Posts, replies, or resolves comments only on the batch you explicitly approve

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
| **1. Walkthrough** | After setup | Grouped, scannable walkthrough of the PR for you to read |
| **2. Independent review** | You confirm you've read the walkthrough | Agent reviews without seeing your notes; you review independently in parallel |
| **3. Reconcile** | You say you're done reviewing | Both reviews merged into one list for you to sign off item by item |
| **4. Post** | You approve the reconciled list | Approved items posted as inline PR comments |
| **5. Re-review** | New commits address a previous round | Delta diff walked through; open items checked as fixed/not fixed; threads resolved or replied to |

## Output layout

```text
<workspace_path>/
  meta.json                         pr_number, owner, repo, branch_name, baseRefName, current_round
  rounds/1/
    round.json                      round, headRefOid
    diff.patch                      full diff, base...HEAD
    walkthrough/index.md
    walkthrough/1.<slug>.md, ...
    review/agent_review.md
    review/reviewer_review.md
    review/final_review.json        source of truth for posting/resolving
  rounds/N/                         round 2+, incremental
```

## Related skills

- [va-visualize](va-visualize.md) — used to render the walkthrough's structural views
