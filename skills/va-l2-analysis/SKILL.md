---
name: va-l2-analysis
description: Analyze an L2 ticket with the developer and draft the support reply.
disable-model-invocation: true
---

# L2 analysis

Reach a shared understanding of an L2 ticket with the developer, then draft the support reply. Describe the fix in the reply and leave the repository unchanged.

## Input

The developer supplies the bug details, the relevant source files, and a hypothesis.

Start from the files they name and open further files when the cause requires it. Form your own cause from the ticket and the code, then check it against their hypothesis.

## Grill

Ask one round at a time. Give a recommended answer with each question, then wait.

Look up any fact the ticket details or the code can settle. Ask for what cannot be looked up, and for confirmation of the root cause and the customer-visible behaviour. Unknowns stay unknown until the developer resolves them.

Done when you and the developer share the root cause and the customer-visible behaviour.

## Shared understanding

Pause and state that shared picture, including whether you recommend accepting it as a bug. Wait for approval or a correction.

## Reply

After approval, draft the First Response. When the developer has accepted the issue as a bug, draft the Resolution and wait for their approval.

Follow [references/response-templates.md](references/response-templates.md) for both drafts. Apply corrections the developer makes.
