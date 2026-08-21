# oh-my-formalization

A starter kit for Lean 4 formalization projects with a
[leanblueprint](https://github.com/PatrickMassot/leanblueprint) site,
paper-gap notes, and CI — the framework installed, your repo owning only a
thin configuration. From the family of tools behind
[TNLean](https://github.com/LionSR/TNLean) and
[QICLean](https://github.com/LionSR/QICLean).

## 20 minutes to a live site

1. **Use this template** (button above) → clone your new repo.
2. `./init.sh KnotInv "Knot Invariants" you/knot-invariants` — stamps your
   identity into the tree; the only other file you'll ever configure is
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

## The paper-gap discipline

A theorem is formalized only when its Lean signature has no hypothesis
absent from the cited source. Every deviation — a smuggled hypothesis, a
corrected constant, a scope restriction — gets a note under
`docs/paper-gaps/`, named `<sourcekey>_<topic>.tex` against the registry in
`texra-blueprint.toml`. CI fails on a reference to a missing note or an
unregistered key. Install the
[texra-lean-skills](https://github.com/texra-ai/texra-lean-skills) plugin
and the `paper-gap-notes` skill walks your agent through it.

## Updating the framework

Everything shared arrives by version pin: bump the `texra-blueprint` tag in
the two workflows (and the `lean-env-action` tag) and read the diff. Your
repo owns its mathematics, its chapters, its notes, and its config — nothing
else to sync.
