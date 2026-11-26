#!/usr/bin/env python3
"""Round state: where the round stands, and the two gates recorded by script.

Usage:
  python round.py status        <workspace> [--round N]
  python round.py plan-approved <workspace> [--round N]
  python round.py commit        <workspace> <sha> [--round N]

status         prints the resume point as JSON. Phase is derived from the files:
                 walk   a thread in comments.json has no item yet
                 plan   a fix exists and plan_approved is false
                 fix    plan approved, no commit_sha (uncommitted_changes tells
                        implement/verify apart from ready-to-commit)
                 push   commit_sha is not on origin/<branch>
                 post   an item has no reply_id
                 done   every item is posted (or the round had no threads)
plan-approved  records the user's plan approval; needs every thread decided,
               at least one fix, and rounds/N/plan.md.
commit <sha>   records the round commit; needs plan approval, <sha> = HEAD,
               and a clean working tree.
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
from _utils import (fail, read_json, write_json, read_meta, round_dir, comments_path, replies_path,
                    read_replies, resolve_round, git, git_out, git_fetch)


def load(ws: str, n: int):
    if not os.path.exists(comments_path(ws, n)):
        fail(f"round {n} is not set up")
    threads = read_json(comments_path(ws, n))["threads"]
    return threads, read_replies(ws, n)


def on_remote(sha: str, branch: str) -> bool:
    git_fetch(branch)
    return git("merge-base", "--is-ancestor", sha, f"origin/{branch}").returncode == 0


def status(ws: str, n: int) -> dict:
    meta = read_meta(ws)
    threads, data = load(ws, n)
    items = data["items"]
    decided = {i["n"] for i in items}
    counts = {d: sum(i["decision"] == d for i in items) for d in ("fix", "clarify", "skip")}
    out = {"round": n, "total": len(threads), "decided": len(decided), **counts,
           "plan_approved": data["plan_approved"], "commit_sha": data["commit_sha"],
           "posted": sum(bool(i["reply_id"]) for i in items),
           "deviations": [i["n"] for i in items if i["deviation"]]}
    pending = [t["n"] for t in threads if t["n"] not in decided]
    if pending:
        phase = "walk"
        out["pending"] = pending
    elif counts["fix"] and not data["plan_approved"]:
        phase = "plan"
    elif counts["fix"] and not data["commit_sha"]:
        phase = "fix"
        out["uncommitted_changes"] = bool(git_out("status", "--porcelain"))
    elif counts["fix"] and not on_remote(data["commit_sha"], meta["branch"]):
        phase = "push"
    elif any(not i["reply_id"] for i in items):
        phase = "post"
    else:
        phase = "done"
    return {"phase": phase, **out}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["status", "plan-approved", "commit"])
    ap.add_argument("workspace")
    ap.add_argument("sha", nargs="?")
    ap.add_argument("--round", type=int)
    args = ap.parse_args()
    ws, n = args.workspace, resolve_round(args.workspace, args.round)

    if args.action == "status":
        print(json.dumps(status(ws, n)))
        return

    threads, data = load(ws, n)
    if args.action == "plan-approved":
        decided = {i["n"] for i in data["items"]}
        pending = [t["n"] for t in threads if t["n"] not in decided]
        if pending:
            fail(f"threads #{pending} are undecided")
        if not any(i["decision"] == "fix" for i in data["items"]):
            fail("no fix in this round; there is no plan to approve")
        if not os.path.exists(os.path.join(round_dir(ws, n), "plan.md")):
            fail(f"{round_dir(ws, n)}/plan.md not found")
        data["plan_approved"] = True
        write_json(replies_path(ws, n), data)
        print(f"Round {n}: plan approved")
        return

    if not args.sha:
        fail("commit needs <sha>")
    if not data["plan_approved"]:
        fail("plan is not approved yet")
    if any(i["reply_id"] and i["decision"] == "fix" for i in data["items"]):
        fail("fix replies are already posted with the recorded commit; it can't change now")
    sha = git_out("rev-parse", f"{args.sha}^{{commit}}")
    if sha != git_out("rev-parse", "HEAD"):
        fail(f"{sha[:7]} is not HEAD; the round commit is the last commit")
    if git_out("status", "--porcelain"):
        fail("working tree has uncommitted changes; they would be left out of the round commit")
    data["commit_sha"] = sha
    write_json(replies_path(ws, n), data)
    print(f"Round {n}: commit {sha[:7]} recorded")


if __name__ == "__main__":
    main()
