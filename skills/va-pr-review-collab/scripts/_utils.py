"""Shared gh/git/diff helpers for va-pr-review-collab scripts.

No concern-file parsing lives here — the agent reads/writes the workspace's
markdown itself and calls scripts with plain values. These helpers only talk
to gh, git, meta.json, and round.json.
"""
import fnmatch, json, os, shutil, subprocess, sys


# ── Meta (stable PR identity, top-level) ─────────────────────────────────────

def read_meta(workspace: str) -> dict:
    with open(os.path.join(workspace, "meta.json")) as f:
        return json.load(f)


def write_meta(workspace: str, meta: dict) -> None:
    with open(os.path.join(workspace, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)


def meta_exists(workspace: str) -> bool:
    return os.path.exists(os.path.join(workspace, "meta.json"))


# ── Round metadata (per-round, round.json) ───────────────────────────────────

def round_dir(workspace: str, round_num: int) -> str:
    return os.path.join(workspace, "rounds", str(round_num))


def read_round_meta(workspace: str, round_num: int) -> dict:
    with open(os.path.join(round_dir(workspace, round_num), "round.json")) as f:
        return json.load(f)


def write_round_meta(workspace: str, round_num: int, round_meta: dict) -> None:
    with open(os.path.join(round_dir(workspace, round_num), "round.json"), "w") as f:
        json.dump(round_meta, f, indent=2)


def current_round(workspace: str) -> int:
    """Reads meta.json's current_round. Errors clearly if the workspace predates
    the rounds/ layout (flat diff/walkthrough/review/ with no meta.json current_round)."""
    meta = read_meta(workspace)
    if "current_round" not in meta:
        print(
            f"{workspace}/meta.json has no 'current_round' — this looks like a "
            f"pre-restructure workspace (flat diff/walkthrough/review/ layout). "
            f"This skill version only understands the rounds/<N>/ layout; migrate "
            f"manually or start a fresh workspace.",
            file=sys.stderr,
        )
        sys.exit(1)
    return meta["current_round"]


# ── gh / git ─────────────────────────────────────────────────────────────────

def gh(*args) -> dict:
    """Run a gh command, return parsed JSON. Raises on error."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"gh error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def gh_graphql(query: str, **variables) -> dict:
    """Run a gh api graphql call, return the parsed `data` object. Raises on error."""
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F" if isinstance(v, int) else "-f", f"{k}={v}"]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    resp = json.loads(result.stdout)
    if "errors" in resp:
        raise RuntimeError(json.dumps(resp["errors"]))
    return resp["data"]


def git(*args, env: dict | None = None) -> subprocess.CompletedProcess:
    full_env = {**os.environ, **env} if env else None
    return subprocess.run(["git", *args], capture_output=True, text=True, env=full_env)


def commit_reachable(oid: str) -> bool:
    """Whether `oid` still exists in the local repo — false after a force-push/
    rebase drops it from history (and it was never fetched into any other ref)."""
    r = git("cat-file", "-e", f"{oid}^{{commit}}")
    return r.returncode == 0


# ── Posting ──────────────────────────────────────────────────────────────────

def post_inline(owner: str, repo: str, pr_number: int, commit_id: str,
                 path: str, line: int, line_end: int | None, body: str) -> dict:
    """POST one inline PR review comment. Raises RuntimeError on failure."""
    args = [
        "gh", "api", f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
        "--method", "POST",
        "-f", f"body={body}", "-f", f"commit_id={commit_id}",
        "-f", f"path={path}", "-f", "side=RIGHT",
    ]
    if line_end is not None:
        args += ["-F", f"start_line={line}", "-F", f"line={line_end}", "-f", "start_side=RIGHT"]
    else:
        args += ["-F", f"line={line}"]

    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    resp = json.loads(result.stdout)
    return {"comment_id": resp["id"], "url": resp["html_url"]}


def post_file_level(owner: str, repo: str, pr_number: int, commit_id: str,
                     path: str, body: str) -> dict:
    """POST one file-level PR review comment (subject_type=file, no line) —
    for findings that can't anchor to a `+`-side diff line (e.g. deletion-only).
    Unlike a plain issue comment, this attaches to `path` in the Files Changed
    tab and forms a real, resolvable review thread — verified live against
    GitHub's API: subjectType FILE supports both replies and resolveReviewThread
    exactly like a line comment. Raises RuntimeError on failure."""
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
         "--method", "POST",
         "-f", f"body={body}", "-f", f"commit_id={commit_id}",
         "-f", f"path={path}", "-f", "subject_type=file"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    resp = json.loads(result.stdout)
    return {"comment_id": resp["id"], "url": resp["html_url"]}


def reply_to_comment(owner: str, repo: str, pr_number: int, comment_id: int, body: str) -> dict:
    """POST a reply on an existing review comment's thread. Raises RuntimeError on failure."""
    result = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies",
         "--method", "POST", "-f", f"body={body}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    resp = json.loads(result.stdout)
    return {"comment_id": resp["id"], "url": resp["html_url"]}


def fetch_author_replies(owner: str, repo: str, pr_number: int, comment_ids: list[int],
                         max_replies: int = 3, max_chars: int = 300) -> dict[int, str]:
    """Read-only. For each root comment id, return a table-cell string with the latest
    replies from anyone other than the authenticated reviewer (`gh api user`).
    Missing/failed fetch -> {} (callers leave the column empty). Never written to
    final_review.json — GitHub stays the source of truth."""
    if not comment_ids:
        return {}
    try:
        me = subprocess.run(["gh", "api", "user", "--jq", ".login"],
                            capture_output=True, text=True, check=True).stdout.strip()
        res = subprocess.run(
            ["gh", "api", "--paginate", "--slurp",
             f"repos/{owner}/{repo}/pulls/{pr_number}/comments?per_page=100"],
            capture_output=True, text=True, check=True)
        pages = json.loads(res.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as e:
        detail = getattr(e, "stderr", "") or str(e)
        print(f"[WARN] could not fetch author replies: {detail.strip()}", file=sys.stderr)
        return {}
    comments = [c for page in pages for c in (page if isinstance(page, list) else [page])]
    wanted = set(comment_ids)
    out: dict[int, str] = {}
    for cid in wanted:
        replies = [c for c in comments
                   if c.get("in_reply_to_id") == cid
                   and (c.get("user") or {}).get("login") not in (me, None)]
        replies.sort(key=lambda c: c.get("created_at", ""))
        cells = []
        for c in replies[-max_replies:]:
            body = " ".join((c.get("body") or "").split())
            if len(body) > max_chars:
                body = body[:max_chars].rstrip() + "…"
            body = body.replace("|", "\\|")
            cells.append(f"@{c['user']['login']}: {body} ([thread]({c.get('html_url', '')}))")
        if cells:
            out[cid] = "<br>".join(cells)
    return out


def check_head_current(owner: str, repo: str, pr_number: int, expected_head: str) -> str | None:
    """Returns a warning string if the PR's head has moved past `expected_head`
    since round setup ran, else None. New commits on the branch after setup mean
    inline comments would anchor to a stale commit."""
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "-R", f"{owner}/{repo}", "--json", "headRefOid"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"could not check current PR head: {result.stderr.strip()}"
    current_oid = json.loads(result.stdout)["headRefOid"]
    if current_oid == expected_head:
        return None

    # `expected_head` is captured from local `git rev-parse HEAD`, not from
    # the remote — so a mismatch isn't always "someone else pushed since
    # setup". If the remote's oid is an ancestor of the local one, the local
    # branch is simply ahead of the remote (unpushed commits); re-running
    # setup.py would just re-capture the same unpushed head and loop forever.
    local_ahead = git("merge-base", "--is-ancestor", current_oid, expected_head).returncode == 0
    if local_ahead:
        return (
            f"Local HEAD ({expected_head[:8]}) is ahead of the PR's remote head "
            f"({current_oid[:8]}) — you have local commits that haven't been "
            f"pushed. Push them first; re-running setup.py won't help, it would "
            f"just re-capture the same unpushed HEAD."
        )
    return (
        f"PR head has moved: round setup captured {expected_head[:8]}, "
        f"but the PR's current head is {current_oid[:8]}. New commits landed "
        f"since setup — inline comments would anchor to the stale commit. "
        f"Re-run setup.py for this round before posting."
    )


from _constants import (
    GENERATED_SUFFIXES,
    GENERATED_BASENAMES,
    GENERATED_GLOBS,
)

_GENERATED_SUFFIXES = GENERATED_SUFFIXES
_GENERATED_BASENAMES = GENERATED_BASENAMES
_GENERATED_GLOBS = GENERATED_GLOBS

_DIFF_BATCH_SIZE = 200  # git diff has no --pathspec-from-file; batch args to stay under OS ARG_MAX


def base_diff_range(base: str) -> str:
    """Full-PR range for round 1: the base is a branch name, needs the remote prefix."""
    return f"origin/{base}...HEAD"


def delta_diff_range(previous_oid: str, base: str | None = None,
                     include_base_merge: bool = False) -> tuple[str, dict]:
    """Delta range for round N>1, returned as (range, info).

    A bare commit oid needs no remote prefix. When the author merged the base
    branch since `previous_oid`, a plain `previous_oid...HEAD` also shows the
    base branch's own changes. Unless `include_base_merge`, build a synthetic
    commit (previous head + the base content HEAD contains) and diff against it,
    so only the author's own changes remain. Conflicted paths take the base
    side. Any failure falls back to the plain range."""
    plain = (f"{previous_oid}...HEAD", {})
    if include_base_merge or not base:
        return plain
    try:
        return _delta_without_base_merge(previous_oid, base) or plain
    except Exception as e:  # never block setup on this optimization
        print(f"WARNING: could not exclude the base merge ({e}); using the plain delta.",
              file=sys.stderr)
        return plain


def _delta_without_base_merge(previous_oid: str, base: str) -> tuple[str, dict] | None:
    import tempfile
    m = git("merge-base", f"origin/{base}", "HEAD")
    if m.returncode != 0:
        return None
    base_oid = m.stdout.strip()
    if git("merge-base", "--is-ancestor", base_oid, previous_oid).returncode == 0:
        return None  # previous head already had this base content: nothing to exclude
    mt = git("merge-tree", "--write-tree", "--name-only", "-z", previous_oid, base_oid)
    if mt.returncode not in (0, 1):
        raise RuntimeError(mt.stderr.strip() or "git merge-tree failed")
    # -z output: <tree> NUL, conflicted paths each NUL-terminated, NUL, messages
    fields = mt.stdout.split("\0")
    tree = fields[0].strip()
    conflicts = []
    for path in fields[1:]:
        if not path:
            break
        conflicts.append(path)
    idx_dir = tempfile.mkdtemp(prefix="review_idx_")
    idx = os.path.join(idx_dir, "index")
    env = {"GIT_INDEX_FILE": idx,
           "GIT_AUTHOR_NAME": "review", "GIT_AUTHOR_EMAIL": "review@localhost",
           "GIT_COMMITTER_NAME": "review", "GIT_COMMITTER_EMAIL": "review@localhost"}
    try:
        if git("read-tree", tree, env=env).returncode != 0:
            raise RuntimeError("read-tree failed")
        for path in conflicts:
            blob = git("rev-parse", f"{base_oid}:{path}")
            if blob.returncode == 0:
                mode = git("ls-tree", base_oid, "--", path).stdout.split()[0]
                r = git("update-index", "--add", "--cacheinfo",
                        f"{mode},{blob.stdout.strip()},{path}", env=env)
            else:
                r = git("update-index", "--force-remove", path, env=env)
            if r.returncode != 0:
                raise RuntimeError(f"could not set base side for {path}: {r.stderr.strip()}")
        wt = git("write-tree", env=env)
        if wt.returncode != 0:
            raise RuntimeError("write-tree failed")
        ct = git("commit-tree", wt.stdout.strip(), "-p", previous_oid, "-m", "review base", env=env)
        if ct.returncode != 0:
            raise RuntimeError(ct.stderr.strip() or "commit-tree failed")
    finally:
        shutil.rmtree(idx_dir, ignore_errors=True)
    return (f"{ct.stdout.strip()}..HEAD",
            {"base_merge_oid": base_oid, "base_conflict_files": conflicts})


def changed_files(range_: str) -> list[str]:
    r = git("diff", "--name-only", range_)
    return [f for f in r.stdout.splitlines() if f]


def detect_generated(files: list[str]) -> set[str]:
    """Returns the subset of `files` considered generated/build-output."""
    generated = set()

    if files:
        r = subprocess.run(
            ["git", "check-attr", "-z", "linguist-generated", "--stdin"],
            input="\0".join(files), capture_output=True, text=True,
        )
        fields = r.stdout.split("\0")
        for i in range(0, len(fields) - 2, 3):
            path, _attr, value = fields[i], fields[i + 1], fields[i + 2]
            if value.strip() in ("set", "true"):
                generated.add(path)

    for path in files:
        if path in generated:
            continue
        base_name = os.path.basename(path)
        if (base_name in _GENERATED_BASENAMES or path.endswith(_GENERATED_SUFFIXES)
                or any(fnmatch.fnmatch(path, pattern) for pattern in _GENERATED_GLOBS)):
            generated.add(path)

    return generated
 
 
def filter_files(files: list[str], exclude_patterns: list[str] | None = None) -> tuple[list[str], set[str], set[str]]:
    """Filter files removing generated files and user-specified exclude globs.
    
    Returns:
        (kept_files, generated_files, user_excluded_files)
    """
    generated = detect_generated(files)
    user_excluded = set()
    if exclude_patterns:
        for path in files:
            if path in generated:
                continue
            if any(fnmatch.fnmatch(path, pattern) for pattern in exclude_patterns):
                user_excluded.add(path)
    kept = [f for f in files if f not in generated and f not in user_excluded]
    return kept, generated, user_excluded

def scoped_diff(range_: str, files: list[str]) -> str:
    """git diff for exactly these files (empty string if files is empty)."""
    if not files:
        return ""
    chunks = [files[i:i + _DIFF_BATCH_SIZE] for i in range(0, len(files), _DIFF_BATCH_SIZE)]
    parts = []
    for chunk in chunks:
        r = git("diff", range_, "--", *chunk)
        if r.returncode != 0:
            raise RuntimeError(f"git diff failed: {r.stderr.strip()}")
        parts.append(r.stdout)
    return "".join(parts)
