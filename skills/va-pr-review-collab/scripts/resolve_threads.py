#!/usr/bin/env python3
"""Reply to / resolve GitHub review threads for a re-review round from final_review.json.

Usage:
  python resolve_threads.py <workspace_path> [--round N] [--dry-run] [--force]

Reads round N's final_review.json:
  - "resolved":   Fixed / Moot            -> reply (if any) + resolve the thread
  - "unresolved": Not Fixed / Partially Fixed -> reply explaining why not fixed, leave thread open

Never acts on a thread that already has a reply from someone other than the
identity running this script — those are printed as [FLAGGED] for the reviewer
to handle by hand, not auto-resolved. Overridable with --force.

Prints one line per item and a JSON summary at the end. Exits non-zero if any
item failed or was ambiguous (comment ID not found in the current thread list).
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import read_meta, round_dir, current_round, gh, gh_graphql, reply_to_comment

REVIEW_THREADS_QUERY = """
query($owner: String!, $repo: String!, $pr: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      author { login }
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          comments(first: 50) {
            pageInfo { hasNextPage }
            nodes { databaseId body author { login } }
          }
        }
      }
    }
  }
}
"""


def fetch_review_threads(owner: str, repo: str, pr_number: int) -> tuple[list[dict], str | None]:
    threads, cursor, pr_author = [], None, None
    while True:
        data = gh_graphql(REVIEW_THREADS_QUERY, owner=owner, repo=repo, pr=pr_number,
                           **({"cursor": cursor} if cursor else {}))
        pr = data["repository"]["pullRequest"]
        if pr_author is None and pr.get("author"):
            pr_author = pr["author"]["login"]
        rt = pr["reviewThreads"]
        threads.extend(rt["nodes"])
        if not rt["pageInfo"]["hasNextPage"]:
            break
        cursor = rt["pageInfo"]["endCursor"]
    return threads, pr_author


def index_by_comment_id(threads: list[dict]) -> dict[int, dict]:
    """Maps each comment's databaseId to its thread + the thread's other comments.

    `comments_truncated` is set when a thread has more than the 50 replies
    fetched — undercounting replies here would mean a late third-party reply
    could slip past the [FLAGGED] check and get auto-resolved."""
    index = {}
    for t in threads:
        comments = t["comments"]["nodes"]
        truncated = t["comments"]["pageInfo"]["hasNextPage"]
        for c in comments:
            if c["databaseId"] is not None:
                index[c["databaseId"]] = {"thread_id": t["id"], "isResolved": t["isResolved"],
                                           "comments": comments, "comments_truncated": truncated}
    return index


RESOLVE_MUTATION = """
mutation($threadId: ID!) {
  resolveReviewThread(input: { threadId: $threadId }) { thread { id isResolved } }
}
"""


def resolve_thread(thread_id: str) -> None:
    gh_graphql(RESOLVE_MUTATION, threadId=thread_id)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace")
    ap.add_argument("--round", type=int, help="defaults to the workspace's current round")
    ap.add_argument("--dry-run", action="store_true", help="parse + print, don't reply/resolve")
    ap.add_argument("--force", action="store_true", help="resolve even if thread has third-party replies")
    args = ap.parse_args()

    round_num = args.round if args.round is not None else current_round(args.workspace)
    if round_num == 1:
        print("Round 1 has no previous round to resolve threads against.", file=sys.stderr)
        sys.exit(1)

    rev_dir = os.path.join(round_dir(args.workspace, round_num), "review")
    json_path = os.path.join(rev_dir, "final_review.json")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(json_path) as f:
        review_data = json.load(f)

    items = []
    # 1. Resolved items (Fixed / Moot): will reply (if reply given) and resolve thread
    for r in review_data.get("resolved", []):
        cid = r.get("comment_id")
        if cid is not None:
            try:
                cid = int(cid)
            except (ValueError, TypeError):
                cid = None
        items.append({
            "title": r.get("title", ""),
            "verdict": r.get("status", "Fixed"),
            "comment_id": cid,
            "evidence": r.get("evidence", ""),
            "reply": r.get("reply"),
            "source": "resolved",
            "raw_item": r,
        })

    # 2. Unresolved items (Not Fixed / Partially Fixed):
    # will reply with why it is not resolved, but will leave the thread open!
    unresolved_list = review_data.get("unresolved", [])
    if not unresolved_list and "open" in review_data:
        unresolved_list = [o for o in review_data.get("open", []) if o.get("comment_id")]
    for u in unresolved_list:
        cid = u.get("comment_id")
        if cid is None:
            continue
        try:
            cid = int(cid)
        except (ValueError, TypeError):
            continue
        verdict = u.get("status") or "Not Fixed"
        reply_text = u.get("reply") or u.get("evidence") or u.get("comment")
        items.append({
            "title": u.get("title", ""),
            "verdict": verdict,
            "comment_id": cid,
            "evidence": u.get("evidence", ""),
            "reply": reply_text,
            "source": "unresolved",
            "raw_item": u,
        })

    meta = read_meta(args.workspace)
    owner, repo, pr_number = meta["owner"], meta["repo"], meta["pr_number"]

    me = gh("api", "user")["login"]

    # Fetch live thread state even on --dry-run
    threads, pr_author = fetch_review_threads(owner, repo, pr_number)
    by_comment_id = index_by_comment_id(threads)

    results, failed = [], False

    for it in items:
        tag = it["title"][:70]

        if it["comment_id"] is None:
            print(f"[SKIP] no Comment ID recorded — {tag}", file=sys.stderr)
            failed = True
            continue

        entry = by_comment_id.get(it["comment_id"])
        if entry is None:
            print(f"[AMBIGUOUS] comment {it['comment_id']} not found in current review "
                  f"threads (deleted/minimized upstream?) — {tag}", file=sys.stderr)
            failed = True
            continue

        comments = entry["comments"]
        initial_comment = comments[0] if comments else None

        # Verify thread was initiated by me (our review comment)
        if initial_comment and initial_comment["author"] and initial_comment["author"]["login"] not in (me, None) and not args.force:
            print(f"[FLAGGED] thread for comment {it['comment_id']} was started by "
                  f"{initial_comment['author']['login']} (not {me}) — handle by hand, not auto-resolving — {tag}")
            continue

        # Check subsequent replies: PR author and our own replies are expected.
        # Only unexpected third parties (other reviewers) are flagged.
        unexpected_third_party = [
            c for c in comments[1:]
            if c["author"] and c["author"]["login"] not in (me, pr_author, None)
        ]
        if unexpected_third_party and not entry["isResolved"] and not args.force:
            print(f"[FLAGGED] thread for comment {it['comment_id']} has a reply from third party "
                  f"{unexpected_third_party[0]['author']['login']} — handle by hand, not auto-resolving — {tag}")
            continue

        if entry["comments_truncated"] and not entry["isResolved"] and not args.force:
            print(f"[FLAGGED] thread for comment {it['comment_id']} has more than 50 replies — "
                  f"can't confirm there's no third-party reply beyond what was fetched, "
                  f"handle by hand — {tag}")
            continue

        # Compute what will actually happen
        if it["verdict"] in ("Fixed", "Moot") and entry["isResolved"]:
            will_reply = False
            will_resolve = False
        else:
            will_reply = bool(it["reply"])
            if will_reply:
                already_replied = any(
                    c["author"] and c["author"]["login"] == me and c["body"].strip() == it["reply"].strip()
                    for c in comments
                )
                if already_replied:
                    will_reply = False
            will_resolve = it["verdict"] in ("Fixed", "Moot") and not entry["isResolved"]

        action = ("replied+resolved" if will_reply and will_resolve else
                  "replied (left open)" if will_reply and not will_resolve else
                  "resolved" if will_resolve else
                  "no-op")

        if args.dry_run:
            print(f"[dry-run] would {action} (comment {it['comment_id']}, {it['verdict']}) — {tag}")
            continue

        try:
            if will_reply:
                reply_to_comment(owner, repo, pr_number, it["comment_id"], it["reply"])
            if will_resolve:
                resolve_thread(entry["thread_id"])
        except RuntimeError as ex:
            print(f"[FAIL] {tag}: {ex}", file=sys.stderr)
            failed = True
            continue

        if it.get("raw_item"):
            if will_reply:
                it["raw_item"]["thread_replied"] = True
            if will_resolve:
                it["raw_item"]["thread_resolved"] = True
            if will_reply or will_resolve:
                with open(json_path, "w") as f:
                    json.dump(review_data, f, indent=2)

        print(f"[{action}] {tag}")
        results.append({"title": it["title"], "verdict": it["verdict"], "action": action})

    print("\n--- SUMMARY ---")
    print(json.dumps(results, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
