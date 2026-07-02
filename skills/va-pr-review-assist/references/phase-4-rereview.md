# Phase 4 — Re-review

**Triggered**: reviewer says *"re-review"* in the same session.

---

## Step 1 — Prepare round

### Main Agent
```bash
python scripts/prepare_round.py <workspace_path>
```

Fetches latest commits, checks for force-push, saves incremental diff to `diff/round-N.patch`, updates `headRefOid` in `meta.json`. Prints JSON:
```json
{"new_oid": "...", "round_n": N, "force_pushed": false}
```

- If `error: no_new_commits` — tell reviewer there are no new commits and stop.
- If `force_pushed: true` — warn reviewer: *"Branch was force-pushed. Incremental diff covers last reviewed commit to new tip; history may have been rewritten."*

Hold `new_oid` and `round_n` in context — needed for Step 8.

Write `<workspace_path>/concerns/round-N-reviewer.md` (same template as Phase 0 Step 4, `N` substituted):
```markdown
# Reviewer Concerns — Round N

Add your own concerns below as you go through the walkthrough. Free-form is fine — one item per finding, mention file/line if you can.
```

---

## Step 2 — Sync resolved state

### Main Agent
```bash
python scripts/sync_resolved.py <workspace_path>
```

Queries GitHub for threads resolved via the UI. Moves those entries from `comments.md` → `comments_resolved.md`. Entries remaining in `comments.md` are open concerns.

> Note: handles up to 100 review threads. Flag if the PR exceeds this.

---

## Step 3 — Walkthrough

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>` and `N` (round number from Step 1) before sending.

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `diff/round-N.patch` — incremental diff for this round (source of truth)
- `walkthrough/` — prior round walkthroughs (optional reference for context)

## Task

Read `<workspace_path>/diff/round-N.patch`. Optionally read prior walkthroughs in `<workspace_path>/walkthrough/` for context.

Write a single-pass walkthrough of all changes in the incremental diff to `<workspace_path>/walkthrough/round-N.md`. Use code/pseudo-code. Free-form — no fixed template.

## Summary

After writing the file, return a brief summary: files changed, any connection to prior concerns.
~~~

### After Return
Relay the sub-agent summary to the reviewer, then tell them: *"Walkthrough written to `<workspace_path>/walkthrough/round-N.md` — open it in your IDE. As you go through it, jot down anything you spot into `<workspace_path>/concerns/round-N-reviewer.md`. Come back when ready."*

If reviewer has questions, spawn a new sub-agent (same no-spawn rule) with `<workspace_path>` and the question.

---

## Step 4 — Review

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>` and `N` before sending.

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `diff/round-N.patch` — incremental diff for this round (source of truth)
- `ticket.md` — ticket requirements and acceptance criteria
- `comments/comments.md` — all currently open posted concerns (Thread ID, Comment ID per entry)

## Task

Read `<workspace_path>/diff/round-N.patch`, `<workspace_path>/comments/comments.md`, and `<workspace_path>/ticket.md`.

**Part 1 — Addressed/open assessment**: For each open concern in `comments.md`, determine whether the incremental diff addresses it.

Write to `<workspace_path>/concerns/review-round-N.md`:

```
### Addressed
#### <concern title> — Round <original_round>
- **Thread ID**: PRRT_...
- **Comment ID**: <integer>
- **Proof**: <file:line reference or code snippet from diff>

### Still Open
#### <concern title> — Round <original_round>
- **Thread ID**: PRRT_...
- **Comment ID**: <integer>
- **Reason**: <what was expected vs what the diff shows>
```

**Part 2 — New issues**: Find new issues in the incremental diff. Write new Concern Items to `<workspace_path>/concerns/round-N-agent.md` — kept separate from the reviewer's own notes in `round-N-reviewer.md` so neither anchors the other. Same format as `comments.md` entries (bold field labels, code-first Issue and Suggestion), plus one extra blank field per item:
```
- **Reviewer Feedback**: 
```
Leave it blank — the human reviewer fills it in.

## Summary

After writing both files, return a brief summary: addressed/still-open/new issue counts.
~~~

### After Return
Relay the sub-agent summary to the reviewer, then go to Step 5.

---

## Step 5 — Reviewer feedback

