---
name: va-writing-for-agent-readers
description: Principles for writing content that an agent reads (skills, AGENTS.md / CLAUDE.md, prompts, subagent briefs), not for how an agent words its own output.
disable-model-invocation: true
---

The base is `writing-for-agents`, loaded first; its levers apply. Where it and
the principles below differ, these win.

## Principles

- **Colleague**: the reader is a capable co-worker. A brief states the task, the
  context and the expected result plainly, and leaves the how to the reader.
- **Waypoints, not rails**: a workflow is a guide. The reader adapts the route
  when the situation calls for it; criteria bind the outcome, not the path.
- **Earn every token**: every word and line shapes behaviour or is cut. What the
  model already knows from training stays out.
- **One source of truth**: facts the reader can find (code, config, other docs)
  are pointed to, not copied.
- **Declarative by default**: state what things are and how parts depend on each
  other; the reader derives the order. Imperative fits where order is fixed and
  skipping a step breaks things: migrations, setup, numbered procedure steps.
- **Cold reader**: the document is read with none of the conversation that
  produced it. The context the reader needs is in the document or behind a
  pointer.
- **Output template**: when a human reads the result, the document gives the
  exact shape (headings, tables, fields), not just "write a report".

A document is done when every principle has been applied to it.
