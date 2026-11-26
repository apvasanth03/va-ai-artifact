# va-task-exec

Take a single-session task from ambiguity to verified delivery, spending effort only where it reduces risk.

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

- Takes a small feature or bug fix through exploration, requirements, optional design, planning, implementation, verification, and review in one session
- Keeps one record, the plan: a compact `Requirement` (why, what, definition of done (DoD)) and the steps
- Writes the `Requirement` to the plan first for you to confirm, then asks for your approval on the full plan (and on the design, when one is needed)
- Reviews its own diff against the DoD before showing you the work

## When to reach for it

- The task can be completed end-to-end **within a single session/context window**
- You want a confirmed DoD and an approved plan before any code is written

> ⚠️ **Single-session only.** This skill is not designed to resume across sessions. For multi-session work, use [va-epic-exec](va-epic-exec.md).

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `grilling` skill installed from [mattpocock/skills](https://github.com/mattpocock/skills)
- Installed alongside it: `va-sdlc-template`, `va-visualize`, and `va-pr-address-comments` for PR comments

## Input

- **Workspace** — where the plan and design files are written
- **Task** — what you want done
- **Context** — requirements, tickets, docs, designs, POCs, code

The skill asks if the workspace or task is missing.

## Workflow

| Step | Gate | What happens |
|---|---|---|
| **1. Explore** | — | Understand the code the task touches: what exists, what changes, what it affects. A bug fix also reproduces the bug (by hand or with a failing test) and finds the root cause |
| **2. Requirement** | Approval on `Requirement` and `Scope` in `plan.md` | Run `grilling` until scope and a checkable DoD are clear, then write `plan.md` with only the `Requirement` and `Scope` sections |
| **3. High-level design** | Approval on `hld.md` | Only for new or complex design. Asks if you already have a design. If so, validates it against the requirement; otherwise drafts one |
| **4. Plan** | Approval on the plan | Picks the layout and completes the plan around the `Requirement` via `va-sdlc-template`; a complex plan moves to `plan/plan.md` |
| **5. Implement** | — | Follows the plan and updates its status; notes any deviation |
| **6. Verify** | — | Runs the plan's verification and fixes failures until nothing is red; checks it can't run (e.g. on a device) become manual steps for you |
| **7. Self-review** | — | Checks the diff: every DoD item met, every plan item delivered, nothing unplanned |
| **8. Summary** | Your review | Shows evidence per DoD item, verification results, deviations, and assumptions, then waits for you |

- No `story.md`: the plan's `Requirement` (one line each for why and what, plus the DoD) is a compact story; a ticket or PRD is linked in `References`.
- For a bug fix, `Why this shape` records the root cause and the DoD includes a regression test that fails before the fix and passes after.
- If the task does not fit one session, the skill says so and proposes a split.
- Scope changes or public contract shifts always need your approval; technical details are decided by the agent.
- Commits or amends happen only with your approval.
- To address the PR's review comments afterwards, ask for it: the skill runs `va-pr-address-comments` with the plan (and `hld.md`) as context, in `<workspace>/pr_comments/`.

## Output layout

A simple plan is one file; a complex plan uses a `plan/` folder.

```text
<workspace>/
├── hld.md                # Only for new or complex design
└── plan.md               # Simple plan: requirement, steps, verification
```

```text
<workspace>/
├── hld.md
└── plan/                 # Complex plan
    ├── plan.md           # Requirement, task table, verification
    ├── 1.<task_slug>.md  # Task specs
    └── ...
```

`hld.md` is absent when the task needs no new design.

## Related skills

- [va-sdlc-template](va-sdlc-template.md) — used for the HLD, plan, and task specs
- [va-visualize](va-visualize.md) — used for HLD diagrams and visuals
- [va-epic-exec](va-epic-exec.md) — runs this skill once per ticket, from the plan onward
- [va-pr-address-comments](va-pr-address-comments.md) — addresses the PR's review comments
