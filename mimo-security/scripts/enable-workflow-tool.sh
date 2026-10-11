#!/usr/bin/env bash
# Turn on MiMoCode's workflow tool for future sessions (mimo-security scan).
# Idempotent: safe to run more than once. Does not touch the running process —
# MiMoCode must be restarted (new shell) after this.
set -euo pipefail

FLAG='export MIMOCODE_EXPERIMENTAL_WORKFLOW_TOOL=true'
MARKER='MIMOCODE_EXPERIMENTAL_WORKFLOW_TOOL'

rc=""
for candidate in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
  if [ -f "$candidate" ]; then
    rc="$candidate"
    break
  fi
done
if [ -z "$rc" ]; then
  rc="$HOME/.bashrc"
fi

if grep -q "$MARKER" "$rc" 2>/dev/null; then
  echo "already enabled in $rc"
else
  printf '\n# Enable MiMoCode dynamic workflows (mimo-security scan)\n%s\n' "$FLAG" >>"$rc"
  echo "added to $rc"
fi

case "${MIMOCODE_EXPERIMENTAL_WORKFLOW_TOOL:-}" in
  true | 1) echo "this process already has the flag" ;;
  *)
    echo "restart MiMoCode (new shell) so the flag takes effect"
    ;;
esac
