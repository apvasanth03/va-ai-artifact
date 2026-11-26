"""Workspace, gh and git helpers shared by the va-pr-address-comments scripts.

# Adapted from va-pr-review-collab/scripts/_utils.py (meta/round I/O, gh, git,
# reply_to_comment, generated-file filtering).
"""
import fnmatch, json, os, subprocess, sys

from _constants import GENERATED_SUFFIXES, GENERATED_BASENAMES, GENERATED_GLOBS


def fail(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


# ── JSON files ───────────────────────────────────────────────────────────────

def read_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def write_json(path: str, data) -> None:
    """Atomic write, so an interrupted script never leaves half a file."""
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


# ── Workspace layout ─────────────────────────────────────────────────────────

def meta_path(ws: str) -> str:
    return os.path.join(ws, "meta.json")


def read_meta(ws: str) -> dict:
    if not os.path.exists(meta_path(ws)):
        fail(f"{meta_path(ws)} not found — run setup.py first")
    return read_json(meta_path(ws))


def round_dir(ws: str, n: int) -> str:
    return os.path.join(ws, "rounds", str(n))


def resolve_round(ws: str, requested: int | None) -> int:
    return requested if requested is not None else read_meta(ws)["current_round"]


def comments_path(ws: str, n: int) -> str:
    return os.path.join(round_dir(ws, n), "comments.json")


def replies_path(ws: str, n: int) -> str:
    return os.path.join(round_dir(ws, n), "final_replies.json")


def queue_path(ws: str, n: int) -> str:
    return os.path.join(round_dir(ws, n), "comment_queue.md")


EMPTY_REPLIES = {"plan_approved": False, "commit_sha": None, "items": []}


def read_replies(ws: str, n: int) -> dict:
    p = replies_path(ws, n)
    return {**EMPTY_REPLIES, **read_json(p)} if os.path.exists(p) else json.loads(json.dumps(EMPTY_REPLIES))


# ── gh / git ─────────────────────────────────────────────────────────────────

TLS_HINT = ("If this is a TLS/x509 error inside the tool sandbox, re-run the "
            "command with the sandbox disabled.")


def run(cmd: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True)


def gh_json(*args) -> dict | list:
    r = run(["gh", *args])
    if r.returncode != 0:
        fail(f"gh {' '.join(args[:2])} failed: {r.stderr.strip()}\n{TLS_HINT}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def gh_graphql(query: str, **variables) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        if v is None:
            continue
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    r = run(args)
    if r.returncode != 0:
        fail(f"gh api graphql failed: {r.stderr.strip()}\n{TLS_HINT}")
    resp = json.loads(r.stdout)
    if "errors" in resp:
        fail(f"GraphQL errors: {json.dumps(resp['errors'])}")
    return resp["data"]


def git(*args) -> subprocess.CompletedProcess:
    return run(["git", *args])


def git_out(*args) -> str:
    r = git(*args)
    if r.returncode != 0:
        fail(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def git_fetch(*refs: str) -> None:
    r = git("fetch", "--quiet", "origin", *refs)
    if r.returncode != 0:
        fail(f"git fetch origin {' '.join(refs)} failed: {r.stderr.strip()}\n{TLS_HINT}")


def reply_to_comment(owner: str, repo: str, pr: int, comment_id: int, body: str) -> dict:
    """POST a reply on a review thread (root comment id). Raises RuntimeError on failure."""
    r = run(["gh", "api", f"repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies",
             "--method", "POST", "-f", f"body={body}"])
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    resp = json.loads(r.stdout)
    return {"reply_id": resp["id"], "url": resp["html_url"]}


def list_pr_comments(owner: str, repo: str, pr: int) -> list[dict]:
    """All review comments on the PR (REST, paginated)."""
    pages = gh_json("api", "--paginate", "--slurp", f"repos/{owner}/{repo}/pulls/{pr}/comments?per_page=100")
    return [c for page in pages for c in (page if isinstance(page, list) else [page])]


# ── Generated-file filtering ─────────────────────────────────────────────────

def detect_generated(files: list[str]) -> set[str]:
    """Files marked linguist-generated in .gitattributes, or matching the known patterns."""
    generated = set()
    if files:
        r = run(["git", "check-attr", "-z", "linguist-generated", "--stdin"], stdin="\0".join(files))
        fields = r.stdout.split("\0")
        for i in range(0, len(fields) - 2, 3):
            if fields[i + 2].strip() in ("set", "true"):
                generated.add(fields[i])
    for path in files:
        if path in generated:
            continue
        if (os.path.basename(path) in GENERATED_BASENAMES or path.endswith(GENERATED_SUFFIXES)
                or any(fnmatch.fnmatch(path, g) for g in GENERATED_GLOBS)):
            generated.add(path)
    return generated
