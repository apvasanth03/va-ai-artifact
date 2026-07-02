# Phase 0 — Setup

## Step 1 — Confirm branch

### Main Agent
Confirm the PR branch is checked out. If not, ask reviewer to check it out first. Once confirmed, ensure local is up to date:
```bash
git pull origin <branch_name>
```
Required because `setup.py` uses local HEAD as `headRefOid` — if local is behind remote, inline comments anchor to the wrong commit.

---

## Step 2 — Collect ticket context

### Main Agent
If not provided as args, ask:
> "Please share the ticket title, description, and acceptance criteria — or say 'use PR description' to skip."

---

## Step 3 — Write ticket context and run setup

### Main Agent
Write reviewer's input to `<workspace_path>/ticket.md`. Then run:
```bash
python scripts/setup.py <workspace_path>
```
Creates workspace directories, fetches PR metadata via `gh pr view`, writes `meta.json`, filters out generated files (via `.gitattributes` `linguist-generated` or a generic fallback pattern list — logged so the reviewer can spot misses), then saves the filtered diff to `diff/round-1.patch`.

---

## Step 4 — Create reviewer concerns file

### Main Agent
Write `<workspace_path>/concerns/round-1-reviewer.md`:
```markdown
# Reviewer Concerns — Round 1

Add your own concerns below as you go through the walkthrough. Free-form is fine — one item per finding, mention file/line if you can.
```
Gives the reviewer a place to capture their own findings independently of the sub-agent's review, so neither anchors the other. Referenced again at the end of Phase 1 and read back in Phase 2 Part C.
