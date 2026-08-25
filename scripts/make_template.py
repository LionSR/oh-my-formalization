#!/usr/bin/env python3
"""Generate the copier template from the buildable tree.

The rendered fixture on main is the source of truth; this script compiles
it into a copier template by inverse-stamping the identity strings. A
generated template cannot drift from the tree it was generated from.

Usage: python3 scripts/make_template.py OUT_DIR
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# The main-source fixture literal also appears as the copier.yml question
# default and in texra-blueprint.toml; main() checks both against this one.
MAIN_SOURCE_FIXTURE = \
    "arXiv:0000.00000 (a model source; replace with your first real one)"

# Order matters: a fixture string containing another must come first, so the
# longer match is consumed before the shorter one mangles it. main() checks
# this ordering, and that every entry still occurs in the tree.
SUBSTITUTIONS = [
    ("[[ site_url ]]", "[[ site_url ]]"),
    ("[[ repo_slug ]]", "[[ repo_slug ]]"),
    ("[[ project_title ]]", "[[ project_title ]]"),
    ("[[ author_name ]]", "[[ author_name ]]"),
    (f'demo = "{MAIN_SOURCE_FIXTURE}"',
     '[[ source_key ]] = "[[ main_source ]]"'),
    ("[[ project_description ]]",
     "[[ project_description ]]"),
    ("[[ project_name ]]", "[[ project_name ]]"),
]


def tracked_files(root: Path) -> list[str]:
    """The committed tree only: build artifacts never leak into the template."""
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True, capture_output=True, text=True).stdout
    return sorted(filter(None, listing.split("\0")))


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    out = Path(sys.argv[1]).resolve()
    if out.exists():
        shutil.rmtree(out)

    copier_text = (root / "copier.yml").read_text(encoding="utf-8")
    if f'default: "{MAIN_SOURCE_FIXTURE}"' not in copier_text:
        sys.exit("copier.yml main_source default drifted from "
                 "MAIN_SOURCE_FIXTURE in scripts/make_template.py")

    for i, (old, _) in enumerate(SUBSTITUTIONS):
        for later, _ in SUBSTITUTIONS[i + 1:]:
            if old in later:
                sys.exit(f"substitution order hazard: {old!r} would corrupt "
                         f"the later, longer entry {later!r}")

    hits = dict.fromkeys((old for old, _ in SUBSTITUTIONS), 0)
    for rel_str in tracked_files(root):
        src = root / rel_str
        if not src.is_file():
            continue
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
            count = text.count(old)
            if count:
                hits[old] += count
                text = text.replace(old, new)
        dest.write_text(text, encoding="utf-8")
        dest.chmod(src.stat().st_mode)

    if missing := [old for old, count in hits.items() if count == 0]:
        sys.exit("fixture strings no longer occur in the tree (the template "
                 "would render incompletely): " + ", ".join(map(repr, missing)))

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
