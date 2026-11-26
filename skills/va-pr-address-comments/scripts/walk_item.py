#!/usr/bin/env python3
"""Record one approved walk decision.

Usage:
  python walk_item.py add <workspace> --rows 5            --decision fix     < reply.txt
  python walk_item.py add <workspace> --rows 1-9,14       --decision skip    < reply.txt
  python walk_item.py add <workspace> --rows 3 --round 2  --decision clarify < reply.txt

--rows    queue `#` numbers (ranges allowed); a group passes all its rows.
--decision fix | clarify | skip
stdin     the exact reply text (Markdown). The same text is posted on every row.

Validates, then writes one item per row to rounds/N/final_replies.json and
marks each row's Decision in comment_queue.md. A repeat `add` for a row
replaces its item (a re-decision); after `round.py plan-approved` the item is
marked `deviation: true` so it is flagged before commit and at posting.

Item: {n, comment_id, group, decision, reply, deviation, reply_id, url}
  group     read from the queue's Group column
  reply_id  url   written by post_replies.py

Reply rules:
  fix              contains `{sha}` (filled with the round commit at posting)
  clarify | skip   no `{sha}`
  all              no @mention outside code; no va-pr-address-comments marker
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from _constants import MARKER_PREFIX
from _utils import fail, read_json, write_json, comments_path, replies_path, queue_path, read_replies, resolve_round

DECISIONS = ("fix", "clarify", "skip")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
MENTION = re.compile(r"(?<![\w.])@[A-Za-z0-9][\w-]*")


def parse_rows(spec: str) -> list[int]:
    rows = []
    for part in spec.split(","):
        part = part.strip()
        if re.fullmatch(r"\d+-\d+", part):
            a, b = map(int, part.split("-"))
            rows += range(a, b + 1)
        elif part.isdigit():
            rows.append(int(part))
        else:
            fail(f"--rows: '{part}' is not a number or range")
    return sorted(set(rows))


def validate_reply(decision: str, reply: str) -> None:
    if not reply.strip():
        fail("reply on stdin is empty")
    has_sha = "{sha}" in reply
    if decision == "fix" and not has_sha:
        fail("a fix reply must contain {sha}")
    if decision != "fix" and has_sha:
        fail(f"a {decision} reply must not contain {{sha}}")
    if MENTION.search(CODE.sub("", reply)):
        fail("reply contains an @mention; the thread already notifies its participants")
    if MARKER_PREFIX in reply:
        fail("reply contains the marker; post_replies.py adds it")


def queue_rows(path: str) -> tuple[list[str], dict[str, int], dict[int, int]]:
    """Lines, header column index, and line index per row #."""
    with open(path) as f:
        lines = f.read().split("\n")
    cols, index = None, {}
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in CELL_SPLIT.split(line.strip())[1:-1]]
        if cols is None and "Decision" in cells and "Group" in cells:
            cols = {name: j for j, name in enumerate(cells)}
        elif cols is not None and cells and cells[0].isdigit():
            index[int(cells[0])] = i
        elif cols is not None and cells and cells[0] == "Comment ID":
            break  # the waiting table starts
    if cols is None:
        fail(f"{path} has no table with Group and Decision columns")
    return lines, cols, index


def cell(line: str, col: int) -> str:
    return CELL_SPLIT.split(line.strip())[1:-1][col].strip()


def set_cell(line: str, col: int, value: str) -> str:
    cells = CELL_SPLIT.split(line.strip())[1:-1]
    cells[col] = f" {value} "
    return "|" + "|".join(cells) + "|"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["add"])
    ap.add_argument("workspace")
    ap.add_argument("--rows", required=True)
    ap.add_argument("--decision", required=True, choices=DECISIONS)
    ap.add_argument("--round", type=int)
    args = ap.parse_args()

    n = resolve_round(args.workspace, args.round)
    reply = sys.stdin.read().strip()
    validate_reply(args.decision, reply)

    threads = {t["n"]: t for t in read_json(comments_path(args.workspace, n))["threads"]}
    rows = parse_rows(args.rows)
    missing = [r for r in rows if r not in threads]
    if missing:
        fail(f"rows {missing} are not in round {n}'s comments.json")

    data = read_replies(args.workspace, n)
    by_n = {i["n"]: i for i in data["items"]}
    posted = [r for r in rows if by_n.get(r, {}).get("reply_id")]
    if posted:
        fail(f"rows {posted} are already posted; a posted reply is not replaced")

    qpath = queue_path(args.workspace, n)
    lines, cols, index = queue_rows(qpath)
    for r in rows:
        group = cell(lines[index[r]], cols["Group"]) if r in index else ""
        item = {"n": r, "comment_id": threads[r]["comment_id"], "group": group or None,
                "decision": args.decision, "reply": reply, "deviation": bool(data["plan_approved"]),
                "reply_id": None, "url": None}
        verb = "Replaced" if r in by_n else "Added"
        by_n[r] = item
        if r in index:
            lines[index[r]] = set_cell(lines[index[r]], cols["Decision"], args.decision)
    data["items"] = [by_n[k] for k in sorted(by_n)]
    write_json(replies_path(args.workspace, n), data)
    with open(qpath, "w") as f:
        f.write("\n".join(lines))

    pending = len(threads) - len(by_n)
    flag = " · deviation" if data["plan_approved"] else ""
    print(f"{verb} #{args.rows} {args.decision}{flag} · {len(by_n)}/{len(threads)} decided · {pending} pending")


if __name__ == "__main__":
    main()
