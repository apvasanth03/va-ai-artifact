#!/usr/bin/env python3
"""Create the round-1 workspace skeleton, or set up the next re-review round.

Usage:
  python setup.py <workspace_path>                 # round 1 (first time only)
  python setup.py <workspace_path> --round N        # N = current_round + 1: advance to the next round
  python setup.py <workspace_path> --round N        # N = current_round: refresh THIS round's head/diff in place
                                                     #   (e.g. after check_head_current says new commits landed)
  python setup.py <workspace_path> --force          # overwrite skeletons even if they hold content

Round 1 fetches full PR metadata, computes the full `base...HEAD` diff (filtering
generated files via .gitattributes linguist-generated, or a fallback pattern
list), and writes empty skeleton files for the walkthrough/review phases.

Round N>1 computes a *delta* diff — only what changed since the previous round's
headRefOid — and writes the lighter round-N skeleton (blind delta review +
classification of the previous round's final_review.md). If the previous round's
headRefOid is no longer reachable locally (force-push/rebase), falls back to the
full base...HEAD diff and says so — never fails silently.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import (
    gh, git, read_meta, write_meta, meta_exists, round_dir, read_round_meta,
    write_round_meta, changed_files, detect_generated, filter_files, scoped_diff,
    base_diff_range, delta_diff_range, commit_reachable,
)


def write_skeleton_file(path: str, stub: str, force: bool) -> None:
    """Write `stub` to `path` unless it already holds real progress.

    A re-run of setup.py (e.g. after an interrupted first attempt) must not
    silently destroy a reviewer's in-progress notes or an already-confirmed
    walkthrough. Only overwrite if the file is missing, still exactly the
    stub, or `--force` was passed.
    """
    if force or not os.path.exists(path):
        with open(path, "w") as f:
            f.write(stub)
        return
    with open(path) as f:
        current = f.read()
    if current == stub:
        with open(path, "w") as f:
            f.write(stub)
        return
    print(f"Skipped (has content) — {path} — pass --force to overwrite anyway", file=sys.stderr)


REVIEWER_STUB = """# Reviewer Review

Add your own findings as you go through the walkthrough — no format required
yet, informal notes are fine. Once the review phase starts, tighten each into:

```
#### <title> — [critical / major / minor]
- **File**: `path/to/file`
- **Line**: 42 or — (deletion-only)
- **Issue**: <one line, then a code/pseudo-code snippet>
- **Why**: <one line>
- **Suggestion**: <code snippet showing the fix>
```
"""

AGENT_STUB = """# Agent Review

_Filled in once the independent review phase runs. Do not read this file
until you're done with your own review — it's written blind to your notes,
and reading it early would anchor your findings on it._
"""

INDEX_STUB = """# Walkthrough

_The full walkthrough lands here: a section list, then one file per section.
Nothing here yet._
"""

def load_previous_open_items(workspace: str, round_num: int) -> list[dict]:
    """Read open items from round (round_num - 1)'s final_review.json.
    Items that are still open going into this round are:
    - newly posted items from round N-1 ("new" or legacy "open")
    - carried-over items that remained unfixed in round N-1 ("unresolved")
    """
    if round_num <= 1:
        return []
    prev_dir = round_dir(workspace, round_num - 1)
    json_path = os.path.join(prev_dir, "review", "final_review.json")
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                data = json.load(f)
            if "new" in data or "unresolved" in data:
                return data.get("new", []) + data.get("unresolved", [])
            return data.get("open", [])
        except Exception as e:
            print(f"[WARN] could not read {json_path}: {e}", file=sys.stderr)
    return []


def generate_reviewer_review_stub(open_items: list[dict], round_num: int) -> str:
    lines = [f"# Reviewer Review — Round {round_num}\n"]
    if open_items:
        lines.append("## Previous Round Open Items\n")
        lines.append("Review each item against the current code. Update Status if anything is not fixed:\n")
        lines.append("| # | Severity | File:Line | Issue Summary | Status [Fixed / Not Fixed / Partially Fixed / Moot] | Comment (optional) |")
        lines.append("|---|---|---|---|---|---|")
        for i, item in enumerate(open_items, 1):
            file_line = f"`{item.get('file', '')}:{item.get('line') or '—'}`"
            title = str(item.get("title", "")).replace("|", "\\|")
            lines.append(f"| {i} | {item.get('severity', 'minor')} | {file_line} | {title} | Fixed | |")
        lines.append("\n---\n")
    lines.append("## New Findings\n")
    lines.append("Add any regressions or new issues spotted in this round's delta diff (free-form notes or Concern Items):\n")
    lines.append("```\n#### <title> — [critical / major / minor]\n- **File**: `path/to/file`\n- **Line**: 42 or — (deletion-only)\n- **Issue**: <one line>\n- **Why**: <one line>\n- **Suggestion**: <snippet>\n```\n")
    return "\n".join(lines)


def generate_agent_review_stub(open_items: list[dict], round_num: int) -> str:
    lines = [f"# Agent Review — Round {round_num}\n"]
    if open_items:
        lines.append("## Previous Round Open Items\n")
        lines.append("| # | Comment ID | File:Line | Issue Summary | Status | Evidence | Reply (optional) |")
        lines.append("|---|---|---|---|---|---|---|")
        for i, item in enumerate(open_items, 1):
            file_line = f"`{item.get('file', '')}:{item.get('line') or '—'}`"
            cid = item.get("comment_id") or "—"
            title = str(item.get("title", "")).replace("|", "\\|")
            lines.append(f"| {i} | {cid} | {file_line} | {title} | | | |")
        lines.append("\n---\n")
    lines.append("## New Findings\n")
    lines.append("_Filled in during the independent delta review pass._\n")
    return "\n".join(lines)

ROUND_WALKTHROUGH_STUB = """# Walkthrough — this round's delta

