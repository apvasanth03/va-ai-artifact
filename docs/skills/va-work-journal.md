# va-work-journal

Capture a work contribution as durable, evidence-backed journal material.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Input](#input)
- [Workflow](#workflow)
- [Output layout](#output-layout)

## What it does

- Records a feature delivery, technical work, team/leadership, or learning contribution as a dated, evidence-backed entry
- Builds source material for a future self-review — not a self-review or rating exercise itself

## When to reach for it

- You've delivered or contributed something worth capturing for a later self-review
- You want to extend an existing contribution record with new evidence or an update

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Input

- **Workspace** — asked for if not provided
- **Contribution** — what to record, optionally with supporting resources (repo paths, PRs, docs), inspected read-only as evidence

## Workflow

| Step | What happens |
|---|---|
| **1. Classify** | Contribution is classified into the best-fitting category; ambiguous cases are asked of you |
| **2. Match or create** | Checked against existing records — extends a matching one with a dated update, or starts a new record |
| **3. Plan** | Category, target file, new-vs-update, proposed index change, and factual outline are presented |
| **4. Gate** | Wait for your explicit approval before writing anything |
| **5. Write** | Record created/updated with the standard structure; `index.md` updated with title, category, status, date, link |

Only facts backed by your input or the linked resources are recorded — outcomes, metrics, and release status stay open until known.

## Output layout

```text
workspace/
├── index.md
└── contributions/
    ├── feature-deliveries/
    ├── technical-work/
    ├── team-leadership/
    └── learning-experiments/
```

Each record (`YYYY-MM-DD-contribution-title.md`) follows the same structure: Summary, Category, My ownership, Context/problem, Work completed, Impact/outcome, Status and next steps, Evidence, Dated updates.
