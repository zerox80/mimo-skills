#!/usr/bin/env python3
"""Capture a stable source binding and path inventory for a deep-security-scan pass.

Stdlib only. Read-only against the target. Writes one binding.json for reuse by
every pass so no pass silently swaps the inspected source state.

Usage:
  python bind_source.py TARGET [--scope GLOB ...] [--exclude GLOB ...]
                         [--out binding.json] [--max-files N]

Exit codes: 0 ok, 1 binding failure, 2 usage error.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_EXCLUDES = [
    ".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", "target",
    ".venv", "venv", "__pycache__", ".tox", ".mypy_cache", ".pytest_cache",
    ".gradle", ".idea", ".vscode", "coverage", ".next", ".nuxt", "out",
    "*.min.js", "*.min.css", "*.map", "*.lock", "package-lock.json",
    "yarn.lock", "pnpm-lock.yaml", "Cargo.lock", "poetry.lock",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.ico", "*.pdf",
    "*.woff", "*.woff2", "*.ttf", "*.eot", "*.mp4", "*.mp3", "*.zip",
    "*.tar", "*.gz", "*.bz2", "*.xz", "*.7z", "*.jar", "*.class", "*.o",
    "*.so", "*.dylib", "*.dll", "*.exe", "*.bin", "*.pyc", "*.pyo",
]

SKIP_DIR_NAMES = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    ".tox", ".mypy_cache", ".pytest_cache", ".gradle", ".idea", ".vscode",
    "dist", "build", "target", "coverage", ".next", ".nuxt",
}


def run_git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip()


def is_excluded(rel: str, name: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, "*/" + pat):
            return True
    return False


def inventory(root: Path, scopes: list[str], excludes: list[str], max_files: int) -> tuple[list[str], list[str]]:
    kept: list[str] = []
    skipped_dirs: set[str] = set()
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
        # prune
        pruned = []
        for d in list(dirnames):
            rel = f"{rel_dir}/{d}" if rel_dir else d
            if d in SKIP_DIR_NAMES or is_excluded(rel, d, excludes):
                skipped_dirs.add(rel)
                pruned.append(d)
        for d in pruned:
            dirnames.remove(d)
        for fn in filenames:
            rel = f"{rel_dir}/{fn}" if rel_dir else fn
            if is_excluded(rel, fn, excludes):
                continue
            if scopes and not any(fnmatch.fnmatch(rel, s) or rel.startswith(s.rstrip("/") + "/") or rel == s.rstrip("/")
                                  for s in scopes):
                continue
            kept.append(rel)
            if len(kept) >= max_files:
                return sorted(kept), sorted(skipped_dirs | {f"(truncated at {max_files} files)"})
    return sorted(kept), sorted(skipped_dirs)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="repository root or scoped directory to bind")
    ap.add_argument("--scope", action="append", default=[], help="include pattern or path prefix (repeatable)")
    ap.add_argument("--exclude", action="append", default=[], help="exclude glob (repeatable)")
    ap.add_argument("--out", default="binding.json", help="output path (default: binding.json)")
    ap.add_argument("--max-files", type=int, default=20000, help="inventory cap")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        print(f"ERROR: target does not exist: {target}", file=sys.stderr)
        return 1

    excludes = DEFAULT_EXCLUDES + args.exclude
    files, skipped = inventory(target, args.scope, excludes, args.max_files)

    git_root_s = run_git(target, "rev-parse", "--show-toplevel")
    is_repo = git_root_s is not None
    git_root = Path(git_root_s) if git_root_s else None

    revision = dirty = branch = None
    submodules = []
    if is_repo and git_root is not None:
        revision = run_git(git_root, "rev-parse", "HEAD")
        branch = run_git(git_root, "rev-parse", "--abbrev-ref", "HEAD")
        status = run_git(git_root, "status", "--porcelain")
        dirty = bool(status) if status is not None else None
        # dirty relative to bound target only
        if dirty and status:
            target_rel = os.path.relpath(target, git_root) if target != git_root else ""
            if target_rel and target_rel != ".":
                lines = [ln for ln in status.splitlines() if ln[3:].startswith(target_rel.rstrip("/") + "/") or ln[3:] == target_rel]
                dirty = bool(lines)
        sm = run_git(git_root, "submodule", "status")
        if sm:
            for line in sm.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2:
                    sha = parts[0]
                    flag = ""
                    if sha and sha[0] in "-+U":
                        flag = sha[0]
                        sha = sha[1:]
                    submodules.append({
                        "path": parts[1],
                        "revision": sha,
                        "status_flag": flag,
                    })

    binding = {
        "format": "mimo-security-scan/v1",
        "kind": "source-binding",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "target": {
            "path": str(target),
            "name": target.name,
            "is_git_repo": is_repo,
            "git_root": str(git_root) if git_root else None,
            "revision": revision,
            "revision_short": revision[:12] if revision else None,
            "branch": branch,
            "dirty_tree": dirty,
            "submodules": submodules,
        },
        "scope": {
            "include": args.scope or ["(entire target)"],
            "exclude_user": args.exclude,
            "exclude_defaults_applied": True,
        },
        "inventory": {
            "file_count": len(files),
            "files": files,
            "skipped_dirs": skipped,
            "truncated": any(s.startswith("(truncated") for s in skipped),
        },
        "notes": [],
    }

    if dirty is True:
        binding["notes"].append(
            "Working tree is dirty relative to the bound target. Every pass must reuse this binding; "
            "stop and rebind if the tree drifts mid-scan."
        )
    if not is_repo:
        binding["notes"].append(
            "Target is not a git repository. Source identity is the inventory digest below; "
            "re-run bind_source.py if the directory changes."
        )

    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(binding, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Bound: {target}")
    print(f"  revision: {revision or '(none)'}  dirty: {dirty}  files: {len(files)}")
    print(f"  wrote: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
