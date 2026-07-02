#!/usr/bin/env python3
"""Phase 3 / Phase 4 Step 7: Post concern items as PR comments.

Usage: python post_concerns.py <workspace_path> <concerns_file>

Reads concerns from <concerns_file>, posts each to GitHub, then appends
the full Concern Item (with Comment ID, Thread ID, URL) to comments/comments.md.
"""
import os, re, sys, json, subprocess

_RANGE_RE = re.compile(r"^(\d+)\s*-\s*(\d+)$")
sys.path.insert(0, os.path.dirname(__file__))
from _utils import (
    read_meta, parse_concerns, format_body,
    append_to_comments, fetch_thread_map,
)


def post_inline(owner: str, repo: str, pr_number: int, headRefOid: str,
                concern: dict) -> tuple[int | None, str | None]:
    lines = concern.get("lines", "—")
    file_path = concern.get("file", "")
    body = format_body(concern)

    args = [
        "gh", "api", f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
        "--method", "POST",
        "-f", f"body={body}",
        "-f", f"commit_id={headRefOid}",
        "-f", f"path={file_path}",
        "-f", "side=RIGHT",
    ]

    m = _RANGE_RE.match(lines)
    if m:
        args += ["-F", f"start_line={m.group(1)}", "-F", f"line={m.group(2)}", "-f", "start_side=RIGHT"]
    else:
        args += ["-F", f"line={lines}"]

    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR posting inline: {result.stderr.strip()}", file=sys.stderr)
        return None, None

    resp = json.loads(result.stdout)
    return resp["id"], resp["html_url"]


def post_general(pr_number: int, concern: dict) -> tuple[None, str | None]:
    file_info = f"**File**: `{concern['file']}`\n\n" if concern.get("file") else ""
    body = file_info + format_body(concern)
    result = subprocess.run(
        ["gh", "pr", "comment", str(pr_number), "--body", body],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR posting general comment: {result.stderr.strip()}", file=sys.stderr)
        return None, None
    # gh pr comment prints the URL on stdout
    url = result.stdout.strip() or None
    return None, url


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: post_concerns.py <workspace> <concerns_file>", file=sys.stderr)
        sys.exit(1)

    workspace     = sys.argv[1]
    concerns_file = sys.argv[2]

    meta       = read_meta(workspace)
    owner      = meta["owner"]
    repo       = meta["repo"]
    pr_number  = meta["pr_number"]
    headRefOid = meta["headRefOid"]

    concerns = parse_concerns(concerns_file)
    if not concerns:
        print("No concerns to post.")
        return

    posted = []
    for concern in concerns:
        lines = concern.get("lines", "—")
        print(f"Posting: {concern['title']}")

        if lines == "—":
            comment_id, url = post_general(pr_number, concern)
        else:
            comment_id, url = post_inline(owner, repo, pr_number, headRefOid, concern)

        concern["comment_id"] = str(comment_id) if comment_id else ""
        concern["thread_id"]  = ""  # populated below
        concern["url"]        = url or ""
        posted.append(concern)
        print(f"  → {url}")

    # Fetch thread node IDs for all inline posts in one GraphQL call
    inline_posted = [c for c in posted if c["comment_id"]]
    if inline_posted:
        thread_map = fetch_thread_map(owner, repo, pr_number)
        for concern in inline_posted:
            cid = int(concern["comment_id"])
            concern["thread_id"] = thread_map.get(cid, "")

    append_to_comments(workspace, posted)
    print(f"\nPosted {len(posted)} comment(s) → comments/comments.md updated.")


if __name__ == "__main__":
    main()
