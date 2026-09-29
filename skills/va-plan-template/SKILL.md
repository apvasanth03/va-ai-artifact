---
name: va-plan-template
description: Templates for plan.md index and task specs. Use when authoring an implementation plan or breaking work into task specs.
---

## Principles

- **Final spec, not a changelog**: Edit task files in place to current state. Never log review history or amendment notes.
- **One task at a time**: Author and approve one task spec before drafting the next.
- **Single home for rationale**: Design decisions and constraints live in `Why this shape` only, never beside code.
- **Visual-first**: Follow `va-visualize` for file trees, diffs, and control flows to minimize prose.
- **Extensible**: Core sections are the baseline; add domain-specific sections as needed.

## Directory Layout

```text
<plan_dir>/
├── plan.md               # Index: goal, scope, task table, verification
├── 1.<task_slug>.md      # Task 1 spec: self-contained implementation detail
├── 2.<task_slug>.md      # Task 2 spec
└── ...
```

---

## Index Template (`plan.md`)

````markdown
# [Feature / Story Title]

[1–2 sentences on architectural premise and objective.]

## Goal

[What this plan delivers when executed.]

## Scope

**In**
- [Deliverable]

**Out**
- [Explicit non-goal]

## Architecture & Visuals

[Optional: High-level sequence diagram, component tree, or data flow using va-visualize.]

## Public API / Contracts

[Optional: Signatures or tables of exposed public APIs / interfaces.]

## Tasks

| # | File | Title | Status |
|---|---|---|---|
| 1 | `1.<task_slug>.md` | [Summary] | Open |
| 2 | `2.<task_slug>.md` | [Summary] | Open |

*Status lifecycle: `Open` (not drafted) → `Draft` (written, in review) → `Approved` (spec approved) → `Implemented` (code verified)*

## Verification

[Plan-level verification commands and observable criteria after all tasks complete.]
- `[run command]` — expected outcome
````

---

## Task Template (`N.<task_slug>.md`)

````markdown
# Task [N] — [Task Title]

[1–2 sentences on what this task accomplishes.]

## Why this shape

- [Architectural rationale, constraints, and trade-offs.]

## Comments

- Document all public APIs.
- Comment private/internal code only when logic is non-obvious.
- Keep comments concise.

## Package Structure

```text
[path/to/module]/
├── [file_a].ts         (new)
├── [file_b].kt         (modified)
└── [file_c].json       (deleted)
```

## Changes

[Exact file paths, targeted diffs or code blocks, ordering, and invariants.]

## Not in this task

- [Explicit guardrails on what is deferred or handled by subsequent tasks.]

## Verification

- `[test command or build command]` — expected pass criteria
- [Manual or observable verification step]
````
