# va-retro

Review the current session for where it lost tokens, time, or accuracy, and get the persistent fixes that make the next session cheaper.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Input](#input)
- [Workflow](#workflow)
- [Output layout](#output-layout)
- [Related skills](#related-skills)

## What it does

- Finds friction in the session and ties each finding to quoted evidence
- Rates each finding's cost in tokens and time (High / Med / Low)
- Proposes the cheapest persistent fix for each: an `AGENTS.md` pointer, a skill edit, a new skill, or a memory
- Reports only; it drafts the fix text when you ask

## When to reach for it

- At the end of a session that felt slow, repetitive, or full of corrections
- After finishing a ticket or epic stage, to feed the next session

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Input

- None. It works from the conversation alone. If early context was truncated, the report says so.

## Workflow

| Step | What happens |
|---|---|
| **1. Find friction** | Each finding is classed by cause: **Wrong Info**, **Missing Info**, **Rework**, or **Other** (tool failures, noise, stalls) |
| **2. Rate impact** | Counts the conversation shows (files read, searches, repeated calls, rounds, waits), rated High / Med / Low |
| **3. Propose fixes** | One line each, naming where the fix lives. A friction with no persistent fix is left out |
| **4. Report** | A verdict, what to keep doing, the top fixes, an index table, and findings grouped by cause (at most 7, ranked by cost) |
| **5. Offer drafts** | Ends by asking whether you want the fixes drafted |

## Output layout

- If the session has a workspace, the report is saved as `<workspace>/feedback/YYYY-MM-DD_retro.md` and the reply is just the saved path
- Otherwise the report is printed in chat

## Related skills

- [va-epic-exec](va-epic-exec.md) — writes a retro per session and merges them at close
