# Phase 2 — Collaborate

## Part A — Independent review

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>` before sending.

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `ticket.md` — ticket requirements and acceptance criteria
- `diff/round-1.patch` — full PR diff (source of truth for what changed)

## Task

Read `<workspace_path>/diff/round-1.patch` and `<workspace_path>/ticket.md`. Do NOT read `walkthrough/` — it would anchor your findings.

Do an independent code review. Look for: correctness bugs, security issues, missing error handling, behavioral gaps vs ticket, and non-blocking improvements.

For each concern, find the exact `+` side line number from the diff hunk (`@@ -x,y +a,b @@`). If no `+` line applies (deletion only), set Lines to `—`.

Write all findings to `<workspace_path>/concerns/round-1-agent.md` — kept separate from the reviewer's own notes so neither anchors the other.

## Output format

Group by severity (critical → major → minor). For each concern:

```
#### <title> — [critical / major / minor] — Round 1
- **File**: `path/to/file`
- **Lines**: 42 or 42-45 or —
- **Issue**: <one line then a code/pseudo-code block showing the problem>
- **Why**: <one line>
- **Suggestion**: <code block showing the fix>
- **Reviewer Feedback**: 
```

Issue and Suggestion are **code-first**: lead with ≤1 line of text, then a code block. No prose paragraphs.

Leave **Reviewer Feedback** blank — the human reviewer fills it in.

Severity: critical = correctness bug or data loss | major = behavioral gap | minor = non-blocking

## Summary

After writing the file, return a brief summary: concern counts by severity, any notable findings.
~~~

### After Return
Relay the sub-agent summary to the reviewer, then go to Part B.

---

## Part B — Reviewer feedback

### Main Agent
Ask the reviewer to confirm:
1. anything they spotted themselves is in `<workspace_path>/concerns/round-1-reviewer.md` (open since the walkthrough)
2. `<workspace_path>/concerns/round-1-agent.md` has **Reviewer Feedback** filled in per item — accept, reject, or additional detail

These files are the primary mechanism — the reviewer works at their own pace in their IDE. Chat feedback is still fine; hold it as `<reviewer_feedback>` for Part C, supplementary rather than a replacement.

---

## Part C — Apply feedback

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>` and `<reviewer_feedback>` before sending (use "none" if the reviewer gave no chat feedback).

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `ticket.md` — ticket requirements and acceptance criteria
- `diff/round-1.patch` — full PR diff (source of truth — use this to validate every concern, agent- or reviewer-authored)
- `concerns/round-1-agent.md` — sub-agent's independent findings, with **Reviewer Feedback** filled in per item
- `concerns/round-1-reviewer.md` — reviewer's own findings, free-form

## Reviewer feedback (chat, supplementary)

<reviewer_feedback>

## Task

Read all four files above. Produce the final, postable concern list at `<workspace_path>/concerns/round-1.md`:

1. **Agent concerns** — honor each item's **Reviewer Feedback** field: drop rejected, keep accepted, revise per additional detail. Blank means not yet reviewed — carry it forward as-is.
2. **Reviewer-authored concerns** — for each item in `round-1-reviewer.md`, verify against the diff. If clearly valid, promote it (fill in File/Lines/Issue/Why/Suggestion, since the note may be informal). If ambiguous or unsupported, use the AskUserQuestion tool to clarify before including it — never silently drop or silently include an unverified claim.
3. **Merge and dedupe** — if a reviewer-authored concern matches an already-accepted agent concern, don't duplicate it; treat it as confirmation of the existing item instead.

Write the merged result, grouped by severity, in the standard format — no `Reviewer Feedback` field, that was only a coordination mechanism between the first two files:

```
#### <title> — [critical / major / minor] — Round 1
- **File**: `path/to/file`
- **Lines**: 42 or 42-45 or —
- **Issue**: <one line then a code/pseudo-code block showing the problem>
- **Why**: <one line>
- **Suggestion**: <code block showing the fix>
```

## Summary

After writing the file, return a brief summary: how many agent concerns were kept vs rejected, how many reviewer concerns were promoted, and how many clarifying questions you asked.
~~~

### After Return
Relay the sub-agent summary to the reviewer, then go to Part D.

---

## Part D — Approval

### Main Agent
Summarize counts from Part C (e.g. "N agent concerns kept, N rejected, N reviewer concerns added, N clarifying questions asked"), then ask: *"Ready to post? (`yes` / `no`)"*
