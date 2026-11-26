# Plan guide

## Principles

- **One combined approval**: Draft the whole plan (`plan.md` and all task specs), then get a single approval.
- **Single home**: Rationale lives in a `Why this shape` section (per task, or plan-level for a simple plan), never beside code. Cross-cutting rules (e.g. comments) live once in `plan.md`, never repeated in task specs.
- **Skeleton-first**: Show changes as a code skeleton: each new class with its fields and public API, and only the changed members of a modified class, and bodies as intent-level pseudocode. Code is exact only where the implementer could get it wrong. Prose carries only the why.
- **Mirror**: When classes share a shape, show one; for the others, list only their differences.
- **Refer, don't restate**: When a skill covers how to do something, name it for the implementer to load, and give only task-specific details.

## Choosing a layout

|               | **Simple: `plan.md`**                                                                       | **Complex: `plan.md` + task specs**                                                                               |
| ------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Pick when** | Trivial or small: roughly 1–3 steps in one area of the codebase, and cheap to re-read whole | Multiple distinct tasks, or tasks need their own diffs, file trees, or invariants and can be edited independently |
| **Template**  | [`simple_plan.md`](simple_plan.md)                                                          | [`complex_plan.md`](complex_plan.md): plan template plus a spec template for each task                            |

When unsure, start with a simple plan; move to complex if it grows. In the complex layout, use a `plan/` folder: `plan/plan.md` and `plan/N.<task_slug>.md`.

When HLD is skipped for a trivial task, put the design rationale in the plan's `Why this shape` section.
