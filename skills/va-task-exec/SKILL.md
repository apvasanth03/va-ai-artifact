---
name: va-task-exec
description: Plan and implement a single-session task end-to-end.
disable-model-invocation: true
---

Take a task from ambiguity to verified delivery in one session, spending tokens
only where they reduce risk.

## Inputs

- **Workspace**: where artifacts (`story.md`, `hld.md`, plan) are written.
- **Task**: what the user wants done.
- **Context**: requirements, docs, POCs, code.

Ask the user if the workspace or task is missing.

## Judge the depth

Exploring, writing `story.md` and the HLD are each skippable for a trivial
task. State the skip with a one-line reason; the user can overrule. Judge each
separately.
Requirement grilling and the plan are always needed; a trivial task gets the
simple layout.

## Steps

1. **Explore**: Understand the current state of the code this task touches.
   Start from the user's context and widen only as needed. Done when you can
   say what exists, what changes and what it affects, without guessing.
2. **Requirement**: Run the `grilling` skill, using what you explored, until
   scope and a checkable Definition of Done (DoD) are unambiguous, whatever the
   task size. Then write `story.md` using
   [`story_template.md`](reference/story_template.md). **Approval required.**
3. **HLD** (`hld.md`): Ask the user if they have a design before drafting one.
   If so, validate it against the requirement and what you explored, and run the
   `grilling` skill on the gaps; update it in place if it is in the workspace,
   otherwise write it to `hld.md`. If not, draft it from the requirement and
   exploration using [`hld_template.md`](reference/hld_template.md).
   **Approval required.**
4. **Plan**: Run the `va-plan-template` skill to pick the template and create
   the plan. **Approval required.**
5. **Implement**: Follow the plan, updating its status (checkboxes, or task
   `Status`) as you go. Fix issues that come up on the way and note any
   deviation from the plan.
6. **Verify**: Run the plan's verification and fix failures until nothing is
   red.
7. **Self-review**: Review the diff: every DoD item met, every plan item
   delivered, nothing unplanned. Fix findings and re-verify. The user should
   see the work only after this pass.
8. **Summary**: Show evidence the task is done: each DoD item delivered, the
   verification results (what ran, what passed), and any deviations and
   assumptions. Then wait for the user.

If `story.md` is skipped, confirm the DoD in chat and record it atop the plan so
self-review has something to check against.

## Boundaries

- Decide technical details yourself; ask before changing scope or public
  contracts.
- If you can't fix an issue, ask the user.
- Commit or amend only with the user's approval.
