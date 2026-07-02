#!/usr/bin/env python3
"""Phase 4 Step 1: Fetch new commits, save incremental diff, update headRefOid.

Usage: python prepare_round.py <workspace_path>

Prints JSON: {"new_oid": "...", "round_n": N, "force_pushed": false}
Exits with code 1 (prints error JSON) if no new commits since last review.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import git, read_meta, write_meta


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: prepare_round.py <workspace_path>", file=sys.stderr)
        sys.exit(1)

    workspace    = sys.argv[1]
    meta         = read_meta(workspace)
    branch       = meta["branch_name"]
    reviewed_oid = meta["reviewed_oid"]
    round_n      = meta["round"] + 1

    r = git("fetch", "origin", branch)
    if r.returncode != 0:
        print(f"git fetch failed: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)

    r = git("rev-parse", f"origin/{branch}")
    if r.returncode != 0 or not r.stdout.strip():
        print(f"git rev-parse failed: {r.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    new_oid = r.stdout.strip()

    if new_oid == reviewed_oid:
        print(json.dumps({"error": "no_new_commits"}))
        sys.exit(1)

    # Exit code non-zero means reviewed_oid is not an ancestor → force-push
    force_pushed = git("merge-base", "--is-ancestor", reviewed_oid, new_oid).returncode != 0

    diff_path = os.path.join(workspace, "diff", f"round-{round_n}.patch")
    with open(diff_path, "w") as f:
        f.write(git("diff", f"{reviewed_oid}..{new_oid}").stdout)

    # Update headRefOid now so post_concerns.py anchors comments to the new commit in Step 7
    meta["headRefOid"] = new_oid
    write_meta(workspace, meta)

    print(json.dumps({
        "new_oid":      new_oid,
        "round_n":      round_n,
        "force_pushed": force_pushed,
    }))


if __name__ == "__main__":
    main()
