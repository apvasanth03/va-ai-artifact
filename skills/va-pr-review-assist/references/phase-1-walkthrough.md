# Phase 1 — Analysis & Walkthrough

## Step 1 — Generate walkthrough

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>` before sending.

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `ticket.md` — ticket requirements and acceptance criteria
- `diff/round-1.patch` — full PR diff (source of truth for what changed)

## Task

Read `<workspace_path>/ticket.md` and `<workspace_path>/diff/round-1.patch`.

Group changed files by feature concern — not by layer. Files implementing the same change across layers belong in one group. Skip generated/build-output files (note count). Check ticket alignment. For each group, explain what changed and why using code/pseudo-code. Include a mermaid diagram of the overall change flow. Batch trivial one-liner changes across files into a single step.

Write the walkthrough to `<workspace_path>/walkthrough/round-1.md` using this structure:

```
## PR: <title>

**Purpose**: <2–3 sentences>
**Base**: <baseRefName> | **Files**: <count> (<N> generated, skipped)

### Ticket Alignment
- ✅ / ⚠️ <requirement> → <status>

### Change Flow
[mermaid diagram]

---

## Group 1: <Name>
> <what it does, how it connects to the next group>
- Files: `path/file`

### `path/file`
<explanation — use code/pseudo-code>

---

## Group N: ...
```

## Summary

After writing the file, return a brief summary: groups, files covered, ticket alignment.
~~~

### After Return
Relay the sub-agent summary to the reviewer, then tell them: *"Walkthrough written to `<workspace_path>/walkthrough/round-1.md` — open it in your IDE. As you go through it, jot down anything you spot into `<workspace_path>/concerns/round-1-reviewer.md` — no format required. Come back when ready or if you have questions."*

If reviewer has questions, spawn a new sub-agent (same no-spawn rule applies) with `<workspace_path>` and the question — it reads `walkthrough/round-1.md` and relevant diff sections to answer. Main agent does not read any files itself.

After reviewer confirms ready, ask: *"Ready for the review phase?"*
