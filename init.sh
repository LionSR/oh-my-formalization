#!/usr/bin/env bash
# Stamp your project's identity into the template.
# Usage: ./init.sh <PackageName> "<Human Title>" <owner/repo>
# Example: ./init.sh KnotInv "Knot Invariants" alice/knot-invariants
set -euo pipefail

if [ $# -ne 3 ]; then
  sed -n '2,4p' "$0"; exit 2
fi

NAME="$1"; TITLE="$2"; SLUG="$3"
OWNER="${SLUG%%/*}"; REPO="${SLUG##*/}"

if ! [[ "$NAME" =~ ^[A-Z][A-Za-z0-9]*$ ]]; then
  echo "PackageName must be UpperCamelCase (got: $NAME)"; exit 2
fi

# File contents.
grep -rl "MyProject\|example/my-project\|example\.github\.io/my-project" \
    --exclude-dir=.git --exclude=init.sh . | while read -r f; do
  sed -i.bak \
    -e "s|example\.github\.io/my-project|${OWNER}.github.io/${REPO}|g" \
    -e "s|example/my-project|${SLUG}|g" \
    -e "s|MyProject: a formalization blueprint|${TITLE}: a formalization blueprint|g" \
    -e "s|MyProject|${NAME}|g" \
    "$f" && rm "$f.bak"
done

# File and directory names.
git mv MyProject.lean "${NAME}.lean"
git mv MyProject "${NAME}"

# Record where this instance came from: the template and the commit it was
# instantiated from. This is the merge base any future update tooling needs;
# it cannot be reconstructed later, so it is written now.
TEMPLATE_REPO="LionSR/oh-my-formalization"
TEMPLATE_SHA="$(git ls-remote "https://github.com/${TEMPLATE_REPO}" HEAD | cut -f1)"
{
  echo ""
  echo "[template]"
  echo "repo = \"${TEMPLATE_REPO}\""
  echo "ref  = \"${TEMPLATE_SHA:-unknown}\"   # commit this instance was stamped from"
  echo "date = \"$(date +%Y-%m-%d)\""
} >> texra-blueprint.toml

echo "Stamped ${NAME} (${TITLE}) for ${SLUG}."
echo "Next: lake exe cache get && lake build, then commit and push."
