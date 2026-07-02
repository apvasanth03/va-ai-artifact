# va-session-feedback

**Invocation**: `/va-session-feedback` (explicit only — `disable-model-invocation: true`)

Analyzes the completed session and produces a structured report of what happened, followed by actionable feedback to improve prompts, skills, and artifacts for future sessions. Works entirely from the current conversation history — no external reads needed.

---

## Prerequisites

None. Works from conversation history only.

---

## Usage

Invoke at the end of any session:
```
/va-session-feedback
```

Output is saved to `<workspace>/feedback/YYYY-MM-DD_feedback.md` if the session had a workspace path, otherwise printed to chat.

---

## Output

Two-part markdown document:

**Part 1 — Report**: Task setup checklist, session summary, sub-agents used, skills invoked, verify iterations.

**Part 2 — Feedback**: Actionable suggestions for the user (prompt clarity), each skill used (gaps, suggestions), artifacts to create or update, session efficiency analysis, and feedback loop assessment.
