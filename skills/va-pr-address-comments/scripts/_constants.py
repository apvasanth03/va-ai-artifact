"""Constants: generated-file patterns, the reply marker, and the bot blocks the cleaner strips.

# Adapted from va-pr-review-collab/scripts/_constants.py (generated-file patterns).
"""

# ── Language & Framework Generated Suffixes ───────────────────────────────────

# Dart / Flutter (code generation, serialization, mocks)
_DART_GENERATED_SUFFIXES = (
    ".g.dart",
    ".freezed.dart",
    ".mocks.dart",
)

# JavaScript / TypeScript / Web (minified assets, generated bundles)
_WEB_GENERATED_SUFFIXES = (
    ".min.js",
    ".min.css",
    ".generated.ts",
    ".generated.js",
)

# Protocol Buffers / gRPC
_PROTOBUF_GENERATED_SUFFIXES = (
    ".pb.go",
    ".pb.cc",
    ".pb.h",
    "_pb2.py",
)

# ── Language & Framework Generated Path Globs ─────────────────────────────────

# Mobile Codegen (e.g. Pigeon's Kotlin/Swift output)
_MOBILE_GENERATED_GLOBS = (
    "*/generates/*/*.kt",
    "*/generates/*/*.swift",
)

# ── Package Manager Lockfiles ────────────────────────────────────────────────

_LOCKFILE_BASENAMES = (
    # Dart / Flutter
    "pubspec.lock",
    # JavaScript / Node
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    # Ruby
    "Gemfile.lock",
    # Python
    "poetry.lock",
    # Rust
    "Cargo.lock",
    # Go
    "go.sum",
    # PHP
    "composer.lock",
)

# ── Combined Generated Patterns ───────────────────────────────────────────────

GENERATED_SUFFIXES = (
    _DART_GENERATED_SUFFIXES
    + _WEB_GENERATED_SUFFIXES
    + _PROTOBUF_GENERATED_SUFFIXES
)

GENERATED_BASENAMES = _LOCKFILE_BASENAMES

GENERATED_GLOBS = _MOBILE_GENERATED_GLOBS


# ── Reply marker ──────────────────────────────────────────────────────────────

# Appended to every posted reply (hidden in GitHub's rendering). Identifies our
# replies for thread selection in later rounds and for idempotent posting.
MARKER_PREFIX = "<!-- va-pr-address-comments r"
MARKER_FORMAT = MARKER_PREFIX + "{round} -->"

# ── Bot noise ─────────────────────────────────────────────────────────────────

# <details> blocks dropped whole, matched on their <summary> text (case-insensitive,
# substring). Everything else in a <details> block is kept and unwrapped, e.g.
# "Committable suggestion", "Suggested fix".
STRIP_DETAILS_SUMMARIES = (
    "prompt for ai agents",
    "analysis chain",
    "scripts executed",
    "supported by static analysis",
    "learnings added",
    "learnings used",
)
