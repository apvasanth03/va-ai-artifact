# Phase 0 Setup · Phase 1 Understand

**Goal**: the round's threads are in the workspace, and the user has confirmed
the agent understands the PR well enough to judge comments on it.

## Setup

```bash
python scripts/setup.py <workspace> [--pr N] [--exclude GLOB…]      # round 1
python scripts/setup.py <workspace> --round <current + 1>           # a later round
```

It refuses, naming the check, when the PR branch isn't checked out, isn't in
sync with origin, or the working tree isn't clean; and on a later round when
the previous round isn't fully posted. Relay the failed check to the user and
wait for them to fix it.

`--exclude` keeps paths (tests, fixtures) out of the change map; it persists
into later rounds. Generated files and lockfiles are filtered automatically.

The script prints the round's counts and the change map. A round with zero
threads to walk ends here: tell the user, listing the waiting count.

## Understand

The brief has two parts:

- **Understanding** — what the PR delivers and why, the design choices a
  reviewer may question, and its deliberate limits. Sourced from the context
  docs when given; otherwise from the PR title and description, and the user.
  It comes from those sources, not from reading the diff: where they are
  silent, it is a Gap to ask, not to guess.
- **Change map** — the printed rollup, regrouped into areas with a role each.

Per-comment code reading happens in the walk, not here.

### `pr_context.md`

Written when no context docs are given. Read whole every round, so under ~30
lines, one line per bullet. A Gap answer is folded into its section.

```markdown
# PR #<n> · <title>
<url> · `<head>` → `<base>`

## What & why
- <1–3 bullets: what the PR delivers and the reason>

## Design choices
- <choice> — <reason>

## Deliberate limits
- <what is intentionally not done or handled elsewhere> — <reason / where tracked>

## References
- <path to project rules or docs this PR follows>
```

With context docs given, `pr_context.md` exists only for a durable Gap answer
the docs lack, and holds only that.

### Brief in chat

Points to the understanding instead of repeating it. In round 1 the user reads
the file before confirming.

````markdown
## PR #<n> · <title>
`<head>` → `<base>` · <n> files (<n> generated excluded) · +<add> / −<del> · head `<sha7>`
Understanding: `pr_context.md` <written | updated | unchanged> — or — context: `<doc>`, `<doc>`

| Area | Files | Δ | Role |
|---|---|---|---|

Comments: walk <n> (<n> new · <n> replied · <n> ⚠️) · waiting on reviewer <n>
Gaps: <question> — only if any

Confirm or correct.
````

At most ~8 map rows; per-file detail on request. Corrections land in
`pr_context.md`, edited by the agent or the user.

## Later rounds

`pr_context.md` is reused, not rebuilt. The brief says whether it changed and
adds the commits since the last round:

```markdown
### Since round <prev>
- `<sha7>` <commit subject>
```

**Done when**: `comments.json` and `comment_queue.md` exist for the round, and
the user has confirmed the brief with every Gap answered and folded in.
