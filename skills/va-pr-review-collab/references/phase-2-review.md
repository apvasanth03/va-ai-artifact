# Phase 2 — Independent Review

**Goal**: two independent reads of the diff — yours and the reviewer's — neither shaped by the other. This is round 1's full review; a re-review round's blind delta review is in `references/phase-5-rereview.md`.

- Review `rounds/1/diff.patch` critically in a single pass (no sub-agents needed). Evaluate against these priorities in order:
  1. **Functional correctness** — does the code fulfill its intended behavior without breaking existing functionality, contracts, or regressions?
  2. **Code quality** — readability, maintainability, architectural fit, idiomatic style, and unnecessary complexity.
  3. **Edge cases & failure modes** — null/empty states, boundaries, error handling, race conditions, and resource leaks.
- Report a finding only with a named failure (what breaks, for whom) or the exact rule it breaks. Style nits and formatting with no failure share one `Nits` row. Each row the reviewer must decide costs them time.
- Write one **ledger** row per finding into `rounds/1/review/agent_review.md` (the table the stub provides): `#`, `Severity`, `File:Line`, `Title`, `Issue`.
  - `Issue` is the problem in at most two sentences — what is wrong and where it bites. The reviewer judges the problem first; the fix and rationale are written at approval.
  - Verify each `Line` against `python scripts/diff_lines.py <workspace_path> <file>` before writing it.
- Once done, say so and wait — don't reveal findings, hint at counts, or check in again until the reviewer says they are done too.

**Done when**: every finding sits in the ledger as one verified row, and the reviewer has said they're finished with their own.