### Main Agent
Tell reviewer: *"Summary at `<workspace_path>/concerns/review-round-N.md` — which addressed concerns should be resolved? For new issues: go through `<workspace_path>/concerns/round-N-agent.md` and fill in **Reviewer Feedback** per item, and add anything you spotted yourself to `<workspace_path>/concerns/round-N-reviewer.md`."*

Confirm both are done before moving on. Chat feedback is still fine — hold it as `<reviewer_feedback>` for Step 6, supplementary rather than the primary mechanism.

---

## Step 6 — Apply feedback

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>`, `N`, and `<reviewer_feedback>` before sending.

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `diff/round-N.patch` — incremental diff (use this to validate every concern, agent- or reviewer-authored)
- `concerns/review-round-N.md` — addressed/open summary with Thread IDs and Comment IDs
- `concerns/round-N-agent.md` — sub-agent's independent new-issue findings, with **Reviewer Feedback** filled in per item
- `concerns/round-N-reviewer.md` — reviewer's own findings, free-form
- `comments/comments.md` — all open posted concerns

## Reviewer feedback (chat, supplementary)

<reviewer_feedback>

## Task

Read all files above. Apply reviewer feedback:

1. **Threads to resolve** — write their Thread IDs (from `review-round-N.md`) to `<workspace_path>/concerns/resolve-round-N.md`, one per line (e.g. `PRRT_kwDO...`).
2. **New concerns** — produce the final, postable list at `<workspace_path>/concerns/round-N.md`: honor each `round-N-agent.md` item's **Reviewer Feedback** field (drop rejected, keep accepted, revise per detail; blank = not yet reviewed, carry forward as-is); verify each `round-N-reviewer.md` item against the diff, promoting valid ones (fill in File/Lines/Issue/Why/Suggestion) and using AskUserQuestion for anything ambiguous or unsupported; dedupe against already-accepted agent concerns. No `Reviewer Feedback` field in this final file — that was only a coordination mechanism.

## Summary

After writing the files, return a brief summary: threads to resolve, still-open count, agent concerns kept/rejected, reviewer concerns promoted, clarifying questions asked.
~~~

### After Return
Use the sub-agent summary to present the approval prompt to the reviewer: *"Proceed? This will resolve [N] threads, reply to [N] still-open, post [N] new concerns. (`yes` / `no`)"*

---

## Step 7 — Resolve + Reply + Post

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>` and `N` before sending.

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `meta.json` — PR metadata (owner, repo, pr_number, headRefOid)
- `concerns/review-round-N.md` — addressed/open summary
- `concerns/resolve-round-N.md` — Thread IDs to resolve (one per line)
- `concerns/round-N.md` — new concern items to post
- `comments/comments.md` — open posted concerns

## Task

Three operations in order:

**1. Resolve** confirmed threads:
```
python scripts/resolve_threads.py <workspace_path> <workspace_path>/concerns/resolve-round-N.md
```

**2. Reply** to each "Still Open" entry in `review-round-N.md` using its `Comment ID`. Read `owner`, `repo` from `meta.json`.
```
gh api repos/<owner>/<repo>/pulls/comments/<comment_id>/replies \
  --method POST -f body="**Still open — Round N**: <Reason>"
```
After each reply, use Edit to insert `- **Replied Round N**: <reason summary>` within the matching concern block in `comments.md` (after the `URL` field line). Substitute the real round number — not the letter N. This edit must happen after operation 1 (which rewrites `comments.md`) and before operation 3 (which appends to it).

**3. Post** new concerns:
```
python scripts/post_concerns.py <workspace_path> <workspace_path>/concerns/round-N.md
```

After all three: resolved entries are in `comments_resolved.md`, still-open entries in `comments.md` have `Replied Round N` added, new entries are appended to `comments.md`.

## Summary

After completing all three operations, return a brief summary: resolved/replied/posted counts, any errors.
~~~

### After Return
Relay the sub-agent summary to the reviewer, then go to Step 8.

---

## Step 8 — Update meta.json

### Main Agent
```bash
python scripts/update_meta.py <workspace_path> <new_oid> <round_n>
```

`new_oid` and `round_n` come from the Step 1 output held in context. Updates `reviewed_oid`, `headRefOid`, and `round` in `meta.json`.
