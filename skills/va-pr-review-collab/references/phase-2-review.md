# Phase 2 — Independent Review

**Goal**: two independent reads of the diff — yours and the reviewer's — neither shaped by the other. This is round 1's full review; a re-review round's blind delta review is Phase 5a in `references/phase-5-rereview.md`.

- Review `rounds/1/diff.patch` critically in a single pass (no sub-agents needed). Evaluate against these priorities in order:
  1. **Functional correctness** — does the code fulfill its intended behavior without breaking existing functionality, contracts, or regressions?
  2. **Code quality** — readability, maintainability, architectural fit, idiomatic style, and unnecessary complexity.
  3. **Edge cases & failure modes** — null/empty states, boundaries, error handling, race conditions, and resource leaks.
- Write your findings to `rounds/1/review/agent_review.md`, replacing the stub, in the Concern Item format. For a modified (not new) file, verify each `Line:` value against `python scripts/diff_lines.py <workspace_path> <file>` before writing it down — the file's current line numbers only match the diff's `+`-side numbers when nothing above your target line was added/removed.
- Once done, say so and wait — don't reveal findings, hint at counts, or check in again until the reviewer says they are done too.

**Done when**: `rounds/1/review/agent_review.md` reflects your independent judgment, and the reviewer has said they're finished with their own.
