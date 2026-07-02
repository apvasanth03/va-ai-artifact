---
name: va-pr-review-assist
description: PR review assistant skill. Use when the user wants help reviewing a pull request — guides them through changes group-by-group, collaboratively surfaces concerns, and posts agreed inline comments via gh CLI.
disable-model-invocation: true
---

# PR Review Assistant

## Task

Guide the reviewer through a PR group-by-group, collaboratively surface concerns, and post agreed comments as inline PR comments. Supports multiple review rounds in the same session. Reviewer makes the final call on every concern — never review or post autonomously.

## Required Information

- `workspace_path` — directory for this review session. Always ask — no default.
- PR branch checked out locally — confirm before starting
- Ticket context: title, description, acceptance criteria — or reviewer says *"use PR description"*

If any are missing, ask before proceeding.

## Context

Main agent **orchestrates only** — sub-agents do all reading, reviewing, and posting. Main agent holds only `workspace_path` — no phase outputs in context. All shared state lives under `<workspace_path>`.

`gh` is available for GitHub interactions. Use local `git` and filesystem reads wherever possible; `gh` only for PR metadata and posting.

### Workspace Layout

```
<workspace_path>/
  meta.json               — PR metadata: pr_number, owner, repo, branch_name, baseRefName, headRefOid, reviewed_oid, round
  ticket.md               — ticket context written in Phase 0
  diff/
    round-1.patch         — full diff, generated files excluded, round 1
    round-2.patch         — incremental diff, round 2+
  walkthrough/
    round-1.md            — all groups, round 1
    round-2.md            — single-pass, round 2+
  concerns/
    round-N-agent.md      — sub-agent's independent findings for round N (Phase 2 Part A, or Phase 4 Step 4 Part 2), Reviewer Feedback field filled in by reviewer
    round-N-reviewer.md   — reviewer's own findings for round N, free-form; created empty at Phase 0 Step 4 (round 1) or Phase 4 Step 1 (round N)
    round-N.md            — final merged, postable Concern Items for round N (round-N-agent.md + round-N-reviewer.md, verified against the diff) — output of Phase 2 Part C or Phase 4 Step 6, posted in Phase 3 / Phase 4 Step 7
    review-round-N.md     — addressed/open summary for round N, written by Phase 4 Step 4 Part 1
    resolve-round-N.md    — Thread IDs to resolve (one per line), written in Phase 4 Step 6
  comments/
    comments.md           — active posted concerns (with Comment ID, Thread ID, URL)
    comments_resolved.md  — resolved concerns (moved here)
```

### Data Formats

