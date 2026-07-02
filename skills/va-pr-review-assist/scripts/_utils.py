"""Shared utilities for va-pr-review-assist scripts."""
import json, os, re, subprocess, sys


# ── Meta ────────────────────────────────────────────────────────────────────

def read_meta(workspace: str) -> dict:
    with open(os.path.join(workspace, "meta.json")) as f:
        return json.load(f)


def write_meta(workspace: str, meta: dict) -> None:
    with open(os.path.join(workspace, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)


# ── Concern item parsing / writing ──────────────────────────────────────────

_HEADER = re.compile(r"^#### (.+?) — \[(.+?)\] — Round (\d+)")
_FIELD  = re.compile(r"^- \*\*(.+?)\*\*: ?(.*)")


def parse_concerns(filepath: str) -> list[dict]:
    """Parse Concern Items from a markdown file."""
    concerns, current = [], {}
    with open(filepath) as f:
        for raw in f:
            line = raw.rstrip()
            m = _HEADER.match(line)
            if m:
                if current:
                    concerns.append(current)
                current = {
                    "title":    m.group(1).strip(),
                    "severity": m.group(2).strip(),
                    "round":    int(m.group(3)),
                }
                continue
            m = _FIELD.match(line)
            if m and current:
                key = m.group(1).lower().replace(" ", "_")
                val = m.group(2).strip()
                if key == "file":
                    val = val.strip("`")
                current[key] = val
    if current:
        concerns.append(current)
    return concerns


def write_concern(f, concern: dict, include_post_fields: bool = False) -> None:
    """Write a single Concern Item in markdown format."""
    f.write(f"#### {concern['title']} — [{concern['severity']}] — Round {concern['round']}\n")
    f.write(f"- **File**: `{concern.get('file', '')}`\n")
    f.write(f"- **Lines**: {concern.get('lines', '—')}\n")
    f.write(f"- **Issue**: {concern.get('issue', '')}\n")
    f.write(f"- **Why**: {concern.get('why', '')}\n")
    f.write(f"- **Suggestion**: {concern.get('suggestion', '')}\n")
    if include_post_fields:
        f.write(f"- **Comment ID**: {concern.get('comment_id', '')}\n")
        f.write(f"- **Thread ID**: {concern.get('thread_id', '')}\n")
        f.write(f"- **URL**: {concern.get('url', '')}\n")
    for key, val in concern.items():
        if key.startswith("replied_round_"):
            label = " ".join(p.capitalize() for p in key.split("_"))  # replied_round_2 → Replied Round 2
            f.write(f"- **{label}**: {val}\n")
    f.write("\n")


def read_comments(workspace: str) -> list[dict]:
    path = os.path.join(workspace, "comments", "comments.md")
    if not os.path.exists(path):
        return []
    return parse_concerns(path)


def write_comments(workspace: str, concerns: list[dict]) -> None:
    path = os.path.join(workspace, "comments", "comments.md")
    with open(path, "w") as f:
        for c in concerns:
            write_concern(f, c, include_post_fields=True)


def append_to_comments(workspace: str, concerns: list[dict]) -> None:
    path = os.path.join(workspace, "comments", "comments.md")
    with open(path, "a") as f:
        for c in concerns:
            write_concern(f, c, include_post_fields=True)


def append_to_resolved(workspace: str, concerns: list[dict]) -> None:
    path = os.path.join(workspace, "comments", "comments_resolved.md")
    with open(path, "a") as f:
        for c in concerns:
            write_concern(f, c, include_post_fields=True)


# ── gh / git helpers ─────────────────────────────────────────────────────────

def gh(*args) -> dict:
    """Run a gh command, return parsed JSON. Raises on error."""
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"gh error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout) if result.stdout.strip() else {}


def graphql(query: str) -> dict:
    """Run a GraphQL query via gh, return parsed data dict."""
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"GraphQL error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout).get("data", {})


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


# ── Diff scoping (generated-file filtering) ──────────────────────────────────

# Generic fallback patterns for common generated/lockfile artifacts across
# ecosystems. Repos that tag generated files via `.gitattributes`
# (linguist-generated=true) are detected via git check-attr instead — this
# list only covers repos that don't.
_GENERATED_SUFFIXES = (
    ".g.dart", ".freezed.dart", ".mocks.dart", ".pb.go", ".pb.cc", ".pb.h",
    "_pb2.py", ".min.js", ".min.css", ".generated.ts", ".generated.js",
)
_GENERATED_BASENAMES = (
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Gemfile.lock",
    "poetry.lock", "Cargo.lock", "go.sum", "pubspec.lock", "composer.lock",
)

_DIFF_BATCH_SIZE = 200  # git diff has no --pathspec-from-file support; batch positional args to stay well under OS ARG_MAX


def diff_range(base: str) -> str:
    return f"origin/{base}...HEAD"


def changed_files(base: str) -> list[str]:
    r = git("diff", "--name-only", diff_range(base))
    return [f for f in r.stdout.splitlines() if f]


def detect_generated(files: list[str]) -> set[str]:
    """Returns the subset of `files` considered generated/build-output."""
    generated = set()

    if files:
        # -z on both sides avoids C-style quoting of paths with special
        # characters (spaces, colons, non-ASCII) that would otherwise never
        # match an entry in `files` and silently slip through unfiltered.
        r = subprocess.run(
            ["git", "check-attr", "-z", "linguist-generated", "--stdin"],
            input="\0".join(files), capture_output=True, text=True,
        )
        fields = r.stdout.split("\0")
        # Output is NUL-separated triplets: path, attribute, value, ...
        for i in range(0, len(fields) - 2, 3):
            path, _attr, value = fields[i], fields[i + 1], fields[i + 2]
            if value.strip() in ("set", "true"):
                generated.add(path)

    for path in files:
        if path in generated:
            continue
        base_name = os.path.basename(path)
        if base_name in _GENERATED_BASENAMES or path.endswith(_GENERATED_SUFFIXES):
            generated.add(path)

    return generated


def scoped_diff(base: str, files: list[str]) -> str:
    """git diff for exactly these files (empty string if files is empty).

    Batches the file list rather than passing it all as positional args in
    one call, so a large file list can't hit the OS argument-length limit
    (git diff has no --pathspec-from-file support, unlike git add/rm/etc).

    Raises RuntimeError on failure rather than silently returning partial
    output — a mid-batch git failure must not produce a truncated patch
    that looks complete to a downstream reader.
    """
    if not files:
        return ""
    chunks = [files[i:i + _DIFF_BATCH_SIZE] for i in range(0, len(files), _DIFF_BATCH_SIZE)]
    parts = []
    for chunk in chunks:
        r = git("diff", diff_range(base), "--", *chunk)
        if r.returncode != 0:
            raise RuntimeError(f"git diff failed: {r.stderr.strip()}")
        parts.append(r.stdout)
    return "".join(parts)


# ── Comment body formatting ───────────────────────────────────────────────────

def format_body(concern: dict) -> str:
    return (
        f"**{concern['severity'].upper()}: {concern['title']}**\n\n"
        f"**Issue**: {concern.get('issue', '')}\n"
        f"**Why**: {concern.get('why', '')}\n"
        f"**Suggestion**: {concern.get('suggestion', '')}"
    )


# ── Thread ID lookup ─────────────────────────────────────────────────────────

def fetch_thread_map(owner: str, repo: str, pr_number: int) -> dict[int, str]:
    """Returns {comment_database_id: thread_node_id}."""
    data = graphql(f"""
{{
  repository(owner: "{owner}", name: "{repo}") {{
    pullRequest(number: {pr_number}) {{
      reviewThreads(first: 100) {{
        nodes {{
          id
          isResolved
          comments(first: 1) {{ nodes {{ databaseId }} }}
        }}
      }}
    }}
  }}
}}""")
    threads = (
        data.get("repository", {})
            .get("pullRequest", {})
            .get("reviewThreads", {})
            .get("nodes", [])
    )
    return {
        t["comments"]["nodes"][0]["databaseId"]: t["id"]
        for t in threads
        if t["comments"]["nodes"]
    }


def fetch_resolved_ids(owner: str, repo: str, pr_number: int) -> set[int]:
    """Returns set of comment database IDs whose threads are resolved."""
    data = graphql(f"""
{{
  repository(owner: "{owner}", name: "{repo}") {{
    pullRequest(number: {pr_number}) {{
      reviewThreads(first: 100) {{
        nodes {{
          isResolved
          comments(first: 1) {{ nodes {{ databaseId }} }}
        }}
      }}
    }}
  }}
}}""")
    threads = (
        data.get("repository", {})
            .get("pullRequest", {})
            .get("reviewThreads", {})
            .get("nodes", [])
    )
    return {
        t["comments"]["nodes"][0]["databaseId"]
        for t in threads
        if t["isResolved"] and t["comments"]["nodes"]
    }
