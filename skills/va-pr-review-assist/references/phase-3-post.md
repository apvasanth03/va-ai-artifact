# Phase 3 — Post

## Step 1 — Post concerns

### Main Agent
Spawn a sub-agent with the prompt below. Substitute `<workspace_path>` before sending.

### Sub-agent Prompt

~~~
You are a worker sub-agent in a PR review session. Perform all work directly using your tools (Read, Write, Bash) — do not use the Agent tool or spawn further agents.

Workspace: `<workspace_path>`
- `meta.json` — PR metadata (pr_number, owner, repo, headRefOid — used as commit_id for inline comments)
- `concerns/round-1.md` — approved concern items to post

## Task

Run using the Bash tool:
```
python scripts/post_concerns.py <workspace_path> <workspace_path>/concerns/round-1.md
```

Posts each concern as an inline comment (or general PR comment if Lines is —), fetches Thread IDs via GraphQL, and appends each Concern Item to `<workspace_path>/comments/comments.md` with Comment ID, Thread ID, and URL populated.

## Summary

After running the script, return a brief summary: posted counts, inline vs general, any errors.
~~~

### After Return
Relay the sub-agent summary to the reviewer.
