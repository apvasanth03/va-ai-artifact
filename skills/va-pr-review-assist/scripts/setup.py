#!/usr/bin/env python3
"""Phase 0: Create workspace, write meta.json, save diff.

Usage: python setup.py <workspace_path>

Gets the changed-file list first, filters out generated files (via
.gitattributes linguist-generated, plus a generic fallback pattern list),
then writes the diff scoped to only the remaining files — so the saved
patch never carries generated-file noise, on every PR regardless of size.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import gh, git, write_meta, changed_files, detect_generated, scoped_diff


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: setup.py <workspace_path>", file=sys.stderr)
        sys.exit(1)

    workspace = sys.argv[1]

    # Create workspace directories
    for d in ["diff", "walkthrough", "concerns", "comments"]:
        os.makedirs(os.path.join(workspace, d), exist_ok=True)

    # Fetch PR and repo metadata
    pr = gh("pr", "view", "--json", "number,title,body,baseRefName,headRefName,headRefOid,headRepository")

    meta = {
        "pr_number":    pr["number"],
        "owner":        pr["headRepository"]["nameWithOwner"].split("/")[0],
        "repo":         pr["headRepository"]["name"],
        "branch_name":  pr["headRefName"],
        "headRefOid":   pr["headRefOid"],
        "baseRefName":  pr["baseRefName"],
        "reviewed_oid": pr["headRefOid"],
        "round":        1,
    }
    write_meta(workspace, meta)
    print(f"meta.json written  — PR #{meta['pr_number']}: {pr['title']}")

    # Fetch remote base and save diff
    base = meta["baseRefName"]
    r = git("fetch", "origin", base)
    if r.returncode != 0:
        print(f"git fetch failed: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    all_files = changed_files(base)
    generated = detect_generated(all_files)
    kept_files = [f for f in all_files if f not in generated]

    if generated:
        print(f"Generated skipped  — {len(generated)} file(s): {', '.join(sorted(generated)[:10])}"
              + (" ..." if len(generated) > 10 else ""))

    try:
        diff_text = scoped_diff(base, kept_files)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    diff_path = os.path.join(workspace, "diff", "round-1.patch")
    with open(diff_path, "w") as f:
        f.write(diff_text)
    print(f"Diff saved         — {diff_path}")

    # Both reviewed_oid and headRefOid = local HEAD (what the diff was generated from).
    # headRefOid is used as commit_id when posting inline comments — must match the diff source.
    local_head = git("rev-parse", "HEAD")
    meta["reviewed_oid"] = local_head.stdout.strip()
    meta["headRefOid"] = local_head.stdout.strip()
    write_meta(workspace, meta)
    print(f"reviewed_oid set   — {meta['reviewed_oid'][:8]}...")


if __name__ == "__main__":
    main()