_The walkthrough for this round's delta diff lands here: a section list, then one file per section._
"""


def setup_round_1(workspace: str, force: bool, exclude: list[str] | None = None) -> None:
    if meta_exists(workspace):
        meta = read_meta(workspace)
        print(
            f"{workspace}/meta.json already exists (current_round="
            f"{meta.get('current_round', '?')}). Use --round N to set up the "
            f"next round, not a bare setup.py call.",
            file=sys.stderr,
        )
        sys.exit(1)

    legacy = [d for d in ("diff", "walkthrough", "review")
              if os.path.isdir(os.path.join(workspace, d))]
    if legacy:
        print(
            f"{workspace} has a top-level {', '.join(legacy)}/ directory but no "
            f"meta.json — this looks like a pre-restructure (flat-layout) "
            f"workspace. This skill version only understands the rounds/<N>/ "
            f"layout; migrate manually or point setup.py at a fresh directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    r1_dir = round_dir(workspace, 1)
    for d in [r1_dir, os.path.join(r1_dir, "walkthrough"), os.path.join(r1_dir, "review")]:
        os.makedirs(d, exist_ok=True)

    # Owner/repo come from the local checkout, not the PR's headRepository —
    # for a fork-based PR, headRepository is the contributor's fork, but
    # comments must be posted against the repo the PR was opened in (the one
    # checked out locally).
    repo_info = gh("repo", "view", "--json", "nameWithOwner")
    owner, repo = repo_info["nameWithOwner"].split("/", 1)

    pr = gh("pr", "view", "--json", "number,title,body,baseRefName,headRefName")

    meta = {
        "pr_number":    pr["number"],
        "owner":        owner,
        "repo":         repo,
        "branch_name":  pr["headRefName"],
        "baseRefName":  pr["baseRefName"],
        "current_round": 1,
    }
    if exclude:
        meta["exclude"] = exclude
    write_meta(workspace, meta)
    print(f"meta.json written  — PR #{meta['pr_number']}: {pr['title']}")

    base = meta["baseRefName"]
    r = git("fetch", "origin", base)
    if r.returncode != 0:
        print(f"git fetch failed: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    diff_range = base_diff_range(base)
    all_files = changed_files(diff_range)
    kept_files, generated, user_excluded = filter_files(all_files, exclude)

    if generated:
        print(f"Generated skipped  — {len(generated)} file(s): {', '.join(sorted(generated)[:10])}"
              + (" ..." if len(generated) > 10 else ""))
    if user_excluded:
        print(f"Excluded skipped   — {len(user_excluded)} file(s): {', '.join(sorted(user_excluded)[:10])}"
              + (" ..." if len(user_excluded) > 10 else ""))

    try:
        diff_text = scoped_diff(diff_range, kept_files)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    diff_path = os.path.join(r1_dir, "diff.patch")
    with open(diff_path, "w") as f:
        f.write(diff_text)
    print(f"Diff saved         — {diff_path}")

    # headRefOid = local HEAD (what the diff was generated from) — anchors
    # inline comments to the right commit when posting.
    local_head = git("rev-parse", "HEAD")
    head_ref_oid = local_head.stdout.strip()
    write_round_meta(workspace, 1, {"round": 1, "headRefOid": head_ref_oid})
    print(f"headRefOid set     — {head_ref_oid[:8]}...")

    write_skeleton_file(os.path.join(r1_dir, "walkthrough", "index.md"), INDEX_STUB, force)
    write_skeleton_file(os.path.join(r1_dir, "review", "reviewer_review.md"), REVIEWER_STUB, force)
    write_skeleton_file(os.path.join(r1_dir, "review", "agent_review.md"), AGENT_STUB, force)
    print("Skeleton written   — walkthrough/index.md, review/reviewer_review.md, review/agent_review.md"
          " (any file already holding content was left alone — see warnings above, if any)")


def setup_round_n(workspace: str, round_num: int, force: bool, exclude: list[str] | None = None) -> None:
    if not meta_exists(workspace):
        print(f"{workspace}/meta.json not found — run setup.py without --round first.",
              file=sys.stderr)
        sys.exit(1)

    meta = read_meta(workspace)
    current = meta.get("current_round", 0)
    next_round = current + 1
    if round_num not in (current, next_round):
        print(
            f"--round {round_num} requested, but the workspace is at round "
            f"{current} — use --round {current} to refresh the current round's "
            f"head/diff (e.g. after check_head_current flags new commits), or "
            f"--round {next_round} to advance to the next round. Rounds are set "
            f"up sequentially, one at a time.",
            file=sys.stderr,
        )
        sys.exit(1)
    if round_num == 1:
        print("Round 1 is set up by a bare `setup.py <workspace>` call, not --round 1.",
              file=sys.stderr)
        sys.exit(1)

    prev_round_meta = read_round_meta(workspace, round_num - 1)
    previous_oid = prev_round_meta["headRefOid"]

    n_dir = round_dir(workspace, round_num)
    for d in [n_dir, os.path.join(n_dir, "walkthrough"), os.path.join(n_dir, "review")]:
        os.makedirs(d, exist_ok=True)

    base = meta["baseRefName"]
    r = git("fetch", "origin", base)
    if r.returncode != 0:
        print(f"git fetch failed: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    fallback_to_base = not commit_reachable(previous_oid)
    if fallback_to_base:
        print(
            f"WARNING: round {round_num - 1}'s headRefOid ({previous_oid[:8]}) is no "
            f"longer reachable locally — likely a force-push/rebase on the branch "
            f"since then. Falling back to the FULL base...HEAD diff for this round "
            f"instead of a delta; review it as if this were a fresh full pass, not "
            f"just what changed.",
            file=sys.stderr,
        )
        diff_range = base_diff_range(base)
    else:
        diff_range = delta_diff_range(previous_oid)

    if exclude is not None:
        meta["exclude"] = exclude
        write_meta(workspace, meta)
    exclude_patterns = meta.get("exclude", [])

    all_files = changed_files(diff_range)
    kept_files, generated, user_excluded = filter_files(all_files, exclude_patterns)

    if generated:
        print(f"Generated skipped  — {len(generated)} file(s): {', '.join(sorted(generated)[:10])}"
              + (" ..." if len(generated) > 10 else ""))
    if user_excluded:
        print(f"Excluded skipped   — {len(user_excluded)} file(s): {', '.join(sorted(user_excluded)[:10])}"
              + (" ..." if len(user_excluded) > 10 else ""))

    try:
        diff_text = scoped_diff(diff_range, kept_files)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    diff_path = os.path.join(n_dir, "diff.patch")
    with open(diff_path, "w") as f:
        f.write(diff_text)
    print(f"Diff saved         — {diff_path} ({'full base diff (fallback)' if fallback_to_base else 'delta since round ' + str(round_num - 1)})")

    local_head = git("rev-parse", "HEAD")
    head_ref_oid = local_head.stdout.strip()
    write_round_meta(workspace, round_num, {
        "round": round_num,
        "headRefOid": head_ref_oid,
        "previous_round_headRefOid": previous_oid,
        "delta_fallback_to_base": fallback_to_base,
    })
    print(f"headRefOid set     — {head_ref_oid[:8]}...")

    meta["current_round"] = round_num
    write_meta(workspace, meta)

    open_items = load_previous_open_items(workspace, round_num)
    reviewer_stub = generate_reviewer_review_stub(open_items, round_num)
    agent_stub = generate_agent_review_stub(open_items, round_num)

    write_skeleton_file(os.path.join(n_dir, "walkthrough", "index.md"), ROUND_WALKTHROUGH_STUB, force)
    write_skeleton_file(os.path.join(n_dir, "review", "reviewer_review.md"), reviewer_stub, force)
    write_skeleton_file(os.path.join(n_dir, "review", "agent_review.md"), agent_stub, force)
    print(f"Skeleton written   — round {round_num}: walkthrough/index.md, "
          f"review/{{reviewer_review.md, agent_review.md}}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--round", type=int,
                     help="current_round + 1 to advance, or current_round itself to refresh in place")
    ap.add_argument("--force", action="store_true",
                     help="overwrite skeleton files even if they already have content")
    ap.add_argument("--exclude", nargs="*", default=None,
                     help="globs to exclude from the diff (e.g. 'test/*' '*_test.dart')")
    args = ap.parse_args()

    if args.round is None:
        setup_round_1(args.workspace, args.force, args.exclude)
    else:
        setup_round_n(args.workspace, args.round, args.force, args.exclude)


if __name__ == "__main__":
    main()
