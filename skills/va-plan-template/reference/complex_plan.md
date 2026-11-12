## Plan (`plan.md`)

````markdown
# [Feature / Story Title]

## Goal

[What this plan delivers when executed.]

## Overview

[Optional: one visual of the whole change at a glance.]

## Scope

**In**
- [Deliverable]

**Out**
- [Explicit non-goal]

## Why this shape

[Optional: plan-level rationale. Use it when HLD is skipped.]

## References

[Optional: `story.md`, `hld.md`, docs, and skills the implementer should load.]

## Comments

Document public APIs; comment private code only where logic is non-obvious. Keep concise.

## Tasks

| # | File | Title | Status |
|---|---|---|---|
| 1 | `1.<task_slug>.md` | [Summary] | Open |
| 2 | `2.<task_slug>.md` | [Summary] | Open |

*Status: `Open` (not implemented) → `Implemented` (code verified)*

## Verification

[Required. Plan-level verification commands and observable criteria after all tasks complete.]
- `[run command]` — expected outcome
````

---

## Task spec (`N.<task_slug>.md`)

````markdown
# Task [N] — [Task Title]

[1–2 sentences on what this task accomplishes.]

## Why this shape

[Optional: rationale, constraints, trade-offs not already in `hld.md`.]

## Package Structure

```text
[path/to/module]/
├── [file_a]            (new)
├── [file_b]            (modified)
└── [file_c]            (deleted)
```

## Changes

[Visuals per `va-visualize`.]

## Not in this task

- [Explicit guardrails on what is deferred or handled by subsequent tasks.]

## Verification

[Optional: include only when the task can be verified independently; otherwise use the plan-level `Verification`.]

- `[test command or build command]` — expected pass criteria
- [Manual or observable verification step]
````
