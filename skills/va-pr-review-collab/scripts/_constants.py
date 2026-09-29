"""Constants for generated file detection and review filtering."""

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
