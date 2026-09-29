# va-task-exec

Execute single-session tasks end-to-end, from story to verified implementation.

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

- Takes a task from story through design, planning, implementation, and verification in one session
- Enforces approval gates at each stage while leaving internal technical decisions to the agent

## When to reach for it

- The task can be completed end-to-end **within a single session/context window** — do not use for multi-session or long-running work
- Need structured checkpoints (story → design → plan → build) rather than jumping straight to code

> ⚠️ **Single-session only.** This skill is not designed to resume across sessions or survive a context reset. For work that spans multiple sessions, break it up or use a different workflow.

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `grilling` skill installed from [mattpocock/skills](https://github.com/mattpocock/skills)

## Input

- **Workspace** — the artifact root to write story/design/plan files into
- **Task & Context** — requirements, docs, POCs

Both are required; the skill asks before exploring if either is missing.

## Workflow

| Stage | Gate | What happens |
|---|---|---|
| **1. Story** | Approval on `story.md` | Run `grilling` until scope and a checkable Definition of Done are clear, then write the story |
| **2. High-level design** | Approval on `hld.md` | Validate a user-provided design, or draft one — architecture, visuals, contracts, boundaries |
| **3. Planning** | Approval on `plan.md`, then per task spec | Author the plan index, then each task spec one at a time (via `va-plan-template`) |
| **4. Execution & verification** | — | Implement each approved task in order, run its verification, mark it `Implemented` |
| **5. Review & summary** | — | Run plan-level verification, diff against specs, fix regressions, report deviations |

Scope changes or public contract shifts always require approval; internal errors and technical details are resolved autonomously.

## Output layout

```text
<workspace>/
├── story.md              # Requirements and checkable Acceptance Criteria (DoD)
├── hld.md                # Architecture, visuals, contracts, and boundaries
└── plan/
    ├── plan.md           # Plan index, verification suite, and task table
    ├── 1.<task_slug>.md  # Sequential task specs
    └── ...
```

## Related skills

- [va-plan-template](va-plan-template.md) — used for `plan/plan.md` and task specs
- [va-visualize](va-visualize.md) — used for HLD diagrams and visuals
