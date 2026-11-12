# Skills

Personal collection of AI agent skills.

| Name                         | Description                                                                    | Docs                                    |
| ---------------------------- | ------------------------------------------------------------------------------ | --------------------------------------- |
| va-epic-exec                 | Deliver a multi-session epic through kickoff, ticket, and close stages         | [docs](va-epic-exec.md)                 |
| va-l2-analysis               | Analyze an L2 ticket with the developer and draft the support reply            | [docs](va-l2-analysis.md)               |
| va-plan-template             | Templates for `plan.md` (simple or complex) and task specs                     | [docs](va-plan-template.md)             |
| va-pr-review-collab          | Collaborative PR review — independent reviews merged and posted together       | [docs](va-pr-review-collab.md)          |
| va-retro                     | Retrospective on a session: friction found and the persistent fixes            | [docs](va-retro.md)                     |
| va-task-exec                 | Execute single-session tasks end-to-end, from story to verified implementation | [docs](va-task-exec.md)                 |
| va-visualize                 | Visualize code logic, control flow, and diffs                                  | [docs](va-visualize.md)                 |
| va-work-journal              | Capture a work contribution as durable, evidence-backed journal material       | [docs](va-work-journal.md)              |
| va-writing-for-agent-readers | Principles for writing content that an agent reads                             | [docs](va-writing-for-agent-readers.md) |

## Installation

### GitHub CLI ([`gh skill`](https://cli.github.com/manual/gh_skill))

Browse and install interactively:

```
gh skill install apvasanth03/va-ai-artifact
```

Install a specific skill:

```
gh skill install apvasanth03/va-ai-artifact {{SKILL_NAME}}
```

### Vercel Skills ([`npx skills`](https://github.com/vercel-labs/skills))

Browse and install interactively:

```
npx skills add apvasanth03/va-ai-artifact
```

Install a specific skill:

```
npx skills add apvasanth03/va-ai-artifact --skill {{SKILL_NAME}}
```

> See the [Skills](#skills) table above for available `{{SKILL_NAME}}` values.
