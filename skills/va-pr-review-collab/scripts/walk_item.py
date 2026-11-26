#!/usr/bin/env python3
"""Record reviewer decisions from the reconcile step.

`add` validates approved items, saves them into the round's final_review.json
(creating the file when missing) and marks their rows in review_queue.md.
`discard` marks rows only; nothing reaches final_review.json.

Usage:
  python walk_item.py add <workspace> --section new|unresolved|resolved
                          [--row N] [--edited] [--round R]  < item.json
  python walk_item.py add <workspace> --section new --rows 1,2,3 --from-queue [--round R]
  python walk_item.py discard <workspace> --row N | --rows 4,5 --reason "<few words>" [--round R]

Without --from-queue, the item JSON arrives on stdin: one object using the
SKILL.md item fields. With --from-queue, each row's item is read from
review/queue_items.json (keyed by row number); every item is validated before
anything is written.
`new` items take no comment_id or url; post_all.py writes those back.
A repeat `add` replaces the earlier item: `new` matches on file + title,
`unresolved` and `resolved` match on comment_id.
"""
import argparse, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from _utils import current_round, round_dir
from diff_lines import plus_ranges

SECTIONS = {
    "new": {"required": ["title", "severity", "file", "line", "issue", "why", "suggestion"],
            "forbidden": ["comment_id", "url"]},
    "unresolved": {"required": ["title", "comment_id", "status", "evidence"],
                   "statuses": ["Not Fixed", "Partially Fixed"]},
    "resolved": {"required": ["title", "comment_id", "status", "evidence"],
                 "statuses": ["Fixed", "Moot"]},
}
SEVERITIES = ["critical", "major", "minor"]
EMPTY_REVIEW = {"new": [], "unresolved": [], "resolved": []}
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def fail(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def validate(section: str, item: dict, patch_path: str) -> None:
    spec = SECTIONS[section]
    missing = [k for k in spec["required"] if k not in item]
    if missing:
        fail(f"{section} item is missing: {', '.join(missing)}")
    present = [k for k in spec.get("forbidden", []) if k in item]
    if present:
        fail(f"{', '.join(present)} is written by post_all.py, not by hand")
    if "statuses" in spec and item["status"] not in spec["statuses"]:
        fail(f"status for {section} must be one of {spec['statuses']}")
    if section != "new":
        if not isinstance(item["comment_id"], int):
            fail("comment_id must be an integer")
        return
    if item["severity"] not in SEVERITIES:
        fail(f"severity must be one of {SEVERITIES}")
    line = item["line"]
    if line is None:
        return
    if not isinstance(line, int):
        fail("line must be an integer or null")
    with open(patch_path) as f:
        ranges = plus_ranges(f.read(), item["file"])
    if not any(start <= line <= end for start, end in ranges):
        shown = ", ".join(f"{s}-{e}" for s, e in ranges) or "no hunks"
        fail(f"line {line} is not a +side line of {item['file']} (hunks: {shown})")


def save_json(path: str, data: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def same_item(section: str, a: dict, b: dict) -> bool:
    if section == "new":
        return (a.get("file"), a.get("title")) == (b.get("file"), b.get("title"))
    return a.get("comment_id") == b.get("comment_id")


def read_queue(queue_path: str) -> tuple[list[str], dict[str, int]]:
    """Return the queue's lines and the column index of each header name."""
    with open(queue_path) as f:
        lines = f.read().split("\n")
    for line in lines:
        if line.startswith("|"):
            names = [c.strip() for c in CELL_SPLIT.split(line.strip())[1:-1]]
            if "Decision" in names and "Note" in names:
                return lines, {n: i for i, n in enumerate(names)}
    fail(f"{queue_path} has no table with Decision and Note columns")


def find_row(lines: list[str], row: int) -> int | None:
    for i, line in enumerate(lines):
        cells = CELL_SPLIT.split(line.strip())[1:-1]
        if line.startswith("|") and cells and cells[0].strip() == str(row):
            return i
    return None


def row_decision(queue_path: str, row: int) -> str | None:
    lines, cols = read_queue(queue_path)
    i = find_row(lines, row)
    if i is None:
        return None
    return CELL_SPLIT.split(lines[i].strip())[1:-1][cols["Decision"]].strip()


def mark_row(queue_path: str, row: int, decision: str, note: str) -> None:
    lines, cols = read_queue(queue_path)
    i = find_row(lines, row)
    if i is None:
        fail(f"row {row} not found in {queue_path}")
    cells = CELL_SPLIT.split(lines[i].strip())[1:-1]
    cells[cols["Decision"]] = f" {decision} "
    cells[cols["Note"]] = f" {note.replace('|', chr(92) + '|')} " if note else " "
    lines[i] = "|" + "|".join(cells) + "|"
    with open(queue_path, "w") as f:
        f.write("\n".join(lines))


def parse_rows(args) -> list[int]:
    rows = [args.row] if args.row is not None else []
    if args.rows:
        try:
            rows += [int(r) for r in args.rows.split(",") if r.strip()]
        except ValueError:
            fail("--rows takes row numbers separated by commas, e.g. 1,2,3")
    if len(set(rows)) != len(rows):
        fail("a row number is listed twice")
    return rows


def load_queue_items(path: str) -> dict:
    if not os.path.exists(path):
        fail(f"{path} does not exist")
    with open(path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            fail(f"{path} is invalid JSON: {e}")
    if not isinstance(data, dict):
        fail(f"{path} must be one object keyed by row number")
    return data


def upsert(data: dict, section: str, item: dict) -> str:
    items = data[section]
    for i, existing in enumerate(items):
        if same_item(section, existing, item):
            items[i] = item
            return "Replaced"
    items.append(item)
    return "Added"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["add", "discard"])
    ap.add_argument("workspace")
    ap.add_argument("--section", choices=list(SECTIONS))
    ap.add_argument("--row", type=int, help="row # in review_queue.md")
    ap.add_argument("--rows", help="several row #s, comma-separated (1,2,3)")
    ap.add_argument("--from-queue", action="store_true",
                    help="add: read each row's item from review/queue_items.json instead of stdin")
    ap.add_argument("--edited", action="store_true", help="mark the rows Edited instead of Approved")
    ap.add_argument("--reason", default="", help="discard: a few words on why")
    ap.add_argument("--round", type=int, help="defaults to the workspace's current round")
    args = ap.parse_args()

    round_num = args.round if args.round is not None else current_round(args.workspace)
    rdir = round_dir(args.workspace, round_num)
    rev_dir = os.path.join(rdir, "review")
    json_path = os.path.join(rev_dir, "final_review.json")
    queue_path = os.path.join(rev_dir, "review_queue.md")
    queue_items_path = os.path.join(rev_dir, "queue_items.json")

    rows = parse_rows(args)
    if rows:
        if not os.path.exists(queue_path):
            fail(f"{queue_path} does not exist")
        for row in rows:
            decision = row_decision(queue_path, row)
            if decision is None:
                fail(f"row {row} not found in {queue_path}")
            if args.action == "discard" and decision in ("Approved", "Edited"):
                fail(f"row {row} is {decision} and its item is already in final_review.json; "
                     "remove that item from the file first, then discard")

    if args.action == "discard":
        if not rows:
            fail("discard needs --row or --rows")
        for row in rows:
            mark_row(queue_path, row, "Discarded", args.reason)
        print(f"Rows {', '.join(map(str, rows))} marked Discarded")
        return

    if not args.section:
        fail("add needs --section")
    if args.from_queue:
        if not rows:
            fail("--from-queue needs --row or --rows")
        queued = load_queue_items(queue_items_path)
        missing = [r for r in rows if str(r) not in queued]
        if missing:
            fail(f"no item in {queue_items_path} for row(s) {', '.join(map(str, missing))}")
        new_items = [queued[str(r)] for r in rows]
    else:
        if len(rows) > 1:
            fail("several rows need --from-queue; stdin carries one item")
        try:
            new_items = [json.load(sys.stdin)]
        except json.JSONDecodeError as e:
            fail(f"item JSON on stdin is invalid: {e}")
    for item in new_items:
        if not isinstance(item, dict):
            fail("each item must be one JSON object")
        validate(args.section, item, os.path.join(rdir, "diff.patch"))

    data = dict(EMPTY_REVIEW)
    if os.path.exists(json_path):
        with open(json_path) as f:
            data = {**EMPTY_REVIEW, **json.load(f)}
    verbs = [upsert(data, args.section, item) for item in new_items]
    save_json(json_path, data)

    for row in rows:
        mark_row(queue_path, row, "Edited" if args.edited else "Approved", "")
    for verb, item in zip(verbs, new_items):
        print(f"{verb} in {args.section} — {item['title']}")
    print(f"(new={len(data['new'])}, unresolved={len(data['unresolved'])}, resolved={len(data['resolved'])})")


if __name__ == "__main__":
    main()
