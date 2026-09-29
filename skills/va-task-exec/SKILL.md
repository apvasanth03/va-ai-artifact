---
name: va-task-exec
description: Execute single-session tasks end-to-end.
disable-model-invocation: true
---

Single-session task workflow. Enforces alignment gates while granting autonomy on internal technical decisions.

## Inputs & Structure

Ensure **Workspace** (artifact root) and **Task & Context** (requirements, docs, POCs) are provided. If either is missing, ask the user before exploring.

```text
<workspace>/
├── story.md              # Requirements and checkable Acceptance Criteria (DoD)
├── hld.md                # Architecture, visuals, contracts, and boundaries
└── plan/
    ├── plan.md           # Plan index, verification suite, and task table
    ├── 1.<task_slug>.md  # Sequential task specs
    └── ...
```

## Workflow

*Note: Templates are baseline references—adapt, expand, or omit sections to fit the task.*

### 1. Story (`story.md`)
1. Analyze context and run `grilling` until scope and a checkable **Definition of Done (DoD)** are clear.
2. Author `story.md` using [`reference/story_template.md`](reference/story_template.md).
3. **Gate**: Wait for user approval before moving to design.

### 2. High-Level Design (`hld.md`)
1. Ask user for their HLD / plan, or offer to draft one:
   - *User provided*: Validate against context, grill on gaps, and finalize into `hld.md`.
   - *Agent authored*: Draft `hld.md` using [`reference/hld_template.md`](reference/hld_template.md).
2. **Gate**: Wait for user approval before moving to planning.

### 3. Planning (`plan/`)
Use `va-plan-template`:
1. Author `plan/plan.md` (task table in `Open`/`Draft` status) → **Gate**: Wait for user approval.
2. Author each `plan/N.<task_slug>.md` sequentially → **Gate**: User approval required per spec (mark `Approved`) before drafting the next.

### 4. Execution & Verification
For each approved task in order:
1. Implement changes and run task verifications.
2. Update task status to `Implemented` in `plan/plan.md`.

*Autonomy bounds*: Resolve internal errors and technical details autonomously; require user approval for scope changes or public contract shifts.

### 5. Review & Summary
1. Run plan-level verification from `plan/plan.md`.
2. Review git diff against specs; fix regressions.
3. Report: delivered tasks, verification results, and assumptions/gotchas/deviations.
