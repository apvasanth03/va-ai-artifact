# va-plan-template

Templates for `plan.md` index and task specs.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Input](#input)
- [Workflow](#workflow)
- [Output layout](#output-layout)

## What it does

- Provides a standard directory layout, index template, and task spec template for implementation plans
- Enforces one-task-at-a-time authoring and approval
- Keeps rationale in one place (`Why this shape`) and visuals via `va-visualize`

## When to reach for it

- Authoring an implementation plan for a feature or story
- Breaking work into discrete, sequential task specs

## Invocation

- Auto-invocable — no `disable-model-invocation` flag
- Triggered when authoring a plan or breaking work into task specs

## Input

- A feature/story to plan for, with enough context to define goal and scope

## Workflow

| Step | What happens |
|---|---|
| **1. Draft index** | Author `plan.md` using the index template — Goal, Scope, task table with each task marked `Open` |
| **2. Gate** | Wait for approval on the index before drafting any task spec |
| **3. Draft task spec** | Author `1.<task_slug>.md` using the task template; mark its row `Draft` in `plan.md` |
| **4. Gate** | Wait for approval on that spec; mark it `Approved` before drafting the next task |
| **5. Repeat** | Steps 3–4 for each remaining task, in order — never draft two specs ahead of approval |
| **6. Implement** | As each task is executed and verified, mark it `Implemented` in `plan.md` |

## Output layout

```text
<plan_dir>/
├── plan.md               # Index: goal, scope, task table, verification
├── 1.<task_slug>.md      # Task 1 spec: self-contained implementation detail
├── 2.<task_slug>.md      # Task 2 spec
└── ...
```

**`plan.md`** — Goal, Scope (In/Out), optional Architecture & Visuals, optional Public API/Contracts, Tasks table (status: `Open` → `Draft` → `Approved` → `Implemented`), Verification.

**`N.<task_slug>.md`** — Why this shape, Comments guidance, Package Structure, Changes, Not in this task, Verification.
