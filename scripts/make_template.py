#!/usr/bin/env python3
"""Generate the copier template from the buildable tree.

The rendered fixture on main is the source of truth; this script compiles
it into a copier template by inverse-stamping the identity strings — the
exact inverse of init.sh's substitution table. A generated template cannot
drift from the tree it was generated from.

Usage: python3 scripts/make_template.py OUT_DIR
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Order matters: longest, most specific first (same discipline as init.sh).
SUBSTITUTIONS = [
    ("https://example.github.io/my-project", "[[ site_url ]]"),
    ("example/my-project", "[[ repo_slug ]]"),
    ("MyProject: a formalization blueprint",
     "[[ project_title ]]: a formalization blueprint"),
    ("A. Author", "[[ author_name ]]"),
    ('demo = "arXiv:0000.00000 (a model source; replace with your first real one)"',
     '[[ source_key ]] = "[[ main_source ]]"'),
    ("A Lean 4 formalization built from the oh-my-formalization starter.",
     "[[ project_description ]]"),
    ("MyProject", "[[ project_name ]]"),
]

SKIP_DIRS = {".git", ".lake", "web", "_site", "__pycache__"}
SKIP_FILES: set[str] = set()


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    out = Path(sys.argv[1]).resolve()
    if out.exists():
        shutil.rmtree(out)

    for src in sorted(root.rglob("*")):
        rel = src.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if not src.is_file() or rel.name in SKIP_FILES:
            continue
        rel_str = str(rel)
        for old, new in SUBSTITUTIONS:
            rel_str = rel_str.replace(old, new)
        # Store .github under a templated directory name: a branch holding
        # .github/workflows/* cannot be pushed by the Actions token.
        if rel_str == ".github" or rel_str.startswith(".github/"):
            rel_str = "[[ dot_github ]]" + rel_str[len(".github"):]
        dest = out / rel_str
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = src.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dest)
            continue
        for old, new in SUBSTITUTIONS:
            text = text.replace(old, new)
        dest.write_text(text, encoding="utf-8")
        dest.chmod(src.stat().st_mode)

    # The answers-file stub: copier writes the instance's recorded merge base
    # (answers + template version) through this file. Template-only machinery,
    # so it is synthesized here rather than living in the buildable tree.
    (out / "[[ _copier_conf.answers_file ]]").write_text(
        "# Recorded by copier: the answers and template version this instance\n"
        "# was rendered from. Do not edit by hand.\n"
        "[[ _copier_answers|to_nice_yaml ]]\n", encoding="utf-8")

    print(f"template generated at {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
