#!/usr/bin/env python3
"""Phase 4 Step 2: Sync resolved state from GitHub.

Usage: python sync_resolved.py <workspace_path>

Queries GitHub for review threads that have been resolved (e.g., via the
GitHub UI). Moves matching entries from comments/comments.md to
comments/comments_resolved.md.

Prints a summary of what was moved.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import (
    read_meta, read_comments, write_comments,
    append_to_resolved, fetch_resolved_ids,
)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: sync_resolved.py <workspace>", file=sys.stderr)
        sys.exit(1)

    workspace = sys.argv[1]
    meta      = read_meta(workspace)

    concerns = read_comments(workspace)
    if not concerns:
        print("comments/comments.md is empty — nothing to sync.")
        return

    resolved_ids = fetch_resolved_ids(meta["owner"], meta["repo"], meta["pr_number"])

    still_open = []
    now_resolved = []

    for concern in concerns:
        cid = concern.get("comment_id", "")
        if cid.isdigit() and int(cid) in resolved_ids:
            now_resolved.append(concern)
        else:
            still_open.append(concern)

    if now_resolved:
        append_to_resolved(workspace, now_resolved)
        write_comments(workspace, still_open)
        print(f"Moved {len(now_resolved)} resolved concern(s) to comments_resolved.md:")
        for c in now_resolved:
            print(f"  ✓ {c['title']}")
    else:
        print("No newly resolved concerns found.")

    print(f"{len(still_open)} concern(s) still open.")


if __name__ == "__main__":
    main()