Used in `concerns/round-N-agent.md` (Phase 2 Part A — sub-agent's independent findings, before reviewer or merge):
```markdown
#### <Issue title> — [critical / major / minor] — Round N
- **File**: `path/to/file`
- **Lines**: 42 or 42-45 or — (deletion-only)
- **Issue**: <one line max — then a code/pseudo-code snippet showing the problem>
- **Why**: <one line — no prose blocks>
- **Suggestion**: <code snippet showing the fix — minimal prose>
- **Reviewer Feedback**: <blank when written; reviewer fills in accept / reject / additional detail>
```

`concerns/round-N-reviewer.md` has no fixed format — it's the reviewer's own free-form notes, one item per finding, file/line mentioned if known. Phase 2 Part C verifies each note against the diff before promoting it into the final list.

Used in `concerns/round-N.md` (Phase 2 Part C output — final, merged, postable list; no `Reviewer Feedback` field, that was only a coordination mechanism between the two files above):
```markdown
#### <Issue title> — [critical / major / minor] — Round N
- **File**: `path/to/file`
- **Lines**: 42 or 42-45 or — (deletion-only)
- **Issue**: <one line max — then a code/pseudo-code snippet showing the problem>
- **Why**: <one line — no prose blocks>
- **Suggestion**: <code snippet showing the fix — minimal prose>
```

Keep Issue and Suggestion **code-first**: lead with a short phrase, then a code block. Avoid multi-line prose explanations — if it can be shown in code, show it in code.

Used in `comments/comments.md` (after posting — Phase 3 adds the last three fields; Phase 4 Step 7 appends `Replied` when a reply is posted):
```markdown
#### <Issue title> — [critical / major / minor] — Round N
- **File**: `path/to/file`
- **Lines**: 42 or 42-45
- **Issue**: <what is wrong — use code/pseudo-code>
- **Why**: <why it matters>
- **Suggestion**: <how to fix — prefer code snippet>
- **Comment ID**: <integer id from gh api response>
- **Thread ID**: <graphql node id, e.g. PRRT_...>
- **URL**: <github comment url>
- **Replied Round N**: <reason summary>  ← optional; added when a reply is posted
```

Used in `concerns/review-round-N.md` (Phase 4 Step 5 — addressed/open summary):
~~~markdown
### Addressed
#### <concern title> — Round <original_round>
- **Thread ID**: PRRT_...
- **Comment ID**: <integer>
- **Proof**: <evidence from diff — file:line reference or code snippet>

### Still Open
#### <concern title> — Round <original_round>
- **Thread ID**: PRRT_...
- **Comment ID**: <integer>
- **Reason**: <what was expected vs what the diff shows>
~~~

Used in Phase 4 Step 6 (reviewer summary presented by main agent):
```
### Addressed (N)
- <title> — <proof summary>

### Still Open (N)
- <title> — <reason summary>

### New Issues (N)
<Concern Items>
```

### Severity Criteria

- **critical** — correctness bug or data loss
- **major** — behavioral regression or missing requirement
- **minor** — style or non-blocking suggestion

## Available Scripts

- **`scripts/setup.py`** — Phase 0: create workspace dirs, fetch PR metadata, write `meta.json`, filter out generated files, save diff
- **`scripts/post_concerns.py`** — Phase 3 / Phase 4 Step 7: post concerns to GitHub, append to `comments.md`
- **`scripts/prepare_round.py`** — Phase 4 Step 1: fetch new commits, save incremental diff, update `headRefOid`; prints `{new_oid, round_n, force_pushed}` or `{error: "no_new_commits"}` + exit 1
- **`scripts/sync_resolved.py`** — Phase 4 Step 2: sync resolved thread state from GitHub
- **`scripts/resolve_threads.py`** — Phase 4 Step 7: resolve threads via GraphQL, move to `comments_resolved.md`
- **`scripts/update_meta.py`** — Phase 4 Step 8: update `reviewed_oid`, `headRefOid`, `round` in `meta.json`

## Workflow

Read the reference file for the current phase before executing it — load on demand, not all upfront.

| Phase | Trigger | Reference |
|---|---|---|
| **Phase 0 — Setup** | Start of every review | `references/phase-0-setup.md` |
| **Phase 1 — Analysis & Walkthrough** | After Phase 0 | `references/phase-1-walkthrough.md` |
| **Phase 2 — Collaborate** | After Phase 1 | `references/phase-2-collaborate.md` |
| **Phase 3 — Post** | Reviewer approves concerns | `references/phase-3-post.md` |
| **Phase 4 — Re-review** | Reviewer says *"re-review"* | `references/phase-4-rereview.md` |

---

## Guidelines

### Reference File Convention

Each phase reference file uses three `###` sections per step so the main agent always knows what to do:

| Section | Audience | Meaning |
|---|---|---|
| `### Main Agent` | Main agent | Direct instruction — run a script, spawn a sub-agent, collect input, or redirect the reviewer |
| `### Sub-agent Prompt` | Main agent | Pass this text verbatim to the Agent tool after substituting all `<placeholder>` values |
| `### After Return` | Main agent | Do this once the sub-agent completes |

Steps that only involve a script call or direct main-agent action omit `### Sub-agent Prompt` and `### After Return`.

Every sub-agent prompt begins with the no-spawn rule: *"Perform all work directly using your tools — do not use the Agent tool or spawn further agents."* Never remove it when constructing sub-agent prompts.

### Review Rules

- Line numbers for inline comments must come from the **diff hunk** (`@@ -x,y +a,b @@`) — use the `+` side line numbers. Captured by review sub-agents, not the post step.
- For deletion-only changes (no `+` line) — set `Lines: —` and post as a general PR comment. General comments are not review threads and cannot be resolved or synced in Phase 4.
- Sub-agents must read from `diff/round-N.patch` — never call `gh pr diff` or re-fetch via `git`
- Never post or resolve without explicit reviewer approval
