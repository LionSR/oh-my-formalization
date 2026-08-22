# oh-my-formalization

A starter kit for Lean 4 formalization projects with a
[leanblueprint](https://github.com/PatrickMassot/leanblueprint) site,
paper-gap notes, and CI — the framework installed, your repo owning only a
thin configuration. From the family of tools behind
[TNLean](https://github.com/LionSR/TNLean) and
[QICLean](https://github.com/LionSR/QICLean).

## 20 minutes to a live site

Two ways in. **Copier** (recommended — it gives you framework updates later):

```bash
pipx install copier
copier copy -r template gh:LionSR/oh-my-formalization my-repo
```

Copier asks three questions and records its answers plus the template
version in `.copier-answers.yml` — the merge base that later lets
`copier update -r template` replay framework improvements onto your repo
while leaving everything you own untouched.

**Zero-install**: *Use this template* (button above) → clone →
`./init.sh KnotInv "Knot Invariants" you/knot-invariants`. The stamped
`[template]` table in `texra-blueprint.toml` records the same merge base,
so you can adopt copier updates later.

Either way, the only file you'll ever configure afterwards is
`texra-blueprint.toml`.
3. `lake exe cache get && lake build` — **always fetch the Mathlib cache
   before the first build**; green in minutes.
4. Push, then in repo settings enable **Pages → GitHub Actions**. The Pages
   workflow publishes: blueprint (web) · paper-gap notes index.
5. Replace `KnotInv/Basic.lean` and `blueprint/src/chapter/ch01.tex`. The
   sample chapter is a worked example of every macro you need: `\lean{}`,
   `\leanok`, `\notready`, `\uses{}`, `\label`/`\eqref` inside displays, a
   citation, and a paper-gap reference.

## What's inside

| Piece | Where | Notes |
|---|---|---|
| Lean package + one real theorem | `MyProject/` | Mathlib pinned by `lean-toolchain` + `lakefile.toml` |
| Blueprint | `blueprint/src/` | plasTeX plugin from [texra-blueprint](https://github.com/LionSR/texra-blueprint); no local patch copies |
| Paper-gap notes | `docs/paper-gaps/` | policy, template, one demo note; see the `paper-gap-notes` skill in [texra-lean-skills](https://github.com/texra-ai/texra-lean-skills) |
| Config | `texra-blueprint.toml` | site URLs, source-key registry — the file `paper-gaps check` enforces |
| CI | `.github/workflows/` | `ci.yml` (Lean build + blueprint gates + reference check), `pages.yml` (site deploy) |
| Agent skills | `.claude/settings.json` | [texra-lean-skills](https://github.com/texra-ai/texra-lean-skills) auto-installs for Claude Code; other agents run that repo's `install.sh` |

## The paper-gap discipline

A theorem is formalized only when its Lean signature has no hypothesis
absent from the cited source. Every deviation — a smuggled hypothesis, a
corrected constant, a scope restriction — gets a note under
`docs/paper-gaps/`, named `<sourcekey>_<topic>.tex` against the registry in
`texra-blueprint.toml`. CI fails on a reference to a missing note or an
unregistered key. Install the
[texra-lean-skills](https://github.com/texra-ai/texra-lean-skills) plugin
and the `paper-gap-notes` skill walks your agent through it.

## Shared vs. yours

The partition is machine-readable in `copier.yml`: files in
`_skip_if_exists` are rendered once and then **yours** (your mathematics,
`lean-toolchain` — you decide when to bump a toolchain — `lakefile.toml`,
`web.tex` identity, `macros/common.tex` notation, chapters, notes, config,
README). Everything else is **shared**: workflows carrying the framework
pins, `plastex.cfg`, the blueprint preamble (`macros/preamble.tex`), the
paper-gap policy and template. `copier update -r template` rewrites shared
files and never touches yours; editing a shared file locally is the signal
that the change belongs upstream instead.

The `template` branch is generated from `main` by
`scripts/make_template.py` on every push (the exact inverse of `init.sh`'s
substitutions), so the copier template can never drift from the buildable
tree you're looking at.
