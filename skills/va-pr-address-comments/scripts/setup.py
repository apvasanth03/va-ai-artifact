#!/usr/bin/env python3
"""Start a round: check preconditions, fetch and clean unresolved review threads,
select the ones to walk, and write the round's files.

Usage:
  python setup.py <workspace> [--pr N] [--exclude GLOB ...]      # round 1
  python setup.py <workspace> --round N [--exclude GLOB ...]     # N = current_round + 1

Run from inside the PR's repository with the PR branch checked out.

Preconditions (refuses and names the failed check):
  - the PR branch is checked out;
  - it matches origin after `git fetch` (nothing to pull, nothing unpushed);
  - the working tree is clean (untracked files included);
  - round N > 1: the previous round has posted every reply.

Writes:
  meta.json                      round 1; current_round updated every round
                                 {pr_number, owner, repo, url, title, branch, base,
                                  viewer, current_round, excludes}
  rounds/N/round.json            {round, headRefOid, fetched_at}
  rounds/N/comments.json         {threads: [...], waiting: [...]}, read-only afterwards
      thread: n, comment_id (root comment databaseId; replies go there), url,
              author, is_bot, path, line (originalLine when outdated), outdated,
              severity (null if the bot label can't be parsed), title, body (cleaned),
              replies [{author, ours, body (cleaned), at}],
              earlier ({round, decision, reply} from an earlier round, else null),
              reviewer_replied
      waiting: comment_id, path, line, title, decision, replied_at
  rounds/N/comment_queue.md      one row per walk thread; the agent fills Group

Bot noise (AI-agent prompts, analysis chains, executed scripts, learnings,
HTML comments, icons) is stripped before anything is written; no raw copy is kept.

Prints the counts and a change map (diff --numstat vs origin/<base>, generated
files and --exclude globs filtered, rolled up by directory).
"""
import argparse, fnmatch, json, os, sys
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from _utils import (fail, read_json, write_json, meta_path, read_meta, round_dir, comments_path,
                    queue_path, read_replies, gh_json, git, git_out, git_fetch, detect_generated)
from _threads import fetch_threads, select

MAX_MAP_ROWS = 12


def check_preconditions(branch: str) -> str:
    current = git_out("branch", "--show-current")
    if current != branch:
        fail(f"[branch] PR branch is '{branch}' but '{current}' is checked out. Check out the PR branch.")
    git_fetch(branch)
    head = git_out("rev-parse", "HEAD")
    remote = git_out("rev-parse", f"origin/{branch}")
    if head != remote:
        ahead = git_out("rev-list", "--count", f"origin/{branch}..HEAD")
        behind = git_out("rev-list", "--count", f"HEAD..origin/{branch}")
        fail(f"[sync] '{branch}' is {ahead} ahead / {behind} behind origin. Push or pull, then re-run.")
    dirty = git_out("status", "--porcelain")
    if dirty:
        fail(f"[clean] working tree has changes:\n{dirty}\nCommit, stash or remove them, then re-run.")
    return head


def earlier_decisions(ws: str, upto: int) -> dict[int, dict]:
    """Latest decision per thread across rounds 1..upto-1."""
    out = {}
    for r in range(1, upto):
        for item in read_replies(ws, r)["items"]:
            out[item["comment_id"]] = {"round": r, "decision": item["decision"], "reply": item["reply"]}
    return out


def change_map(base: str, excludes: list[str]) -> tuple[list[tuple], int, int]:
    git_fetch(base)
    rows = []
    for line in git_out("diff", "--numstat", "--no-renames", f"origin/{base}...HEAD").splitlines():
        add, dele, path = line.split("\t", 2)
        rows.append((path, int(add) if add.isdigit() else 0, int(dele) if dele.isdigit() else 0))
    generated = detect_generated([r[0] for r in rows])
    kept = [r for r in rows if r[0] not in generated and not any(fnmatch.fnmatch(r[0], g) for g in excludes)]
    excluded = len(rows) - len(kept) - len(generated)

    def bucket(prefix: str) -> dict[str, list]:
        """Files under `prefix`, grouped by their next directory level."""
        depth = len(prefix.split("/")) if prefix else 0
        agg = defaultdict(lambda: [0, 0, 0])
        for path, a, d in kept:
            dirs = path.split("/")[:-1]
            if prefix and dirs[:depth] != prefix.split("/"):
                continue
            key = "/".join(dirs[:depth + 1]) if len(dirs) > depth else (prefix or ".")
            agg[key][0] += 1; agg[key][1] += a; agg[key][2] += d
        return agg

    # Start from top-level dirs; keep splitting the largest bucket while the map fits.
    best = dict(bucket(""))
    tried = set()
    while True:
        splittable = [k for k in best if k not in tried and k != "."]
        if not splittable:
            break
        big = max(splittable, key=lambda k: best[k][0])
        tried.add(big)
        children = bucket(big)
        if len(children) < 2:
            continue
        if len(best) - 1 + len(children) > MAX_MAP_ROWS:
            continue
        del best[big]
        best.update(children)
        tried.discard(big)
    return sorted((k, *v) for k, v in best.items()), len(generated), excluded


