#!/usr/bin/env python3
"""Post every not-yet-posted entry in a round's final_review.json, in one call.

Usage:
  python post_all.py <workspace_path> [--round N] [--dry-run]

Idempotent: an entry that already has a `comment_id` field is skipped (assumed
already posted) rather than re-posted. On each successful post, the returned
comment ID is written back into final_review.json immediately — so a crash mid-run
never leaves a posted comment with no record of it.

Prints one line per entry (posted / skipped / failed) and a JSON summary at
the end. Exits non-zero if any entry failed to post.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import (
    read_meta, read_round_meta, round_dir, current_round,
    post_inline, post_file_level, check_head_current,
)


def format_field(label: str, value: str) -> str:
    val = (value or "").strip()
    if not val:
        return ""
    if "\n" in val or val.startswith("```"):
        return f"**{label}**:\n{val}"
    return f"**{label}**: {val}"


def format_body(e: dict) -> str:
    parts = [f"**[{e.get('severity', 'minor')}]** {e.get('title', '')}"]
    for field in ("Issue", "Why", "Suggestion"):
        formatted = format_field(field, e.get(field.lower(), ""))
        if formatted:
            parts.append(formatted)
    return "\n\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--round", type=int, help="defaults to the workspace's current round")
    ap.add_argument("--dry-run", action="store_true", help="parse + print, don't post")
    ap.add_argument("--force", action="store_true",
                     help="post even if the PR head has moved since round setup")
    args = ap.parse_args()

    round_num = args.round if args.round is not None else current_round(args.workspace)
    rev_dir = os.path.join(round_dir(args.workspace, round_num), "review")
    json_path = os.path.join(rev_dir, "final_review.json")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(json_path) as f:
        review_data = json.load(f)

    entries = review_data.get("new", review_data.get("open", []))

    meta = read_meta(args.workspace)
    round_meta = read_round_meta(args.workspace, round_num)

    if not args.dry_run and not args.force:
        warning = check_head_current(meta["owner"], meta["repo"], meta["pr_number"], round_meta["headRefOid"])
        if warning:
            print(warning, file=sys.stderr)
            sys.exit(1)

    results, failed = [], False

    for e in entries:
        tag = e.get("title", "")[:70]
        posted_id = e.get("comment_id")
        if posted_id is not None:
            status_desc = f", {e.get('status')}" if e.get("status") else ""
            print(f"[skip] already posted ({posted_id}{status_desc}) — existing thread handled by resolve_threads.py — {tag}")
            continue

        if not e.get("file"):
            print(f"[SKIP] no File recorded (required even for a deletion-only finding) — {tag}",
                  file=sys.stderr)
            failed = True
            continue

        if args.dry_run:
            kind = "inline" if e.get("line") else "file-level"
            print(f"[dry-run] would post ({kind}, {e.get('severity', 'minor')}) {e['file']}:{e.get('line') or '—'} — {tag}")
            continue

        body = format_body(e)
        try:
            if e.get("line"):
                result = post_inline(meta["owner"], meta["repo"], meta["pr_number"],
                                      round_meta["headRefOid"], e["file"], int(e["line"]), None, body)
            else:
                result = post_file_level(meta["owner"], meta["repo"], meta["pr_number"],
                                          round_meta["headRefOid"], e["file"], body)
        except RuntimeError as ex:
            print(f"[FAIL] {tag}: {ex}", file=sys.stderr)
            failed = True
            continue

        print(f"[posted] {tag} -> {result['url']}")
        results.append({**result, "title": e["title"]})

        # Write the ID back immediately
        e["comment_id"] = result["comment_id"]
        e["url"] = result["url"]
        with open(json_path, "w") as f:
            json.dump(review_data, f, indent=2)

    print("\n--- SUMMARY ---")
    print(json.dumps(results, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
