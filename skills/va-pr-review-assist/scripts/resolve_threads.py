#!/usr/bin/env python3
"""Phase 4 Step 7: Resolve confirmed GitHub review threads.

Usage: python resolve_threads.py <workspace_path> <resolve_file>

<resolve_file> is a plain-text file with one Thread ID (PRRT_...) per line,
written by the main agent in Phase 4 Step 6 after reviewer confirmation.

Resolves each thread via GraphQL and moves the corresponding entries from
comments/comments.md to comments/comments_resolved.md.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from _utils import read_meta, read_comments, write_comments, append_to_resolved


RESOLVE_MUTATION = """
mutation {{
  resolveReviewThread(input: {{threadId: "{thread_id}"}}) {{
    thread {{ isResolved }}
  }}
}}"""


def resolve_thread(thread_id: str) -> bool:
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={RESOLVE_MUTATION.format(thread_id=thread_id)}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR resolving {thread_id}: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: resolve_threads.py <workspace> <resolve_file>", file=sys.stderr)
        sys.exit(1)

    workspace    = sys.argv[1]
    resolve_file = sys.argv[2]

    with open(resolve_file) as f:
        thread_ids = {line.strip() for line in f if line.strip()}

    if not thread_ids:
        print("No thread IDs to resolve.")
        return

    concerns = read_comments(workspace)
    still_open = []
    resolved = []

    for concern in concerns:
        tid = concern.get("thread_id", "")
        if tid in thread_ids:
            print(f"Resolving: {concern['title']} ({tid})")
            if resolve_thread(tid):
                resolved.append(concern)
                print(f"  ✓ resolved")
            else:
                still_open.append(concern)
        else:
            still_open.append(concern)

    if resolved:
        append_to_resolved(workspace, resolved)
        write_comments(workspace, still_open)
        print(f"\nResolved {len(resolved)} thread(s).")
    else:
        print("No threads were resolved.")


if __name__ == "__main__":
    main()
