# va-l2-analysis

Analyze an L2 support ticket with the developer and draft the support reply.

## Table of Contents

- [What it does](#what-it-does)
- [When to reach for it](#when-to-reach-for-it)
- [Invocation](#invocation)
- [Prerequisites](#prerequisites)
- [Input](#input)
- [Workflow](#workflow)

## What it does

- Builds a shared understanding of an L2 ticket's root cause and customer-visible behaviour with the developer
- Drafts the First Response, and the Resolution once the issue is accepted as a bug
- Produces reply text only — never changes the repository

## When to reach for it

- Triaging an L2 ticket and need to confirm root cause before replying
- Have a hypothesis for the bug and want it checked against the code
- Need a First Response or Resolution drafted in the team's reply format

## Invocation

- Explicit only — `disable-model-invocation: true`
- Must be called by name; not auto-invoked

## Prerequisites

- `grilling` skill installed from [mattpocock/skills](https://github.com/mattpocock/skills)

## Input

- Bug details, relevant source files, and a hypothesis — supplied by the developer
- Skill starts from the files named and opens further files only when needed

## Workflow

| Step | What happens |
|---|---|
| **1. Form a cause** | Read the ticket and code, form an independent root cause, then check it against the developer's hypothesis |
| **2. Grill** | One question round at a time, each with a recommended answer. Look up anything the ticket/code can settle; ask only for what can't be looked up. Continue until root cause and customer-visible behaviour are shared |
| **3. Shared understanding** | State the agreed picture and a recommendation on whether to accept it as a bug. Wait for approval or correction |
| **4. Reply** | After approval, draft the First Response. If accepted as a bug, draft the Resolution and wait for approval. Both follow `references/response-templates.md`; developer corrections are applied directly |
