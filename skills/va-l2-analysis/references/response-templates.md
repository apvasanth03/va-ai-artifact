# Response templates

The draft is plain text for Freshdesk (code fences only — Freshdesk shows markdown emphasis, links, and `#` headings as literal characters). Simple words, short sentences.

Format for both templates below: each label on its own line, its value directly below with no blank line between them, and exactly one blank line before the next label. Write every field named below; fill each from the ticket, the code, or judgment where reasonable — leave a field blank only when nothing available lets you back it, rather than guessing.

## First Response

For the support agent. Under `First cut analysis or Response`, write Issue, Root cause, and Fix in product terms: what is broken, why, and what will change. File paths and code belong in the Resolution.

```
Confirming the availability of adequate details for debugging

Login successful with provided credentials (Yes/No)? :

Availability of necessary logs for troubleshooting: (Yes/No)(Specify exact log details needed) :

Issue identification/classification:

Issue replicable in the customer's account :

Nature of the issue: Scriptfix/Bug/Clarification?

Known Issue identified? – Yes/No (Mention any known method to unblock the customer or workaround available?) :

Additional Details:

Bo Ownership confirmed : (Yes/No) ?

First cut analysis or Response:

Issue:

Root cause:

Fix:
```

## Resolution

For the engineer who will make the fix. Use after the developer accepts the issue as a bug.

Current Behaviour: the cause, `file:line`, and a code block of the offending lines. Expected Behaviour: the change and a code block of the replacement lines. Steps: a from-scratch setup in a new test account, including configuration.

```
Current Behaviour:

Expected Behaviour:

Steps to Reproduce the issue in a new test account:

Screenshots/Video recording/HAR File/Exported Haystack logs:

Bug classification: (Breakage/Deviation from the expected behaviour)

Impact Analysis: Impacting multiple accounts/ Edge case scenario/10+ customer impact/Less than 10 customer impact

Workaround Available: Yes/No

Proposed Workaround:
```
