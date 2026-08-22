#!/usr/bin/env bash
# Build the copier template branch from the buildable tree.
#
# Usage: scripts/build_template_branch.sh OUT_DIR
#
# Runs scripts/make_template.py into OUT_DIR and commits the result on a
# fresh `template` branch. Pushing the branch is the caller's job; the CI
# smoke test consumes the local branch without pushing. Shared by
# .github/workflows/ci.yml and .github/workflows/template.yml so the two
# cannot diverge.
set -euo pipefail

test "$#" -eq 1 || {
  echo "usage: scripts/build_template_branch.sh OUT_DIR" >&2
  exit 2
}
OUT_DIR="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

python3 "$REPO_ROOT/scripts/make_template.py" "$OUT_DIR"
cd "$OUT_DIR"
git init -q -b template
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add -A
git commit -q -m "Generated from ${GITHUB_SHA:-the local tree}"
