# va-visualize

Visualize code logic, control flow, and diffs.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Input](#input)
- [Workflow](#workflow)
- [Related skills](#related-skills)
- [Credit](#credit)

## What it does

- Picks the smallest visual that makes a structural point clear
- Renders it next to brief supporting prose, using real names from the codebase

## When to reach for it

- Explaining logic, control flow, component structure, or a diff visually instead of in prose
- Any visual walkthrough where a picture removes the need for a long description

## Invocation

- Auto-invocable — no `disable-model-invocation` flag
- Triggered whenever a visual walkthrough would help

## Input

- The topic, code, or diff to visualize

## Workflow

Pick the smallest structural view that fits the point — use one, a few, rarely all:

| Visual | Use for |
|---|---|
| **Pseudocode** | Logic or an algorithm |
| **Call tree** | Runtime control flow |
| **Component tree** | UI structure, including state and module boundaries |
| **Shallow file tree** | File responsibility or a broad refactor |
| **Mermaid diagram** | Component interaction, control flow, or data flow |
| **Diff** (any of the above) | What changes, when the surrounding shape already exists |
| **Full code block** | Most of the block is new, or a copyable target shape is needed |

## Related skills

Used by [va-sdlc-template](va-sdlc-template.md), [va-task-exec](va-task-exec.md), and [va-pr-review-collab](va-pr-review-collab.md) for diagrams and structural views.

## Credit

Adapted from [humanlayer/skills](https://github.com/humanlayer/skills/tree/main), with minor updates.
