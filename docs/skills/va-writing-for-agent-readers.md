# va-writing-for-agent-readers

Principles for writing content that an agent reads: skills, `AGENTS.md` / `CLAUDE.md`, prompts, and subagent briefs.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Principles](#principles)
- [Related skills](#related-skills)

## What it does

- Guides how you write or edit documents meant for an agent to read
- Sits on top of `writing-for-agents`; where the two differ, this skill wins
- Is about the document's content, not how an agent words its own replies

## When to reach for it

- Creating or editing a skill, `AGENTS.md`, `CLAUDE.md`, a prompt, or a subagent brief
- Tightening a document that is long, repetitive, or ignored by the agent

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `writing-for-agents` skill installed (loaded first by this skill)

## Input

- The document to write or edit

## Principles

A document is done when every principle has been applied to it.

| Principle | In practice |
|---|---|
| **Colleague** | Write for a capable co-worker: state the task, context, and expected result; leave the how to the reader |
| **Waypoints, not rails** | A workflow is a guide the reader may adapt; criteria bind the outcome, not the path |
| **Earn every token** | Every word shapes behaviour or is cut; leave out what the model already knows |
| **One source of truth** | Point to facts the reader can find (code, config, other docs) instead of copying them |
| **Declarative by default** | State what things are and how they depend on each other; use steps only where order is fixed, such as migrations or setup |
| **Cold reader** | Assume none of the conversation that produced the document; include the context or point to it |
| **Output template** | When a human reads the result, give the exact shape (headings, tables, fields) |

## Related skills

- `writing-for-agents` — the base skill this one extends
