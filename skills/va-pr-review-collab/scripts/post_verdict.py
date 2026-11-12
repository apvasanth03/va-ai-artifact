#!/usr/bin/env python3
"""Draft and post the overall PR verdict (a GitHub review) after the comments are posted.

Usage:
  python post_verdict.py <workspace> --draft [--round N]
      Writes review/verdict.md (short fixed template) and prints the suggested event.
      Add --event X to draft for a verdict the reviewer chose instead of the suggestion.
      Edit the <summary> line, show the body to the reviewer, wait for approval.
  python post_verdict.py <workspace> --event APPROVE|REQUEST_CHANGES|COMMENT [--round N] [--dry-run] [--force]
      Posts review/verdict.md as one PR-level review on the round's head commit.

Idempotent: once posted, `verdict` {event, review_id, url} is recorded in
final_review.json and a second post for the same round is refused. The body lives on
GitHub; only the posting record is stored locally.
"""
import argparse, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import read_meta, read_round_meta, round_dir, current_round, check_head_current

PLACEHOLDER = "<summary>"
LABEL = {"APPROVE": "Approve", "REQUEST_CHANGES": "Request changes", "COMMENT": "Comment"}
BLOCKING = ("critical", "major")


def load_review(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def severity_by_comment(workspace: str, upto_round: int) -> dict:
    """comment_id -> severity, from every round's `new` items (unresolved items carry none)."""
    out = {}
    for n in range(1, upto_round + 1):
        p = os.path.join(round_dir(workspace, n), "review", "final_review.json")
        if os.path.exists(p):
            for it in load_review(p).get("new", []):
                if it.get("comment_id"):
                    out[it["comment_id"]] = it.get("severity", "minor")
    return out


def analyse(workspace: str, round_num: int, data: dict):
    sev = severity_by_comment(workspace, round_num)
    new = data.get("new", [])
    unresolved = [{**u, "severity": sev.get(u.get("comment_id"), "minor")} for u in data.get("unresolved", [])]
    resolved = data.get("resolved", [])
    blocking = [i for i in new + unresolved if i.get("severity") in BLOCKING]
    if blocking:
        event = "REQUEST_CHANGES"
    elif new or unresolved:
        event = "COMMENT"
    else:
        event = "APPROVE"
    return event, new, unresolved, resolved, blocking


def where(i: dict) -> str:
    return f" (`{i['file']}:{i.get('line') or '—'}`)" if i.get("file") else ""


def build_body(event: str, round_num: int, new, unresolved, resolved, blocking) -> str:
    counts = {s: sum(1 for i in new if i.get("severity") == s) for s in ("critical", "major", "minor")}
    stats = [f"{len(new)} new comment{'s' if len(new) != 1 else ''}"
             + (f" ({', '.join(f'{v} {k}' for k, v in counts.items() if v)})" if new else "")]
    if round_num > 1 or resolved or unresolved:
        stats.append(f"{len(resolved)} resolved")
        stats.append(f"{len(unresolved)} still open")
    lines = [f"**Verdict: {LABEL[event]}** · Round {round_num}", "", PLACEHOLDER, "",
             "Posted: " + " · ".join(stats)]
    if event == "REQUEST_CHANGES":
        lines += ["", "**Blocking**"] + [f"- {i['title']}{where(i)}" for i in (blocking or new + unresolved)]
    elif unresolved:
        lines += ["", "**Still open**"] + [f"- {i['title']}" for i in unresolved]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--round", type=int)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--event", choices=list(LABEL))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="post even if the PR head has moved")
    args = ap.parse_args()
    if not args.draft and not args.event:
        ap.error("pass --draft or --event")

    rn = args.round if args.round is not None else current_round(args.workspace)
    rev_dir = os.path.join(round_dir(args.workspace, rn), "review")
    json_path = os.path.join(rev_dir, "final_review.json")
    body_path = os.path.join(rev_dir, "verdict.md")
    if not os.path.exists(json_path):
        sys.exit(f"Error: {json_path} does not exist.")
    data = load_review(json_path)

    if args.draft:
        suggested, new, unresolved, resolved, blocking = analyse(args.workspace, rn, data)
        event = args.event or suggested
        with open(body_path, "w") as f:
            f.write(build_body(event, rn, new, unresolved, resolved, blocking))
        print(f"Suggested verdict: {suggested}\nDrafted for: {event}\nDraft written: {body_path}\n"
              f"Replace the {PLACEHOLDER} line with one sentence, then show it to the reviewer.")
        return

    if data.get("verdict", {}).get("review_id"):
        sys.exit(f"Verdict already posted for round {rn}: {data['verdict'].get('url')}")
    if not os.path.exists(body_path):
        sys.exit(f"Error: {body_path} missing — run with --draft first.")
    body = open(body_path).read()
    if PLACEHOLDER in body:
        sys.exit(f"Error: {body_path} still contains {PLACEHOLDER} — write the summary sentence first.")
    expected = f"**Verdict: {LABEL[args.event]}**"
    if expected not in (body.splitlines() or [""])[0]:
        sys.exit(f"Error: verdict.md header does not match --event {args.event}; re-run --draft --event {args.event}.")

    meta, rmeta = read_meta(args.workspace), read_round_meta(args.workspace, rn)
    if args.dry_run:
        print(f"[dry-run] would post {args.event} on {meta['owner']}/{meta['repo']}#{meta['pr_number']} "
              f"@ {rmeta['headRefOid'][:8]}\n---\n{body}")
        return
    if not args.force:
        warning = check_head_current(meta["owner"], meta["repo"], meta["pr_number"], rmeta["headRefOid"])
        if warning:
            sys.exit(warning)

    res = subprocess.run(
        ["gh", "api", f"repos/{meta['owner']}/{meta['repo']}/pulls/{meta['pr_number']}/reviews",
         "--method", "POST", "-f", f"event={args.event}", "-f", f"commit_id={rmeta['headRefOid']}",
         "-f", f"body={body}"], capture_output=True, text=True)
    if res.returncode != 0:
        err = res.stderr.strip()
        hint = " (GitHub does not allow approving or requesting changes on your own PR — use COMMENT.)" \
            if "own pull request" in err.lower() else ""
        sys.exit(f"[FAIL] {err}{hint}")
    resp = json.loads(res.stdout)
    data["verdict"] = {"event": args.event, "review_id": resp["id"], "url": resp["html_url"]}
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[posted] {args.event} -> {resp['html_url']}")


if __name__ == "__main__":
    main()
