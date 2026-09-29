---
name: va-work-journal
description: Capture a work contribution — feature delivery, technical work, team/leadership, or learning experiment.
disable-model-invocation: true
---

## Purpose

Maintain a durable, evidence-backed contribution journal throughout the year. It is source material for a future self-review — not a self-review format or rating exercise.

## Input

The user provides a workspace and a contribution to record. They may also provide supporting resources such as repository paths, pull requests, or documentation.

Ask for the workspace when it is not provided. Treat linked resources as evidence to inspect read-only. State only facts supported by those resources or by the user; keep unknown outcomes, metrics, and release status open.

## Contribution context

Use the workspace as a contribution journal:

```text
workspace/
├── index.md
└── contributions/
    ├── feature-deliveries/
    ├── technical-work/
    ├── team-leadership/
    └── learning-experiments/
```

If `index.md` does not exist, treat this as the first run and include creating the workspace skeleton in the approval plan.

Each contribution has its own Markdown record. Name the file using the date and a slug: `YYYY-MM-DD-contribution-title.md`.

Keep the same structure in every record:

```markdown
# Contribution title

**Captured on:** YYYY-MM-DD
**Delivered on:** YYYY-MM-DD (add only when known)
**Status:** Planned | In Progress | Delivered | Paused

## Summary
## Category
## My ownership
## Context / problem
## Work completed
## Impact / outcome
## Status and next steps
## Evidence
## Dated updates
```

Classify a contribution into the most fitting category. If it genuinely spans categories, ask the user to decide. Preserve ownership precisely: for example, led, implemented, contributed, guided, reviewed, or learned.

Keep `index.md` concise: title, category, status, last updated date, and a link to each record.

When new information relates to an existing contribution, extend its dated updates rather than duplicating it. If several records may match, present them and ask the user to select the target.

## Approval before writing

Read and assess resources freely. Before creating the workspace skeleton, creating a record, changing a record, or updating the index, present a high-level plan containing:

- the intended category and target file;
- whether this is a new record or an update;
- the proposed index change;
- the factual outline and evidence to capture.

Wait for the user's explicit approval before making those changes.

## Writing style

- Use simple words and short sentences.
- Structure records with headings and bullets; avoid long paragraphs.

## Quality bar

Favour concrete scope, ownership, evidence, status, and outcomes. Evidence is useful even when metrics are unavailable.