def queue_md(n: int, meta: dict, head: str, walk: list[dict], waiting: list[dict]) -> str:
    esc = lambda s: str(s).replace("|", "\\|")
    lines = [f"# Round {n} · PR #{meta['pr_number']} · head `{head[:7]}`",
             "Decision: Pending → fix | clarify | skip · Flags: ⚠️ outdated · ↩ reviewer replied", "",
             "| # | Comment ID | Author | File:Line | Title | Flags | Group | Decision |",
             "|---|---|---|---|---|---|---|---|"]
    for t in walk:
        flags = " ".join(f for f, on in (("⚠️", t["outdated"]), ("↩", t["reviewer_replied"])) if on)
        lines.append(f"| {t['n']} | {t['comment_id']} | {t['author']} | "
                     f"`{os.path.basename(t['path'])}:{t['line'] or '—'}` | {esc(t['title'])} | {flags} |  | Pending |")
    lines += ["", "## Waiting on reviewer",
              "| Comment ID | File:Line | Title | Our decision | Replied on |", "|---|---|---|---|---|"]
    for w in waiting:
        lines.append(f"| {w['comment_id']} | `{os.path.basename(w['path'])}:{w['line'] or '—'}` | "
                     f"{esc(w['title'])} | {w['decision']} | {w['replied_at'][:10]} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workspace")
    ap.add_argument("--pr", type=int, help="round 1: PR number (default: the current branch's PR)")
    ap.add_argument("--round", type=int, help="the next round number (current_round + 1)")
    ap.add_argument("--exclude", nargs="*", default=None, help="globs left out of the change map")
    args = ap.parse_args()
    ws = os.path.abspath(args.workspace)

    if os.path.exists(meta_path(ws)):
        meta = read_meta(ws)
        nxt = meta["current_round"] + 1
        if args.round != nxt:
            fail(f"round {meta['current_round']} already set up; pass --round {nxt} to start the next round")
        pending = [i["n"] for i in read_replies(ws, meta["current_round"])["items"] if not i.get("reply_id")]
        prev_threads = read_json(comments_path(ws, meta["current_round"]))["threads"]
        decided = {i["comment_id"] for i in read_replies(ws, meta["current_round"])["items"]}
        undecided = [t["n"] for t in prev_threads if t["comment_id"] not in decided]
        if pending or undecided:
            fail(f"round {meta['current_round']} is not done (undecided #{undecided}, unposted #{pending}); "
                 f"finish it first (round.py status)")
        n = nxt
        if args.exclude is not None:
            meta["excludes"] = args.exclude
    else:
        if args.round not in (None, 1):
            fail("no meta.json yet; the first round is round 1")
        pr = gh_json("pr", "view", *([str(args.pr)] if args.pr else []),
                     "--json", "number,url,title,headRefName,baseRefName")
        repo = gh_json("repo", "view", "--json", "owner,name")
        viewer = gh_json("api", "user")["login"]
        meta = {"pr_number": pr["number"], "owner": repo["owner"]["login"], "repo": repo["name"],
                "url": pr["url"], "title": pr["title"], "branch": pr["headRefName"],
                "base": pr["baseRefName"], "viewer": viewer, "current_round": 0,
                "excludes": args.exclude or []}
        n = 1

    if os.path.exists(round_dir(ws, n)):
        fail(f"{round_dir(ws, n)} already exists but meta.json does not point to it "
             f"(an interrupted setup); remove that folder and re-run")
    head = check_preconditions(meta["branch"])
    threads = fetch_threads(meta["owner"], meta["repo"], meta["pr_number"])
    sel = select(threads, earlier_decisions(ws, n), meta["viewer"])
    cmap, n_generated, n_excluded = change_map(meta["base"], meta["excludes"])

    os.makedirs(round_dir(ws, n))
    write_json(os.path.join(round_dir(ws, n), "round.json"),
               {"round": n, "headRefOid": head, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    write_json(comments_path(ws, n), {"threads": sel["walk"], "waiting": sel["waiting"]})
    with open(queue_path(ws, n), "w") as f:
        f.write(queue_md(n, meta, head, sel["walk"], sel["waiting"]))
    meta["current_round"] = n  # last, so a crash never points meta at a half-written round
    write_json(meta_path(ws), meta)

    walk = sel["walk"]
    replied = sum(t["reviewer_replied"] for t in walk)
    print(json.dumps({
        "round": n, "pr": meta["pr_number"], "head": head[:7],
        "walk": len(walk), "new": len(walk) - replied, "reviewer_replied": replied,
        "outdated": sum(t["outdated"] for t in walk), "waiting": len(sel["waiting"]),
        "own_threads_skipped": sel["own_threads"],
        "truncated_threads": sel["truncated_threads"],
        "generated_excluded": n_generated, "user_excluded": n_excluded,
    }))
    print("\nChange map (dir · files · +add/−del):")
    for d, files, a, dl in cmap:
        print(f"  {d} · {files} · +{a}/−{dl}")
    if sel["truncated_threads"]:
        print(f"\n[WARN] {sel['truncated_threads']} thread(s) have more than 100 comments; "
              f"only the first 100 were read", file=sys.stderr)


if __name__ == "__main__":
    main()
