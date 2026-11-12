# Phase 1 — Walkthrough

**Goal**: the reviewer scans the whole PR top to bottom in one file. Judgment stays in Phase 2. This is round 1's full walkthrough; a re-review round's delta version is `references/phase-5-rereview.md`'s job.

## Sections

Read `rounds/1/diff.patch` and group it by concern, not by file or commit. A feature, its call site and its test are one section; two unrelated one-liners are two sections. Order sections so each builds on the one before. Tests get one closing section.

Check every count, name and path against the diff before writing it down.

## Section gate

Before writing, propose the sections in chat: a short numbered list, one line per section saying what it covers. The reviewer steers in their own words (a different grouping, more depth on a section) and you revise the list until they approve. Write the walkthrough only from the approved sections.

## Layout

One file, `rounds/1/walkthrough.md`. When one file stops being scannable (roughly past six sections or 1,500 non-test diff lines; your judgment), keep `walkthrough.md` as the overview (Big picture, group list with links) and put each group's sections in `rounds/1/walkthrough/<group>.md`. A group is a few sections that share a package or concern, not a file per section.

## Template

```text
# <PR title>
base ← head, purpose, reference (plan or HLD, when one was given)

## Big picture
one Mermaid diagram of the whole PR (flowchart or sequence); none if the PR has no shape

## Section N: <concern>
### Overview            1-3 sentences: what changed, why
### Package structure   tree of this section's files; `# new` or a few words on each modified file
### How it works       one `va-visualize` view (pseudocode, call tree, sequence, diff) + short bullets
- **Plan:** ...         only when a plan or HLD was given: "followed", or the difference as fact

## Not in this PR
planned items that have no code
```

- Use the PR's real names.
- Drop a subheading when it would be empty or repeat another; a two-line section needs no three headings.
- The Plan line states facts ("plan: `decoder/events/`; diff: one registry file"). Verdicts belong to Phase 2.
- The tests section gives one line on what the tests cover, plus plan differences. The IDE already lists test files and cases.

## Hand-off

Tell the reviewer:
> Walkthrough is ready at `rounds/1/walkthrough.md`. You can add your findings to `rounds/1/review/reviewer_review.md`. Reply to confirm when you are ready for me to start my review.

When the reviewer says a section is wrong or asks a question, fix or answer it from the diff.

**Done when**: the reviewer approved the sections, every section has its tree and view, the file's counts and names match the diff, the reviewer has been notified, and they confirm you should start your review.
