#!/usr/bin/env python3
"""Post one comment to the PR — inline on a file/line, or file-level.

Usage:
  python post_comment.py <workspace_path> --body <text> --file <path> --line <n> [--line-end <n>] [--round N]
  python post_comment.py <workspace_path> --body <text> --file <path>              # file-level (no line)

`--file` is always required — there's no PR-level (issue) comment path here;
every comment anchors to a file, either on a specific line or, with `--line`
omitted, file-level (subject_type=file — a real, resolvable review thread).

Prints JSON: {"comment_id": 123, "url": "https://..."}. This is a one-off
outside the reconciled list — nothing here gets recorded anywhere, unlike
post_all.py's Comment ID write-back.

Caller builds the full markdown body itself; this script does no formatting
or file parsing — it just performs the one gh operation.
"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _utils import read_meta, read_round_meta, current_round, post_inline, post_file_level, check_head_current


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument("--body", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--line", type=int)
    parser.add_argument("--line-end", type=int)
    parser.add_argument("--round", type=int, help="defaults to the workspace's current round")
    parser.add_argument("--force", action="store_true",
                         help="post even if the PR head has moved since round setup")
    args = parser.parse_args()

    meta = read_meta(args.workspace)
    round_num = args.round if args.round is not None else current_round(args.workspace)
    round_meta = read_round_meta(args.workspace, round_num)

    if not args.force:
        warning = check_head_current(meta["owner"], meta["repo"], meta["pr_number"], round_meta["headRefOid"])
        if warning:
            print(warning, file=sys.stderr)
            sys.exit(1)

    try:
        if args.line:
            result = post_inline(
                meta["owner"], meta["repo"], meta["pr_number"], round_meta["headRefOid"],
                args.file, args.line, args.line_end, args.body,
            )
        else:
            result = post_file_level(
                meta["owner"], meta["repo"], meta["pr_number"], round_meta["headRefOid"],
                args.file, args.body,
            )
    except RuntimeError as e:
        print(f"gh error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
