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

- Takes a task through exploration, requirements, design, planning, implementation, verification, and review in one session
- Asks for your approval at the story, design, and plan stages
- Scales the depth to the task: for a trivial task it can skip exploration, the story, or the design, and says why
- Reviews its own diff against the definition of done before showing you the work

## When to reach for it

- The task can be completed end-to-end **within a single session/context window**
- You want structured checkpoints (story → design → plan → build) rather than jumping straight to code

> ⚠️ **Single-session only.** This skill is not designed to resume across sessions or survive a context reset. For multi-session work, use [va-epic-exec](va-epic-exec.md).

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `grilling` skill installed from [mattpocock/skills](https://github.com/mattpocock/skills)

## Input

- **Workspace** — where the story, design, and plan files are written
- **Task** — what you want done
- **Context** — requirements, docs, POCs, code

The skill asks if the workspace or task is missing.

## Workflow

| Step | Gate | What happens |
|---|---|---|
| **1. Explore** | — | Understand the code the task touches: what exists, what changes, what it affects |
| **2. Requirement** | Approval on `story.md` | Run `grilling` until scope and a checkable Definition of Done are clear, then write the story |
| **3. High-level design** | Approval on `hld.md` | Asks if you already have a design. If so, validates it against the requirement; otherwise drafts one — architecture, visuals, contracts, boundaries |
| **4. Plan** | Approval on the plan | Picks the layout and writes the plan via `va-plan-template` |
| **5. Implement** | — | Follows the plan and updates its status; notes any deviation |
| **6. Verify** | — | Runs the plan's verification and fixes failures until nothing is red |
| **7. Self-review** | — | Checks the diff: every DoD item met, every plan item delivered, nothing unplanned |
| **8. Summary** | Your review | Shows evidence per DoD item, verification results, deviations, and assumptions, then waits for you |

- Exploration, the story, and the design can each be skipped for a trivial task, with a one-line reason you can overrule. Requirement grilling and the plan are always done.
- If the story is skipped, the definition of done is confirmed in chat and recorded atop the plan.
- Scope changes or public contract shifts always need your approval; technical details are decided by the agent.
- Commits or amends happen only with your approval.

## Output layout

A simple plan is one file; a complex plan uses a `plan/` folder.

```text
<workspace>/
├── story.md              # Requirements and checkable Acceptance Criteria (DoD)
├── hld.md                # Architecture, visuals, contracts, and boundaries
└── plan.md               # Simple plan
```

```text
<workspace>/
├── story.md
├── hld.md
└── plan/                 # Complex plan
    ├── plan.md           # Task table and verification
    ├── 1.<task_slug>.md  # Task specs
    └── ...
```

`story.md` and `hld.md` are absent when skipped.

## Related skills

- [va-plan-template](va-plan-template.md) — used for the plan and task specs
- [va-visualize](va-visualize.md) — used for HLD diagrams and visuals
- [va-epic-exec](va-epic-exec.md) — runs this skill once per ticket
