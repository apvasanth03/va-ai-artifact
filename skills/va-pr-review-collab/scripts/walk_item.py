#!/usr/bin/env python3
"""Record reviewer decisions from the reconcile step.

`add` validates approved items, saves them into the round's final_review.json
(creating the file when missing) and marks their rows in review_queue.md.
`discard` marks rows only; nothing reaches final_review.json.

Usage:
  python walk_item.py add <workspace> --section new [--edited [ROWS]] [--round R]  < items.json
  python walk_item.py add <workspace> --section new --row N [--edited] [--round R]  < item.json
  python walk_item.py add <workspace> --section unresolved|resolved [--round R]    < item.json
  python walk_item.py edit <workspace> --row N (--set FIELD=VALUE ... | --field FIELD) [--round R]
  python walk_item.py discard <workspace> --row N | --rows 4,5 --reason "<few words>" [--round R]

`add` reads JSON on stdin using the SKILL.md item fields: one item with --row
(or for unresolved/resolved), or one object keyed by queue row number
({"1": {...}, "3": {...}}). Every item is validated before anything is written,
and each `new` item records its queue row as `row`. --edited marks every added
row Edited, or only the listed rows (--edited 3,5); the rest are Approved.
`edit` changes fields of a `new` item already in final_review.json, found by
row: --set for short values (repeatable; line takes an integer or null),
--field to read one field's new text from stdin. The row is marked Edited.
`new` items take no comment_id or url; post_all.py writes those back.
A repeat `add` replaces the earlier item: `new` matches on row (or file + title),
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
        if a.get("row") is not None and b.get("row") is not None:
            return a["row"] == b["row"]
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
        rows += csv_rows(args.rows, "--rows")
    if len(set(rows)) != len(rows):
        fail("a row number is listed twice")
    return rows


def csv_rows(text: str, flag: str) -> list[int]:
    try:
        return [int(r) for r in text.split(",") if r.strip()]
    except ValueError:
        fail(f"{flag} takes row numbers separated by commas, e.g. 1,2,3")


def read_stdin_json(what: str):
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        fail(f"{what} on stdin is invalid JSON: {e}")


def load_review(json_path: str) -> dict:
    data = dict(EMPTY_REVIEW)
    if os.path.exists(json_path):
        with open(json_path) as f:
            data = {**EMPTY_REVIEW, **json.load(f)}
    return data


def edit_item(args, json_path: str, queue_path: str, patch_path: str) -> None:
    if args.row is None:
        fail("edit needs --row")
    if not args.set and not args.field:
        fail("edit needs --set FIELD=VALUE or --field FIELD")
    data = load_review(json_path)
    matches = [e for e in data["new"] if e.get("row") == args.row]
    if not matches:
        fail(f"no new item for row {args.row} in {json_path}")
    if "comment_id" in matches[0]:
        fail(f"row {args.row} is already posted ({matches[0].get('url', 'comment ' + str(matches[0]['comment_id']))}); "
             "edit the comment on GitHub instead")
    item = dict(matches[0])
    editable = set(SECTIONS["new"]["required"])
    changes = {}
    for pair in args.set or []:
        key, sep, value = pair.partition("=")
        if not sep:
            fail(f"--set takes FIELD=VALUE, got {pair!r}")
        changes[key] = value
    if args.field:
        changes[args.field] = sys.stdin.read().strip()
    for key, value in changes.items():
        if key not in editable:
            fail(f"{key} is not editable; fields: {', '.join(sorted(editable))}")
        if key == "line":
            if value in ("null", "None", ""):
                value = None
            else:
                try:
                    value = int(value)
                except ValueError:
                    fail("line takes an integer or null")
        item[key] = value
    validate("new", item, patch_path)
    data["new"][data["new"].index(matches[0])] = item
    save_json(json_path, data)
    if os.path.exists(queue_path) and row_decision(queue_path, args.row) is not None:
        mark_row(queue_path, args.row, "Edited", "")
    print(f"Edited row {args.row} ({', '.join(changes)}) — {item['title']}")


def upsert(data: dict, section: str, item: dict) -> str:
    items = data[section]
    for i, existing in enumerate(items):
        if same_item(section, existing, item):
            if section == "new" and "comment_id" in existing:
                fail(f"'{existing['title']}' is already posted; edit the comment on GitHub instead")
            items[i] = item
            return "Replaced"
    items.append(item)
    return "Added"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["add", "edit", "discard"])
    ap.add_argument("workspace")
    ap.add_argument("--section", choices=list(SECTIONS))
    ap.add_argument("--row", type=int, help="row # in review_queue.md")
    ap.add_argument("--rows", help="discard: several row #s, comma-separated (4,5)")
    ap.add_argument("--edited", nargs="?", const="all", default=None,
                    help="add: mark rows Edited instead of Approved; all added rows, or the listed ones (3,5)")
    ap.add_argument("--set", action="append", metavar="FIELD=VALUE", help="edit: set a short field (repeatable)")
    ap.add_argument("--field", help="edit: replace this field with the text on stdin")
    ap.add_argument("--reason", default="", help="discard: a few words on why")
    ap.add_argument("--round", type=int, help="defaults to the workspace's current round")
    args = ap.parse_args()

    round_num = args.round if args.round is not None else current_round(args.workspace)
    rdir = round_dir(args.workspace, round_num)
    rev_dir = os.path.join(rdir, "review")
    json_path = os.path.join(rev_dir, "final_review.json")
    queue_path = os.path.join(rev_dir, "review_queue.md")
    patch_path = os.path.join(rdir, "diff.patch")

    if args.action == "edit":
        edit_item(args, json_path, queue_path, patch_path)
        return

    if args.action == "discard":
        rows = parse_rows(args)
        if not rows:
            fail("discard needs --row or --rows")
        check_rows(queue_path, rows, discarding=True)
        for row in rows:
            mark_row(queue_path, row, "Discarded", args.reason)
        print(f"Rows {', '.join(map(str, rows))} marked Discarded")
        return

    if not args.section:
        fail("add needs --section")
    if args.rows:
        fail("add takes --row for one item, or items keyed by row on stdin")
    payload = read_stdin_json("item JSON")
    if not isinstance(payload, dict):
        fail("stdin must be one JSON object")
    if args.section != "new":
        if args.row is not None:
            fail(f"{args.section} items have no queue row")
        pairs = [(None, payload)]
    elif args.row is not None:
        pairs = [(args.row, payload)]
    else:
        try:
            pairs = [(int(k), v) for k, v in payload.items()]
        except ValueError:
            fail("without --row, stdin must be an object keyed by row number")
        if not pairs:
            fail("no items on stdin")

    rows = [r for r, _ in pairs if r is not None]
    if rows:
        check_rows(queue_path, rows, discarding=False)
    for row, item in pairs:
        if not isinstance(item, dict):
            fail(f"item for row {row} must be one JSON object")
        if row is not None:
            item["row"] = row
        validate(args.section, item, patch_path)

    edited = set(rows) if args.edited == "all" else set(csv_rows(args.edited, "--edited") if args.edited else [])
    if not edited <= set(rows):
        fail("--edited names a row that is not being added")

    data = load_review(json_path)
    verbs = [upsert(data, args.section, item) for _, item in pairs]
    save_json(json_path, data)

    for row in rows:
        mark_row(queue_path, row, "Edited" if row in edited else "Approved", "")
    for verb, (_, item) in zip(verbs, pairs):
        print(f"{verb} in {args.section} — {item['title']}")
    print(f"(new={len(data['new'])}, unresolved={len(data['unresolved'])}, resolved={len(data['resolved'])})")


def check_rows(queue_path: str, rows: list[int], discarding: bool) -> None:
    if not os.path.exists(queue_path):
        fail(f"{queue_path} does not exist")
    if len(set(rows)) != len(rows):
        fail("a row number is listed twice")
    for row in rows:
        decision = row_decision(queue_path, row)
        if decision is None:
            fail(f"row {row} not found in {queue_path}")
        if discarding and decision in ("Approved", "Edited"):
            fail(f"row {row} is {decision} and its item is already in final_review.json; "
                 "remove that item from the file first, then discard")


if __name__ == "__main__":
    main()
