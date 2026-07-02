# va-ai-artifact

Personal collection of Claude Code agent skills.

## Skills

| Name | Description | Docs |
|---|---|---|
| `va-pr-review-assist` | PR review assistant skill. Use when the user wants help reviewing a pull request — guides them through changes group-by-group, collaboratively surfaces concerns, and posts agreed inline comments via gh CLI. | [docs](docs/skills/va-pr-review-assist.md) |
| `va-session-feedback` | Post-session feedback skill. Invoke at the end of a session to get a structured report and actionable feedback for continuous improvement. | [docs](docs/skills/va-session-feedback.md) |

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
