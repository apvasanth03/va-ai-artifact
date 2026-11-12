---
name: va-retro
description: Retrospective on the current session: where it lost tokens, time or accuracy, and the persistent fixes (AGENTS.md, skills, memory) that make the next session cheaper.
disable-model-invocation: true
---

# Retro

Find the **friction** in this session and the persistent change that removes it, so the next session is cheaper and more effective. The user reads the report and acts on it: every finding must be understandable alone and end in a fix they can apply. Report only; draft fix text when asked.

Work from the conversation alone. Ground each finding in something visible: a quoted line, a tool call, an error. If early context is truncated, say so.

## Friction

Classify each finding by its cause:

- **Wrong Info**: incorrect context from the user, a skill, `AGENTS.md`, memory, or the codebase.
- **Missing Info**: context that should have been there, so the agent searched or asked.
- **Rework**: output redone because of a misread request, an ignored instruction or skill, or a user correction.
- **Other**: friction that fits none of the above (tool failures, noisy calls, stalls).

Record the **impact** of each: cost (tokens: files read, searches, repeated calls) and time (rounds, waits, redo). Quote the counts the conversation shows, and rate each High / Med / Low.

A **fix** names the cheapest persistent home and the change in one line: a deterministic check, an `AGENTS.md` pointer, an edit to a skill, a new skill, a memory. Mark fixes already applied as done. A friction without a persistent fix is not a finding; leave it out.

## Report

Scannable in a minute, detail on demand. Use this template; omit empty sections:

```markdown
# Retro: <session topic> (<date>)

**Verdict**: <how costly the session was, and the cause that drove most of it>

## Keep doing

- <habit worth repeating, optional>

## Fix these first

1. **#<n> <title>**: <fix in one line>
2. ...
3. ...

## Index

| # | Cause | Source | Impact | Fix goes to |
|---|-------|--------|--------|-------------|
| 1 | Missing Info | `AGENTS.md` | 🔴 High: 5 greps, ~3 min | `AGENTS.md` |

## Findings

### <Cause: Wrong Info | Missing Info | Rework | Other>

#### <n>. <Title>

- **What happened**: <quoted evidence>
- **Impact**: <counts> (🔴 High | 🟡 Med | 🟢 Low)
- **Fix**: <file + one-line change>

## Minor

- <what happened> → <fix>

Want me to draft these fixes?
```

Findings are numbered by impact rank (1 = costliest), at most 7, and grouped under their cause heading. Source is one of `user`, `skill`, `AGENTS.md`, `codebase`, `model`, `tooling`.

## Saving

If the session had a workspace, save the report to `<workspace>/feedback/YYYY-MM-DD_retro.md` (date from `date +%Y-%m-%d`) and reply with one line: the saved path. Otherwise print the report in chat.
