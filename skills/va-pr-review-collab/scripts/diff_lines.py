#!/usr/bin/env python3
"""Print a file's `+`-side hunk line ranges from a round's diff.patch.

Lets an agent (or reviewer) sanity-check a `Line:` claim in one cheap call
instead of Reading the whole file to eyeball line numbers. For files that are
entirely new in the diff, current-file line numbers happen to equal diff line
numbers — but for *modified* files they can drift, which is exactly the class
of mistake this catches before a Concern Item's Line field is written down.

Usage:
  python diff_lines.py <workspace_path> <file_path_in_repo> [--round N]

Defaults to the workspace's current round. Prints one line per hunk:
"<new_start>-<new_end>" (inclusive, `+`-side only). A `Line:` value must fall
within one of these ranges to be postable.
"""
import argparse, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import current_round, round_dir

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+) b/(.+)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("file")
    ap.add_argument("--round", type=int, help="defaults to the workspace's current round")
    args = ap.parse_args()

    round_num = args.round if args.round is not None else current_round(args.workspace)
    patch_path = os.path.join(round_dir(args.workspace, round_num), "diff.patch")
    with open(patch_path) as f:
        lines = f.read().splitlines()

    in_file = False
    found = False
    for line in lines:
        if line.startswith("diff --git "):
            # Exact path match on the a/ or b/ side — a substring check here
            # would match "data.py" when asked for "a.py", silently mixing
            # hunks from the wrong file into the result.
            m = DIFF_HEADER_RE.match(line)
            in_file = bool(m) and (m.group(1) == args.file or m.group(2) == args.file)
            continue
        if not in_file:
            continue
        m = HUNK_RE.match(line)
        if m:
            start = int(m.group(1))
            count = int(m.group(2)) if m.group(2) else 1
            end = start + max(count - 1, 0)
            print(f"{start}-{end}")
            found = True

    if not found:
        print(f"no hunks found for {args.file!r} in {patch_path} (round {round_num})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
