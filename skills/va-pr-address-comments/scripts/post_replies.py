#!/usr/bin/env python3
"""Post the round's approved replies from final_replies.json.

Usage:
  python post_replies.py <workspace> [--round N] [--dry-run]

Refuses unless every thread is decided and, when the round has a fix, the
recorded commit_sha is on origin/<branch>. For each item without a reply_id:
fills {sha} with the 7-char commit, appends the marker
`<!-- va-pr-address-comments r<N> -->`, replies on the thread, and writes
reply_id and url back at once. Threads are never resolved.

Idempotent: an item with a reply_id is skipped, and a reply already on GitHub
carrying this round's marker is adopted instead of posted again. Safe to
re-run after a partial failure. Prints one line per item, then a JSON summary;
exits non-zero if any post failed.
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from _constants import MARKER_FORMAT
from _utils import (fail, read_json, write_json, read_meta, comments_path, replies_path, read_replies,
                    resolve_round, reply_to_comment, list_pr_comments, git, git_fetch)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workspace")
    ap.add_argument("--round", type=int)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ws = args.workspace
    n = resolve_round(ws, args.round)
    meta = read_meta(ws)
    threads = read_json(comments_path(ws, n))["threads"]
    data = read_replies(ws, n)
    items = data["items"]

    decided = {i["n"] for i in items}
    pending = [t["n"] for t in threads if t["n"] not in decided]
    if pending:
        fail(f"threads #{pending} are undecided")

    sha7 = None
    if any(i["decision"] == "fix" for i in items):
        sha = data["commit_sha"]
        if not sha:
            fail("the round has fixes but no commit_sha (round.py commit)")
        git_fetch(meta["branch"])
        if git("merge-base", "--is-ancestor", sha, f"origin/{meta['branch']}").returncode != 0:
            fail(f"{sha[:7]} is not on origin/{meta['branch']}; push first")
        sha7 = sha[:7]

    marker = MARKER_FORMAT.format(round=n)
    todo = [i for i in items if not i["reply_id"]]
    existing = {}
    if todo:
        for c in list_pr_comments(meta["owner"], meta["repo"], meta["pr_number"]):
            if marker in (c.get("body") or "") and c.get("in_reply_to_id"):
                existing[c["in_reply_to_id"]] = {"reply_id": c["id"], "url": c["html_url"]}

    posted = adopted = failed = 0
    for item in items:
        if item["reply_id"]:
            print(f"[SKIP] #{item['n']} already posted")
            continue
        body = item["reply"].replace("{sha}", sha7 or "") + "\n\n" + marker
        tag = f"#{item['n']} {item['decision']}" + (" (deviation)" if item["deviation"] else "")
        if args.dry_run:
            print(f"[DRY] {tag} → {item['comment_id']}\n      {body.splitlines()[0][:120]}")
            continue
        if item["comment_id"] in existing:
            item.update(existing[item["comment_id"]])
            adopted += 1
            print(f"[ADOPT] {tag} {item['url']}")
        else:
            try:
                item.update(reply_to_comment(meta["owner"], meta["repo"], meta["pr_number"],
                                             item["comment_id"], body))
                posted += 1
                print(f"[OK] {tag} {item['url']}")
            except RuntimeError as e:
                failed += 1
                print(f"[FAIL] {tag}: {e}", file=sys.stderr)
                continue
        write_json(replies_path(ws, n), data)

    print(json.dumps({"round": n, "posted": posted, "adopted": adopted, "failed": failed,
                      "total": len(items), "done": sum(bool(i["reply_id"]) for i in items),
                      "dry_run": args.dry_run}))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
