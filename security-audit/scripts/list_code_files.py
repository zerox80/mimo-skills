#!/usr/bin/env python3
"""List code files for the security-audit skill.

Rules (must match SKILL.md):
  - Only code files (extension allowlist).
  - Skip every directory whose name starts with '.'.
  - Skip binary files and files larger than MAX_BYTES.

Usage:
  python list_code_files.py [ROOT]
  python list_code_files.py --json [ROOT]

Prints one relative path per line (or JSON array with --json).
Exit code 0 = success, 2 = usage error.
"""

from __future__ import annotations

import json
import os
import sys

MAX_BYTES = 1_500_000  # skip huge files; not useful for static review

CODE_EXTENSIONS = {
    # web / frontend
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue", ".svelte",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    # backend / systems
    ".py", ".pyw", ".rb", ".php", ".go", ".rs", ".java", ".kt", ".kts",
    ".scala", ".cs", ".fs", ".fsx", ".swift", ".m", ".mm", ".dart",
    ".ex", ".exs", ".groovy", ".lua", ".pl", ".pm", ".r",
    # native
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".inl",
    # scripting / shell
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".psm1", ".bat", ".cmd",
    # data / query / config-as-code
    ".sql", ".graphql", ".gql", ".proto",
    # infra / build
    ".tf", ".tfvars", ".hcl", ".gradle", ".cmake", ".mk", ".dockerfile",
    ".yaml", ".yml", ".toml", ".json", ".xml", ".ini", ".cfg", ".conf",
    ".env.example", ".properties",
}

# Exact filenames without a conventional extension
CODE_FILENAMES = {
    "Dockerfile", "Containerfile", "Makefile", "CMakeLists.txt",
    "Jenkinsfile", "Vagrantfile", "Gemfile", "Rakefile", "Procfile",
    "BUILD", "BUILD.bazel", "WORKSPACE", "WORKSPACE.bazel",
}


def is_code_file(name: str) -> bool:
    lower = name.lower()
    if name in CODE_FILENAMES or lower in {n.lower() for n in CODE_FILENAMES}:
        return True
    # multi-part suffixes first (e.g. .env.example)
    for ext in sorted(CODE_EXTENSIONS, key=len, reverse=True):
        if lower.endswith(ext):
            return True
    return False


def is_probably_binary(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return True
        # high ratio of non-text bytes
        text_chars = bytes(range(32, 127)) + b"\n\r\t\f\b"
        nontext = sum(1 for b in chunk if b not in text_chars)
        return bool(chunk) and (nontext / len(chunk)) > 0.30
    except OSError:
        return True


def collect(root: str) -> list[str]:
    results: list[str] = []
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        # Hard rule: never descend into directories starting with '.'
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        for name in sorted(filenames):
            if name.startswith("."):
                # dotfiles are not "code files" in this skill's scope
                continue
            if not is_code_file(name):
                continue
            full = os.path.join(dirpath, name)
            try:
                if os.path.getsize(full) > MAX_BYTES:
                    continue
            except OSError:
                continue
            if is_probably_binary(full):
                continue
            results.append(os.path.relpath(full, root))
    return results


def main() -> int:
    args = [a for a in sys.argv[1:]]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if len(args) > 1:
        print(__doc__.strip())
        return 2
    root = args[0] if args else "."
    if not os.path.isdir(root):
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2
    files = collect(root)
    if as_json:
        print(json.dumps(files, indent=2, ensure_ascii=False))
    else:
        for p in files:
            print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
