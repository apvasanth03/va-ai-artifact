# va-plan-template

Templates for `plan.md` (simple or complex) and task specs.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Input](#input)
- [Workflow](#workflow)
- [Output layout](#output-layout)
- [Related skills](#related-skills)

## What it does

- Provides two plan layouts, a simple single-file plan and a complex plan with one spec per task
- Drafts the whole plan first, then asks for a single combined approval
- Keeps each file a final spec: no review history or amendment notes
- Keeps rationale in one place (`Why this shape`) and shows changes visually via `va-visualize`

## When to reach for it

- Authoring an implementation plan for a feature or story
- Breaking work into discrete task specs that can be edited independently

## Invocation

- Auto-invocable — no `disable-model-invocation` flag
- Triggered when authoring a plan or breaking work into task specs

## Input

- A feature or story to plan for, with enough context to define goal and scope
- `story.md` / `hld.md`, if they exist; the plan references them instead of restating them

## Workflow

| Step | What happens |
|---|---|
| **1. Choose a layout** | Simple for roughly 1–3 steps in one area; complex when there are several distinct tasks that need their own diffs, file trees, or invariants. When unsure, start simple and move to complex if it grows |
| **2. Draft everything** | `plan.md`, plus all task specs for the complex layout |
| **3. Approve once** | You review the whole plan and approve it in one go |
| **4. Implement** | Progress is tracked in the plan: step checkboxes in a simple plan, a task status (`Open` → `Implemented`) in a complex one |

## Output layout

**Simple** — one file:

```text
<plan_dir>/
└── plan.md       # Goal, scope, why this shape, steps, verification
```

**Complex** — an index plus one spec per task:

```text
<plan_dir>/plan/
├── plan.md               # Goal, scope, tasks table, verification
├── 1.<task_slug>.md      # Task 1 spec
├── 2.<task_slug>.md      # Task 2 spec
└── ...
```

- **`plan.md`** — Goal, Overview, Scope, Why this shape, References, Comments guidance, Tasks table (status per task), Verification
- **`N.<task_slug>.md`** — Why this shape, Package Structure, Changes, Not in this task, Verification

## Related skills

- [va-visualize](va-visualize.md) — used to express each change visually
- [va-task-exec](va-task-exec.md) — calls this skill in its planning stage
