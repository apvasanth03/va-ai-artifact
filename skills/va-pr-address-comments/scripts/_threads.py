"""Fetch, clean and select review threads. Pure functions apart from `fetch_threads`."""
import re

from _constants import MARKER_PREFIX, STRIP_DETAILS_SUMMARIES
from _utils import gh_graphql

THREADS_QUERY = """
query($owner: String!, $repo: String!, $pr: Int!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved isOutdated path line originalLine
          comments(first: 100) {
            pageInfo { hasNextPage }
            nodes { databaseId body createdAt url author { login __typename } }
          }
        }
      }
    }
  }
}
"""


def fetch_threads(owner: str, repo: str, pr: int) -> list[dict]:
    threads, cursor = [], None
    while True:
        data = gh_graphql(THREADS_QUERY, owner=owner, repo=repo, pr=pr, cursor=cursor)
        rt = data["repository"]["pullRequest"]["reviewThreads"]
        threads.extend(rt["nodes"])
        if not rt["pageInfo"]["hasNextPage"]:
            return threads
        cursor = rt["pageInfo"]["endCursor"]


# ── Cleaning ─────────────────────────────────────────────────────────────────

_DETAILS_TAG = re.compile(r"<details>|</details>", re.I)
_SUMMARY = re.compile(r"^\s*<summary>(.*?)</summary>", re.I | re.S)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_DROP_TAGS = re.compile(r"<picture>.*?</picture>[ \t]*|<img[^>]*>[ \t]*|<sub>.*?</sub>|</?dl>|</?dd>|<br\s*/?>", re.I | re.S)
_TAG = re.compile(r"<[^>]+>")


def _plain(html: str) -> str:
    return " ".join(_TAG.sub("", html).split())


def _strip_details(text: str) -> str:
    """Drop <details> blocks whose summary is bot noise; unwrap the rest (nesting-aware)."""
    out, pos = [], 0
    while True:
        m = re.search(r"<details>", text[pos:], re.I)
        if not m:
            out.append(text[pos:])
            return "".join(out)
        start = pos + m.start()
        out.append(text[pos:start])
        depth, i, end = 0, start, None
        for t in _DETAILS_TAG.finditer(text, start):
            depth += 1 if t.group().lower() == "<details>" else -1
            if depth == 0:
                end, i = t.start(), t.end()
                break
        if end is None:  # unbalanced: keep the rest as is
            out.append(text[start:])
            return "".join(out)
        inner = text[start + len("<details>"):end]
        sm = _SUMMARY.match(inner)
        summary = _plain(sm.group(1)) if sm else ""
        if not any(s in summary.lower() for s in STRIP_DETAILS_SUMMARIES):
            body = inner[sm.end():] if sm else inner
            out.append((f"**{summary}**\n" if summary else "") + _strip_details(body))
        pos = i


def clean_body(raw: str) -> str:
    text = _HTML_COMMENT.sub("", raw or "")
    text = _strip_details(text)
    text = _DROP_TAGS.sub("", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


_SEVERITY = re.compile(r"</picture>\s*(Critical|Major|Minor|Trivial|Nitpick)\s*\*\*", re.I)
_TITLE_LINE = re.compile(r"^\*\*([^*]+?)\*\*\s*$", re.M)


def parse_severity(raw: str) -> str | None:
    m = _SEVERITY.search(raw or "")
    return m.group(1).capitalize() if m else None


def parse_title(cleaned: str, limit: int = 80) -> str:
    m = _TITLE_LINE.search(cleaned)
    if m:
        title = m.group(1).strip()
    else:
        first = next((l.strip() for l in cleaned.splitlines() if l.strip()), "")
        title = re.split(r"(?<=[.!?])\s", first, maxsplit=1)[0]
    title = title.rstrip(".")
    return title if len(title) <= limit else title[: limit - 1].rstrip() + "…"


# ── Selection ────────────────────────────────────────────────────────────────

def is_ours(comment: dict, viewer: str) -> bool:
    return MARKER_PREFIX in (comment.get("body") or "") or (comment.get("author") or {}).get("login") == viewer


def _author(c: dict) -> str:
    return (c.get("author") or {}).get("login") or "ghost"


def select(threads: list[dict], earlier: dict[int, dict], viewer: str) -> dict:
    """Split unresolved threads into walk / waiting.

    walk    — no earlier decision, or a non-ours comment after our last reply.
    waiting — an earlier decision and nothing after our last reply.
    Threads whose root comment is ours are not review comments; they are counted only.
    """
    walk, waiting, own, truncated = [], [], 0, 0
    for t in threads:
        if t["isResolved"]:
            continue
        comments = t["comments"]["nodes"]
        if not comments:
            continue
        truncated += t["comments"]["pageInfo"]["hasNextPage"]
        root, replies = comments[0], comments[1:]
        if is_ours(root, viewer):
            own += 1
            continue
        cid = root["databaseId"]
        cleaned = clean_body(root["body"])
        ours_idx = [i for i, c in enumerate(replies) if is_ours(c, viewer)]
        last_ours = ours_idx[-1] if ours_idx else None
        prior = earlier.get(cid)
        after_ours = last_ours is not None and any(
            not is_ours(c, viewer) for c in replies[last_ours + 1:])
        if prior and last_ours is not None and not after_ours:
            waiting.append({
                "comment_id": cid, "path": t["path"], "line": t["line"] or t["originalLine"],
                "title": parse_title(cleaned), "decision": prior["decision"],
                "replied_at": replies[last_ours]["createdAt"],
            })
            continue
        walk.append({
            "comment_id": cid, "url": root["url"],
            "author": _author(root),
            "is_bot": (root.get("author") or {}).get("__typename") == "Bot" or _author(root).endswith("[bot]"),
            "path": t["path"], "line": t["line"] or t["originalLine"], "outdated": t["isOutdated"],
            "severity": parse_severity(root["body"]), "title": parse_title(cleaned), "body": cleaned,
            "replies": [{"author": _author(c), "ours": is_ours(c, viewer),
                         "body": clean_body(c["body"]), "at": c["createdAt"]} for c in replies],
            "earlier": prior,
            "reviewer_replied": bool(prior) and after_ours,
        })
    walk.sort(key=lambda w: (w["path"], w["line"] or 0))
    for n, w in enumerate(walk, 1):
        w["n"] = n
    return {"walk": walk, "waiting": waiting, "own_threads": own, "truncated_threads": truncated}
