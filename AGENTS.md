# AGENTS.md

MyProject is a Lean 4 formalization built on Mathlib, with a blueprint
(`blueprint/`) and paper-gap notes (`docs/paper-gaps/`). Shared conventions
come from the installed `lean-conventions` skill; project-local facts belong
in `docs/project_conventions.md` (create it when the first fact appears).

## Build

```bash
lake exe cache get   # ALWAYS before the first build or after a Mathlib bump
lake build
cd blueprint && leanblueprint web && leanblueprint pdf
texra-blueprint paper-gaps check
```

Never build Mathlib from source; if a build starts compiling Mathlib, stop
and fetch the cache.

## First session: interview, then scaffold

If `texra-blueprint.toml` still contains the `demo` source key, this project
has not chosen its subject yet. Ask the user:

1. Which paper(s) or notes are you formalizing? (arXiv id or citation)
2. What is the main theorem you are aiming at?

Then scaffold from the answers: replace the `demo` entry in
`[paper_gaps.sources]` with a real source key (author initials + two-digit
year); add the reference to `blueprint/src/references.bib` and cite it from
`blueprint/src/chapter/ch01.tex`; restate the chapter around the target
theorem as `\notready` statements with `\uses{}` dependencies; put source
files under `Papers/` if the user has them. Keep the faithfulness rule from
the `paper-gap-notes` skill: a Lean statement with hypotheses the source
does not have is a different theorem — record every deviation as a note.

## Blueprint loop

When adding or completing a theorem: update the chapter entry, add
`\lean{}` and `\leanok`, keep `\uses{}` accurate, and verify with
`lake build` then `leanblueprint checkdecls`.
