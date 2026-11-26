---
name: va-task-exec
description: Plan and implement a single-session task end-to-end.
disable-model-invocation: true
---

Take a task from ambiguity to verified delivery in one session, spending tokens
only where they reduce risk. A task is a **feature** (new or changed behaviour)
or a **bug fix**. The plan is the task's record: it carries the requirement and
the steps, so it survives compaction and serves later work such as PR comments.

## Inputs

- **Workspace**: where artifacts (the plan, `hld.md`) are written.
- **Task**: what the user wants done.
- **Context**: requirements, tickets, docs, designs, POCs, code.

Ask the user if the workspace or task is missing.

## Steps

1. **Explore**: Understand the current state of the code this task touches.
   Start from the user's context and widen only as needed. Done when you can
   say what exists, what changes and what it affects, without guessing. A bug
   fix also needs the bug reproduced, by hand or with a failing test, and its
   root cause found; when it can't be reproduced, state the suspected cause as
   an assumption, and the DoD's regression test confirms it.
2. **Requirement**: Run the `grilling` skill, using what you explored, until
   scope and a checkable Definition of Done (DoD) are unambiguous; when the
   context already states a DoD, grill its gaps. Then write `plan.md` with only
   the Requirement and `Scope` sections (see [plan override](#plan-override)).
   **Approval required.**
3. **HLD** (`hld.md`): Only when the task needs new or complex design that no
   existing design covers. Ask the user if they have a design before drafting
   one. If so, validate it against the requirement and what you explored, and
   run the `grilling` skill on the gaps; update it in place if it is in the
   workspace, otherwise write it to `hld.md`. If not, draft it using the
   `va-sdlc-template` skill (HLD), with its Context linking to the plan's
   Requirement. **Approval required.**
4. **Plan**: Run the `va-sdlc-template` skill (plan) to pick the layout and
   complete the plan around the Requirement, with the
   [plan override](#plan-override); for the complex layout, move `plan.md` to
   `plan/plan.md`. **Approval required.**
5. **Implement**: Follow the plan, updating its status (checkboxes, or task
   `Status`) as you go. Fix issues that come up on the way and note any
   deviation from the plan.
6. **Verify**: Run the plan's verification and fix failures until nothing is
   red. A check you can't run, such as on a device, becomes manual check steps
   for the user in the summary.
7. **Self-review**: Review the diff: every DoD item met, every plan item
   delivered, nothing unplanned. Fix findings and re-verify. The user should
   see the work only after this pass.
8. **Summary**: Show evidence the task is done: each DoD item delivered, the
   verification results (what ran, what passed), the manual check steps, and
   any deviations and assumptions. Then wait for the user.

## Plan override

The plan template applies to both layouts with these changes.

| Section | Feature | Bug fix |
| --- | --- | --- |
| **Requirement** (replaces `Goal`) | Why: who benefits, why now. What: what gets delivered | Why: the symptom, how to reproduce it, who is affected. What: the correct behaviour after the fix |
| Requirement › DoD | Pass/fail checklist | Pass/fail checklist, plus a regression test that fails before the fix and passes after |
| Why this shape | The design rationale | The root cause, and why the fix addresses it |
| References | Ticket, PRD, existing design | Ticket, logs, crash report |

Every other section follows the template for both. Each DoD item is proven by
`Verification` or checked in self-review.

The Requirement is a compact story: one line each for Why and What, with the
detail in the DoD.

```markdown
## Requirement
- **Why**: [One line: who benefits / the symptom]
- **What**: [One line: what gets delivered / the correct behaviour]
- **DoD**:
  - [ ] [Pass/fail item]
```

## Boundaries

- Decide technical details yourself; ask before changing scope or public
  contracts.
- If you can't fix an issue, ask the user.
- When the task does not fit one session, tell the user and propose a split.
- Commit or amend only with the user's approval.

## PR comments

When the user asks to address the PR's review comments, follow
[`va-pr-address-comments`](../va-pr-address-comments/SKILL.md) with workspace
`<workspace>/pr_comments/` and context the plan and `hld.md` when present.
