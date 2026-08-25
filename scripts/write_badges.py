#!/usr/bin/env python3
"""Write Shields.io endpoint JSON files for the project homepage.

Usage:
  write_badges.py [OUTPUT_DIR]

  OUTPUT_DIR  Directory to write badge JSON files into.
              Defaults to <repo-root>/badges.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = ROOT / "[[ project_name ]]"
BLUEPRINT_SRC = ROOT / "blueprint" / "src"

_PROOF_BEARING_ENV_TYPES: frozenset[str] = frozenset(
    {"theorem", "lemma", "proposition", "corollary"}
)
_SKIP_ENV_TYPES: frozenset[str] = frozenset({"remark", "example"})


def strip_lean_comments_and_strings(text: str) -> str:
    """Remove Lean comments and strings while preserving token separation."""
    out: list[str] = []
    i = 0
    n = len(text)
    block_depth = 0
    in_string = False

    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""

        if block_depth:
            if ch == "/" and nxt == "-":
                block_depth += 1
                out.append("  ")
                i += 2
            elif ch == "-" and nxt == "/":
                block_depth -= 1
                out.append("  ")
                i += 2
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue

        if in_string:
            if ch == "\\" and nxt:
                out.append("  ")
                i += 2
            else:
                if ch == '"':
                    in_string = False
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue

        if ch == "-" and nxt == "-":
            while i < n and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if ch == "/" and nxt == "-":
            block_depth = 1
            out.append("  ")
            i += 2
            continue
        if ch == '"':
            in_string = True
            out.append(" ")
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def lean_files() -> list[Path]:
    return [
        path
        for path in LEAN_ROOT.rglob("*.lean")
        if "Archive" not in path.relative_to(LEAN_ROOT).parts
    ]


def count_token(token: str) -> int:
    pattern = re.compile(rf"(?<![A-Za-z0-9_']){re.escape(token)}(?![A-Za-z0-9_'])")
    total = 0
    for path in lean_files():
        total += len(pattern.findall(strip_lean_comments_and_strings(path.read_text())))
    return total


def lean_version() -> str:
    raw = (ROOT / "lean-toolchain").read_text().strip()
    return raw.rsplit(":", 1)[-1] if ":" in raw else raw


def mathlib_version() -> str:
    manifest = json.loads((ROOT / "lake-manifest.json").read_text())
    for package in manifest.get("packages", []):
        if package.get("name") == "mathlib":
            return package.get("inputRev") or package.get("rev", "")[:7]
    return "unknown"


def write_badge(name: str, label: str, message: str, color: str, badge_dir: Path) -> None:
    badge_dir.mkdir(parents=True, exist_ok=True)
    payload = {"schemaVersion": 1, "label": label, "message": message, "color": color}
    (badge_dir / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n")


def count_color(count: int, *, warning_at: int = 1, danger_at: int | None = None) -> str:
    if count == 0:
        return "brightgreen"
    if count <= warning_at:
        return "yellow"
    if danger_at is not None and count >= danger_at:
        return "red"
    return "orange"


_TEX_LEAN_RE = re.compile(r"\\lean\{([^}]*)\}", re.DOTALL)
_TEX_LEANOK_RE = re.compile(r"\\leanok")
_TEX_ENV_BEGIN_RE = re.compile(
    r"\\begin\{(definition|theorem|lemma|proposition|corollary|remark|example)\}"
    r"(?:\[.*?\])?"
    r"(?:\\label\{([^}]+)\})?"
)
_TEX_ENV_END_RE = re.compile(
    r"\\end\{(definition|theorem|lemma|proposition|corollary|remark|example)\}"
)
_TEX_PROOF_BEGIN_RE = re.compile(r"\\begin\{proof\}")
_TEX_PROOF_END_RE = re.compile(r"\\end\{proof\}")


@dataclass
class _BlueprintEntry:
    lean_decl: str
    env_type: str
    has_leanok: bool
    proof_has_leanok: bool


def _split_lean_decls(payload: str) -> list[str]:
    payload = re.sub(r"%[^\n]*\n\s*", "", payload)
    payload = re.sub(r"%[^\n]*$", "", payload)
    normalised = re.sub(r"\s+", " ", payload)
    return [decl.strip() for decl in normalised.split(",") if decl.strip()]


def collect_blueprint_entries(blueprint_src: Path) -> list[_BlueprintEntry]:
    """Parse theorem-like blueprint environments for ``\\lean{}`` and ``\\leanok``."""
    entries: list[_BlueprintEntry] = []
    chapter = blueprint_src / "chapter"
    files = sorted(chapter.glob("*.tex")) if chapter.is_dir() else []
    for tex_file in files:
        text = tex_file.read_text(errors="replace")
        lines = text.splitlines()
        lean_decls_by_line: dict[int, list[str]] = {}
        for lm in _TEX_LEAN_RE.finditer(text):
            start_line = text.count("\n", 0, lm.start()) + 1
            lean_decls_by_line.setdefault(start_line, []).extend(
                _split_lean_decls(lm.group(1))
            )
        env_stack: list[dict] = []
        in_proof = False
        current_proof: dict | None = None
        last_env: dict | None = None

        def finish_proof() -> None:
            nonlocal in_proof, current_proof
            if current_proof and current_proof["has_leanok"] and last_env:
                for idx in range(last_env["_entry_start"], last_env["_entry_end"]):
                    e = entries[idx]
                    entries[idx] = _BlueprintEntry(
                        lean_decl=e.lean_decl,
                        env_type=e.env_type,
                        has_leanok=e.has_leanok,
                        proof_has_leanok=True,
                    )
            in_proof = False
            current_proof = None

        for i, line in enumerate(lines, 1):
            m = _TEX_ENV_BEGIN_RE.search(line)
            if m:
                env_stack.append({
                    "type": m.group(1),
                    "lean_decls": list(lean_decls_by_line.get(i, [])),
                    "has_leanok": bool(_TEX_LEANOK_RE.search(line)),
                })
                continue
            m = _TEX_ENV_END_RE.search(line)
            if m and env_stack:
                env = env_stack.pop()
                start = len(entries)
                for decl in env["lean_decls"]:
                    entries.append(_BlueprintEntry(
                        lean_decl=decl,
                        env_type=env["type"],
                        has_leanok=env["has_leanok"],
                        proof_has_leanok=False,
                    ))
                env["_entry_start"] = start
                env["_entry_end"] = len(entries)
                if start < len(entries):
                    last_env = env
                continue
            if _TEX_PROOF_BEGIN_RE.search(line):
                in_proof = True
                current_proof = {"has_leanok": bool(_TEX_LEANOK_RE.search(line))}
                if _TEX_PROOF_END_RE.search(line):
                    finish_proof()
                continue
            if in_proof:
                if current_proof and _TEX_LEANOK_RE.search(line):
                    current_proof["has_leanok"] = True
                if _TEX_PROOF_END_RE.search(line):
                    finish_proof()
                continue
            if env_stack:
                env_stack[-1]["lean_decls"].extend(lean_decls_by_line.get(i, []))
                if _TEX_LEANOK_RE.search(line):
                    env_stack[-1]["has_leanok"] = True
    return entries


def blueprint_badge_counts() -> tuple[int, int]:
    """Return (no_leanok_count, not_ready_count) for unique blueprint declarations."""
    entries = collect_blueprint_entries(BLUEPRINT_SRC)
    decl_entries: dict[str, list] = defaultdict(list)
    for entry in entries:
        decl_entries[entry.lean_decl].append(entry)

    no_leanok = 0
    not_ready = 0
    for elist in decl_entries.values():
        has_stmt = any(e.has_leanok for e in elist)
        has_proof = any(e.proof_has_leanok for e in elist)
        env_types = {e.env_type for e in elist}
        if not has_stmt and not has_proof:
            no_leanok += 1
        if env_types <= _SKIP_ENV_TYPES:
            continue
        is_proof_bearing = bool(env_types & _PROOF_BEARING_ENV_TYPES)
        if is_proof_bearing:
            if not (has_stmt and has_proof):
                not_ready += 1
        elif not has_stmt:
            not_ready += 1
    return no_leanok, not_ready


def main() -> None:
    badge_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "badges"
    sorries = count_token("sorry")
    axioms = count_token("axiom")
    write_badge("sorries", "sorries", str(sorries), count_color(sorries, warning_at=10), badge_dir)
    write_badge("axioms", "axioms", str(axioms), count_color(axioms, warning_at=0), badge_dir)
    write_badge("lean", "Lean", lean_version(), "blue", badge_dir)
    write_badge("mathlib", "Mathlib", mathlib_version(), "blue", badge_dir)
    no_leanok, not_ready = blueprint_badge_counts()
    write_badge(
        "blueprint_no_leanok",
        r"blueprint: no \leanok",
        str(no_leanok),
        count_color(no_leanok, warning_at=100, danger_at=300),
        badge_dir,
    )
    write_badge(
        "blueprint_not_ready",
        "blueprint: not ready",
        str(not_ready),
        count_color(not_ready, warning_at=100, danger_at=300),
        badge_dir,
    )


if __name__ == "__main__":
    main()
