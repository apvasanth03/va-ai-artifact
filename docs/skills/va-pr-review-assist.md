# va-pr-review-assist

**Invocation**: `/va-pr-review-assist` (explicit only — `disable-model-invocation: true`)

Guides the reviewer through a pull request group-by-group, collaboratively surfaces concerns, and posts agreed comments as inline GitHub review comments. Reviewer makes the final call on every concern — the skill never reviews or posts autonomously.

---

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)
- PR branch checked out locally and up to date (`git pull origin <branch>`)
- Python 3 available in `PATH`

---

## Usage

Start a session:
```
/va-pr-review-assist
```

Re-review after new commits are pushed (say this during the session):
```
re-review
```

The skill will ask for:
- **Workspace path** — a directory to store all review state (e.g. `.vasanth/ai-workspace/review/my-feature`)
- **Ticket context** — title, description, and acceptance criteria; or say *"use PR description"* to skip

---

## Workflow

| Phase | Trigger | What happens |
|---|---|---|
| **Phase 0 — Setup** | Start of every review | Collect ticket context, run `setup.py`, create workspace |
| **Phase 1 — Analysis & Walkthrough** | After Phase 0 | Sub-agent generates grouped walkthrough; reviewer reads in IDE |
| **Phase 2 — Collaborate** | After Phase 1 | Sub-agent does independent review; reviewer adds/edits; concerns merged |
| **Phase 3 — Post** | Reviewer approves | Sub-agent posts concerns as inline GitHub comments |
| **Phase 4 — Re-review** | Reviewer says *"re-review"* | Fetches new commits, walkthroughs incremental diff, assesses addressed/open/new concerns, resolves and replies |

---

## Workspace layout

All review state is written to `<workspace_path>/`:

```
<workspace_path>/
  meta.json                   — PR metadata (pr_number, owner, repo, branch, headRefOid, round, …)
  ticket.md                   — ticket context from Phase 0
  diff/
    round-1.patch             — full diff (generated files excluded), round 1
    round-N.patch             — incremental diff, round N (2+)
  walkthrough/
    round-1.md                — grouped walkthrough, round 1
    round-N.md                — single-pass walkthrough, round N (2+)
  concerns/
    round-N-agent.md          — sub-agent's independent findings (with Reviewer Feedback field)
    round-N-reviewer.md       — reviewer's own free-form notes (created empty, filled independently)
    round-N.md                — final merged postable concerns (output of Phase 2 Part C / Phase 4 Step 6)
    review-round-N.md         — addressed/still-open summary, round N (Phase 4)
    resolve-round-N.md        — Thread IDs to resolve, round N (Phase 4)
  comments/
    comments.md               — active posted concerns (Comment ID, Thread ID, URL per entry)
    comments_resolved.md      — resolved concerns
```

