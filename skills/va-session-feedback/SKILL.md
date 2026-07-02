---
name: va-session-feedback
description: Post-session feedback skill. Invoke at the end of a session to get a structured report and actionable feedback for continuous improvement.
disable-model-invocation: true
---

# Session Feedback

## Task

Analyze the completed session and produce a structured report of what happened, followed by actionable feedback to improve prompts, skills, and artifacts for future sessions.

---

## Context

- Works entirely from the current session's conversation history — no external reads needed

---

## Workflow

1. Build **Part 1: Report** from session conversation history
2. Build **Part 2: Feedback** based on report findings
3. **Save**: if the session contains a workspace path (look for a line matching `> **Path**: /some/path` or `workspace: /some/path` in the task prompt or template header), write to `<workspace>/feedback/YYYY-MM-DD_feedback.md` (get date via `date +%Y-%m-%d`); otherwise output in chat

---

## Output Format

Produce the output using exactly this template. Fill every field; write `None` for empty sections. For empty tables, replace the entire table including headers with `None`.

Use the value from **Session → Task** as `<task name>` in the document heading.

### Part 1: Report

```markdown
# Session Feedback — <task name> — <date>

## Report

### Task Setup
List only files explicitly referenced in the task prompt or template input — not every file read during execution.

| Item | Status |
|------|--------|
| Workspace | ✅ provided / ❌ none |
| <each workspace file from task prompt, one per row> | ✅ present / ❌ missing |
| Placeholders filled | ✅ all / ⚠️ some blank / N/A |
| Upfront context | sufficient / thin / missing |

### Session
| Field | Value |
|-------|-------|
| Task | <task name or short description> |
| Template | <detected template name or none> |
| Outcome | completed / partial / blocked |

### Sub Agents
Collapse repeated agents of the same type (e.g., Walkthrough ×5).

| # | Agent | Task |
|---|-------|------|
| 1 | <label> | <task in ≤10 words> |

### Skills
One row per (skill, invoker) pair — if the same skill is invoked by both main and a sub-agent, add two rows.

| Skill | Invoked By | Count |
|-------|------------|-------|
| <name> | main / <agent label> | <n> |

### Verify Iterations
| Round | Command | Outcome |
|-------|---------|---------|
| 1 | <command> | <N errors fixed or ✅ passed> |
```

### Part 2: Feedback

For **Skills**: use the invoked format for skills that were used; use the missed format for applicable skills from the session's available-skills list that were not invoked.

```markdown
## Feedback

### User
- Task specificity: <was scope and acceptance criteria clear?>
- Context completeness: <was relevant context provided?>
- Avoidable clarifications: <clarifications that arose after the agent had already started writing code or running commands — planning-stage clarifications are expected>
- Suggestion: <concrete suggestions to improve the prompt for next time>

### Skills

**<skill-name>**
- Sufficient: <yes / no>
- Gaps: <what the agent had to figure out manually that the skill should cover>
- Suggestion: <specific content to add>

**<skill-name>** ⚠️ not invoked
- Applicable because: <reason>
- Impact: <what the agent had to figure out manually as a result>
- Suggestion: <specific trigger phrase to add to skill description or prompt>

### Artifacts
Improvements to existing artifacts (prompt templates, skills) and new artifacts that would have made the session faster or more effective.

| Action | Type | Name | Specific Change | Rationale |
|--------|------|------|-----------------|-----------|
| create / update | skill / template / mcp / script | <name> | <what exactly to change or add> | <why it would help> |

### Session Efficiency
- Sub-agent usage: <appropriate = each sub-agent had a distinct parallelisable task / too many = a single agent could have done it / too few = main agent did work that could have been parallelised>
- Verify iterations: <root cause if >2 rounds>
- Biggest improvement: <one thing that would most speed up the next similar session>

### Feedback Loop
- Instructed: <✅ explicit verify → review → re-verify cycle found in task prompt or loaded template / ❌ not present>
- Executed: <✅ ran / ⚠️ partially / ❌ skipped>
- Recommendation: <if not instructed — specific instruction to add to the prompt/template>
```

---

## Rules

- **No fabrication** — only report what is visible in the conversation history
- **No skipped sections** — write `None` if a section has no data; for empty tables replace the entire table including headers with `None`
- **Feedback Loop → Artifacts** — if Feedback Loop `Instructed: ❌`, add a row to Artifacts to update the prompt/template with an explicit self-check instruction
- **File save** — when saving to file, also print a one-line confirmation to chat with the full path; when outputting to chat, do not attempt any file write
- **Context truncation** — if early conversation is not visible, note it in Session and mark affected sections ⚠️ may be incomplete
