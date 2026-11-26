# Phase 0 — Setup

**Goal:** the PR's context and diff are in the workspace before anything else starts. Round 1 only; a re-review round's setup is in `references/phase-5-rereview.md`.

## Steps

1. **Check the branch.** The PR branch is checked out locally and current with its remote. A stale branch anchors later inline comments to the wrong commit.
2. **Run setup.**
   ```bash
   python scripts/setup.py <workspace_path> [--exclude glob ...]
   ```
   It fetches the PR metadata, saves the full diff and writes the round-1 skeleton files.
3. **Tell the reviewer** that `rounds/1/review/reviewer_review.md` is theirs from the moment the walkthrough starts; they don't have to wait for the review phase.

## Excluding files

- Machine-generated files and lockfiles are excluded automatically (list in `scripts/_constants.py`).
- Pass `--exclude` when the reviewer asks to leave out tests, mocks or directories, or to scope tests out of a large PR. Choose globs for the workspace's tech stack, e.g. `--exclude 'test/*' '*_test.dart' '*.feature'`.
- Excludes are saved in `meta.json` and carried into later rounds.

## When setup refuses

- `meta.json` already exists: this is not round 1, so use Phase 5.
- The workspace has the old flat layout (`diff/`, `walkthrough/`, `review/` with no `meta.json`).

**Done when:** `meta.json`, `rounds/1/round.json`, `rounds/1/diff.patch` and the three round-1 skeleton files exist, and the reviewer knows where their notes go.
