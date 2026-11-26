---
name: va-sdlc-template
description: Templates for story.md, hld.md and plan.md. Use when writing or updating one.
---

Load the template for the doc you are writing.

| Doc | Template |
| --- | --- |
| Story (`story.md`) | [`story_guide.md`](reference/story_guide.md) |
| HLD (`hld.md`) | [`hld_guide.md`](reference/hld_guide.md) |
| Plan (`plan.md`, task specs) | [`plan_guide.md`](reference/plan_guide.md) |

## Shared principles

These apply to every doc; each guide adds its doc-specific principles.

- **Final spec, not a changelog**: Edit in place so files always read as the
  current spec; leave out review history and amendment notes.
- **Sufficient, not complete**: Include only what lets the doc's reader proceed
  with no ambiguity; link sources instead of copying them, and omit what they
  can derive.
- **Extensible**: Core sections are the baseline; add domain-specific sections
  as needed.
- **Across documents**: The story owns what and why, the HLD owns architecture,
  the plan owns steps. Each later doc references the earlier ones instead of
  restating them.
