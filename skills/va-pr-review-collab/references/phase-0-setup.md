# Phase 0 — Setup

**Goal**: PR context and diff land in the workspace before anything else starts. This phase is round 1 only — a re-review round's setup is `references/phase-5-rereview.md`'s job, not this one.

- Confirm the PR branch is checked out locally and current with its remote — a stale branch anchors later inline comments to the wrong commit.
- Run `scripts/setup.py <workspace_path> [--exclude glob ...]` — it fetches metadata, saves the full diff, lays down the round-1 skeleton files. Refuses to run if `meta.json` already exists (use Phase 5 for the next round instead) or if the workspace has a pre-restructure flat `diff/`/`walkthrough/`/`review/` layout with no `meta.json`.
  - Machine-generated files and lockfiles are automatically excluded via `_constants.py`.
  - If the reviewer requests excluding tests, mocks, or specific directories (or for large PRs where tests should be scoped out), pass `--exclude` with framework-appropriate globs (e.g. `--exclude 'test/*' '*_test.dart' '*.feature'`). The agent chooses patterns based on the workspace tech stack. Configured excludes are saved in `meta.json` and automatically carried forward into subsequent rounds.
- Let the reviewer know `rounds/1/review/reviewer_review.md` is theirs from the moment the walkthrough starts — no need to wait for the review phase.

**Gotcha**: `gh` can fail with a TLS/certificate error (`x509: OSStatus -26276` or similar) when run inside the tool sandbox — it's a sandboxed-network issue, not a real auth or connectivity problem. Every script here that shells out to `gh` (`setup.py`, `post_comment.py`, `post_all.py`, `resolve_threads.py`) can hit this; retry the same command with the sandbox disabled rather than treating it as a `gh auth` problem. `diff_lines.py` never calls `gh` (it only reads the local patch file), so it's unaffected.

**Done when**: `meta.json`, `rounds/1/round.json`, `rounds/1/diff.patch`, and the three round-1 skeleton files exist, and the reviewer knows where their notes go.
