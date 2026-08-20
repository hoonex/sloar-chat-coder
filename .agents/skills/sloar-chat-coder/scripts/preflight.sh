#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--self-test" ]]; then
  root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
  skill="$root/.agents/skills/sloar-chat-coder/SKILL.md"
  [[ -f "$skill" ]] || { echo "missing SKILL.md" >&2; exit 1; }
  grep -q '^name: sloar-chat-coder$' "$skill" || { echo "invalid skill name" >&2; exit 1; }
  grep -q '^description:' "$skill" || { echo "missing description" >&2; exit 1; }
  [[ "$(cat "$root/VERSION")" == "0.2.0" ]] || { echo "VERSION mismatch" >&2; exit 1; }
  for f in "$root"/.agents/skills/sloar-chat-coder/scripts/*.sh; do bash -n "$f"; done
  python3 -m py_compile "$root"/.agents/skills/sloar-chat-coder/scripts/*.py
  [[ -f "$root/docs/FIRST_RUN.md" ]] || { echo "missing first-run guide" >&2; exit 1; }
  [[ -f "$root/.agents/skills/sloar-chat-coder/references/environment-onboarding.md" ]] || { echo "missing onboarding reference" >&2; exit 1; }
  echo "sloar self-test: ok"
  exit 0
fi

repo="${1:-.}"
cd "$repo"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "not a git working tree: $repo" >&2
  exit 2
}

head_sha="$(git rev-parse HEAD)"
tree_sha="$(git rev-parse 'HEAD^{tree}')"
branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || printf '%s' '(detached)')"

if [[ -n "$(git status --porcelain)" ]]; then
  dirty=true
else
  dirty=false
fi

printf 'repository=%s\n' "$(basename "$(git rev-parse --show-toplevel)")"
printf 'branch=%s\n' "$branch"
printf 'head=%s\n' "$head_sha"
printf 'tree=%s\n' "$tree_sha"
printf 'dirty=%s\n' "$dirty"
