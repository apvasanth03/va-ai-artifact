# Phase 1 — Walkthrough

**Goal**: the reviewer can scan the whole PR from the section files. Judgment stays in Phase 2. This is round 1's full walkthrough; a re-review round's lighter, delta-scoped version is `references/phase-5-rereview.md`'s job.

- Read `rounds/1/diff.patch` yourself and group it into logical sections — by concern, not file or commit. A feature, its call site, and its test are one section even across three files; two unrelated one-liners are two sections even in the same file. Order them so each builds on what came before.
- Write `rounds/1/walkthrough/index.md`: PR title/purpose/base branch, the ordered section list with links, and one high-level Mermaid diagram (flowchart or sequence — whichever fits) giving the big-picture shape of the whole PR before the reviewer drills into any section. Scope and detail are your call — a bulk-add-fields PR might not earn one at all; say so rather than forcing a diagram onto something with no shape.
- Write every `rounds/1/walkthrough/<n>.<slug>.md`, then notify the reviewer:
  > Walkthrough is ready at `rounds/1/walkthrough/index.md`. You can add your findings to `rounds/1/review/reviewer_review.md`. Reply to confirm when you are ready for me to start my review.
  - Structure each file with `##`/`###` subheadings per component/concern (a class, a layer, a step) — not bold inline labels standing in for headings.
  - Under a heading: one line of what changed, then the smallest structural view. Use the PR's real names.
  - Cover what changed, why (inferred intent), how it works, and anything worth flagging (described, not judged — judgment is Phase 2's job). Leave out code the diff already makes obvious.
- When the reviewer says a section is wrong, or asks a question, fix or answer it from the diff.

**Done when**: every section file exists, `walkthrough/index.md` links to each, the reviewer has been notified, and they confirm you should start your review.
