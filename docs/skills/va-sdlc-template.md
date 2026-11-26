# va-sdlc-template

Templates for a task's working docs: story (`story.md`), HLD (`hld.md`), and plan (`plan.md`, simple or complex, plus task specs).

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Input](#input)
- [Workflow (plan)](#workflow-plan)
- [Output layout](#output-layout)
- [Related skills](#related-skills)

## What it does

- Routes to one template per doc: story, HLD, or plan
- Story: what and why from the user's view: problem, user story, deliverables, out of scope, constraints, Gherkin or rule acceptance criteria (DoD), open questions
- HLD: only what is new or complex: solution overview, key decisions with their trade-offs, contracts, behaviour, known patterns, and risks and unknowns (each owned by you or a POC)
- Provides two plan layouts, a simple single-file plan and a complex plan with one spec per task
- Drafts the whole plan first, then asks for a single combined approval
- Shows plan changes as a code skeleton: new classes with fields and public API, only the changed members of modified classes, bodies as pseudocode
- Keeps each file a final spec: no review history or amendment notes
- Splits ownership across docs: the story owns what and why, the HLD owns how, the plan owns steps; each later doc links to the earlier ones
- Keeps rationale in one place (`Why this shape`) and shows changes visually via `va-visualize`

## When to reach for it

- Writing a story with scope and acceptance criteria
- Writing a high-level design for new or complex work
- Authoring an implementation plan for a feature or story
- Breaking work into discrete task specs that can be edited independently

## Invocation

- Auto-invocable — no `disable-model-invocation` flag
- Triggered when writing a story, an HLD, or a plan / task specs

## Input

- For a story or HLD: the requirement and what was explored
- For a plan: a feature or story to plan for, with enough context to define goal and scope
- `story.md` / `hld.md`, if they exist; the plan references them instead of restating them

## Workflow (plan)

| Step | What happens |
|---|---|
| **1. Choose a layout** | Simple for roughly 1–3 steps in one area; complex when there are several distinct tasks that need their own diffs, file trees, or invariants. When unsure, start simple and move to complex if it grows |
| **2. Draft everything** | `plan.md`, plus all task specs for the complex layout |
| **3. Approve once** | You review the whole plan and approve it in one go |
| **4. Implement** | Progress is tracked in the plan: step checkboxes in a simple plan, a task status (`Open` → `Implemented`) in a complex one |

## Output layout

**Story / HLD** — one file each: `story.md`, `hld.md`.

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
- **`N.<task_slug>.md`** — Why this shape, Package Structure, Flow, Classes and public API, Test cases, Not in this task, Verification

## Related skills

- [va-visualize](va-visualize.md) — used to express each change visually
- [va-task-exec](va-task-exec.md) — calls this skill for the plan, and for the HLD when the task needs new design
- [va-epic-exec](va-epic-exec.md) — calls this skill for the epic's story and HLD
- [va-pr-address-comments](va-pr-address-comments.md) — uses the simple layout for each round's fix plan
