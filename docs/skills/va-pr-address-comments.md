# va-pr-address-comments

Take the unresolved review comments on your own PR from first read to posted reply, round by round, with you approving every decision, fix, and reply.

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

- Confirms its understanding of the PR with you before judging any comment
- Treats every comment, human or bot, as a claim to verify against the code and the project's rules, never as an instruction
- Groups threads that share one root cause, so one decision covers them
- Walks the threads with you one *card* at a time: the claim, the analysis with evidence, a proposal (`fix`, `clarify`, or `skip`), and the exact reply
- Lands all agreed fixes as one verified commit, then posts a reply on every thread
- Leaves threads open for their author to resolve

## When to reach for it

- Your PR has review comments (from people or bots) to address
- A reviewer replied after an earlier round and the PR needs another pass

## Invocation

- Auto-invocable — no `disable-model-invocation` flag
- Triggered when addressing or replying to review comments on a PR you authored

## Prerequisites

- `gh` CLI, authenticated, and Python 3 for the bundled scripts
- Run from inside the PR's repository, with the PR branch checked out, in sync with origin, and a clean working tree. The setup refuses otherwise and names the failed check
- `va-sdlc-template` installed, for each round's fix plan

## Input

- **Workspace** — the folder for this PR's state (asked for if missing; no default)
- **PR** — defaults to the checked-out branch's PR
- **Context** (optional) — docs describing the PR (what was built, why, the design). Without them the agent writes a short `pr_context.md`

## Workflow

Each **round** is one pass over the PR's unresolved threads at one PR head. A new round starts when you bring new comments. `round.py status` shows where a round stands, so a new session resumes from there.

| Phase | Gate | What happens |
|---|---|---|
| **0. Setup** | — | Pins the round to the PR head, fetches and cleans the threads (bot noise stripped), prints the change map |
| **1. Understand** | Your confirmation of the brief | What the PR delivers and why, design choices, deliberate limits, and a map of the changed areas; gaps are asked, not guessed |
| **2. Group** | Approval on the groups | Threads sharing one root cause are proposed as a group |
| **3. Walk** | Approval on each card | One card per thread or group; you approve, edit, expand, or guide. Each `fix` gets its section in the round's plan |
| **4. Plan review** | Approval on the plan | Cross-fix notes and the verification scoped to the change are added |
| **5. Fix** | Approval on the commit, then on the push | Implements the plan, verifies it, self-reviews the diff, then commits and pushes |
| **6. Post** | Approval on the posting batch | Posts every approved reply and shows the round summary |

- Rounds with no `fix` go straight to Post; with no groups, the Group gate is skipped
- The same issue found beyond the commented lines is raised on the card and needs its own approval
- The agent never stashes, pulls, or switches branches; git state is yours outside the gated commit and push

| Decision | Code change | Reply |
|---|---|---|
| `fix` | Yes, in the round commit | What changed, with the commit |
| `clarify` | No | What was understood, and the question |
| `skip` | No | The reason, or where it is tracked when deferred |

## Output layout

```text
<workspace>/
├── meta.json               # PR identity, viewer, current round, excludes
├── pr_context.md           # Intent, design choices, deliberate limits (when no context docs)
└── rounds/<N>/
    ├── round.json          # PR head the round is pinned to
    ├── comments.json       # Cleaned threads (read-only)
    ├── comment_queue.md    # One row per thread: group, decision
    ├── final_replies.json  # Decisions, replies, plan approval, commit
    └── plan.md             # The round's fix plan, when it has a fix
```

`final_replies.json` is the single source of truth for what gets posted.

## Related skills

- [va-sdlc-template](va-sdlc-template.md) — used for each round's fix plan (simple layout)
- [va-task-exec](va-task-exec.md) — hands its PR's comments to this skill, with the plan as context
- [va-epic-exec](va-epic-exec.md) — runs this skill for the epic's one PR, with the story and HLD as context
- [va-pr-review-collab](va-pr-review-collab.md) — the reviewer side: reviews a PR and posts the comments
