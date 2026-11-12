---
name: va-plan-template
description: Templates for plan.md (simple or complex) and task specs. Use when authoring an implementation plan or breaking work into task specs.
---

## Principles

- **Final spec, not a changelog**: Edit in place so files always read as the current spec; leave out review history and amendment notes.
- **One combined approval**: Draft the whole plan (`plan.md` and all task specs), then get a single approval.
- **Single home**: Rationale lives in a `Why this shape` section (per task, or plan-level for a simple plan), never beside code. Cross-cutting rules (e.g. comments) live once in `plan.md`, never repeated in task specs.
- **Sufficient, not complete**: Include only what lets a reviewer and an implementer proceed with no ambiguity; omit what they can derive.
- **Glanceable**: Express each change in `va-visualize` forms, not sentences, so a reviewer grasps it at a glance.
- **Refer, don't restate**: When a skill covers how to do something, name it for the implementer to load, and give only task-specific details.
- **Extensible**: Core sections are the baseline; add domain-specific sections as needed.

## Choosing a layout

|               | **Simple: `plan.md`**                                                                       | **Complex: `plan.md` + task specs**                                                                               |
| ------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Pick when** | Trivial or small: roughly 1–3 steps in one area of the codebase, and cheap to re-read whole | Multiple distinct tasks, or tasks need their own diffs, file trees, or invariants and can be edited independently |
| **Template**  | [`simple_plan.md`](reference/simple_plan.md)                                                | [`complex_plan.md`](reference/complex_plan.md): plan template plus a spec template for each task                     |

When unsure, start with a simple plan; move to complex if it grows. In the complex layout, use a `plan/` folder: `plan/plan.md` and `plan/N.<task_slug>.md`.

If `story.md` or `hld.md` exist, reference them from the plan instead of restating their content. When HLD is skipped for a trivial task, put the design rationale in the plan's `Why this shape` section.
