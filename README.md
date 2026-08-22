# oh-my-formalization

> A Lean 4 formalization built from the oh-my-formalization starter.

A starter kit for Lean 4 formalization projects. One `copier copy` gives you
a building Lean package on [Mathlib](https://github.com/leanprover-community/mathlib4),
a [blueprint](https://github.com/PatrickMassot/leanblueprint) published as a
website and PDF, a citable paper-gap note apparatus, and CI for all of it.

## What you get

- **Lean package** pinned to a Mathlib release, with one sample theorem.
- **Blueprint** (web + PDF): mathematical prose linked to Lean declarations,
  with a dependency graph. The sample chapter demonstrates every macro you
  need: `\lean{}`, `\leanok`, `\notready`, `\uses{}`, labels inside displays,
  citations, and a paper-gap reference.
- **Paper-gap notes**: wherever your formalization deviates from a cited
  source (a missing hypothesis, a corrected constant, a restricted scope),
  you record a short mathematical note. Notes are named against a source-key
  registry, carry a machine-read verdict (kind + status), and publish as a
  severity-sorted index with permanent, citable PDF URLs. CI fails on a
  reference to a missing note.
- **CI and Pages**: a Lean build with the Mathlib cache, blueprint render
  gates, the paper-gap checks, and an artifact-based GitHub Pages deploy —
  no gh-pages branch.
- **Agent skills**: the [texra-lean-skills](https://github.com/texra-ai/texra-lean-skills)
  bundle works with any coding agent — install with
  `npx skills add texra-ai/texra-lean-skills` (Claude Code sessions pick it
  up automatically from the repository settings).

## Quickstart

```bash
pipx install copier
copier copy -r template gh:LionSR/oh-my-formalization my-project
cd my-project && git init && git add -A && git commit -m "Initialize from oh-my-formalization"
```

Copier asks eight questions: package name, title, `owner/repo`, author, site
URL (override the default for a custom domain — it becomes your permanent
citation base), a one-line description, and optionally the source key and
citation of the main paper you are formalizing (keep the defaults to decide
later).

Then:

1. `lake exe cache get && lake build` — always fetch the Mathlib cache
   before the first build; green in minutes.
2. Create the GitHub repository, push, and enable **Settings → Pages →
   GitHub Actions**. Your site appears with the blueprint (web and PDF) and
   the paper-gap index.
3. Replace `MyProject/Basic.lean` and `blueprint/src/chapter/ch01.tex` with
   your first real result. Any coding agent with the skills installed will
   interview you about the paper you are formalizing and scaffold from
   there (see `AGENTS.md`).

The only file you configure afterwards is `texra-blueprint.toml`.

## Updating

Framework improvements arrive with `copier update -r template` — a three-way
merge against the recorded template version that leaves everything you own
(your mathematics, chapters, notes, and config) untouched. The shared/owned
split is machine-readable in `copier.yml`.

## Under the hood

Blueprint tooling comes from the [texra-blueprint](https://github.com/LionSR/texra-blueprint)
plasTeX plugin and CLI, pinned by tag in `.github/actions/blueprint-env`; CI composes
[lean-env-action](https://github.com/texra-ai/lean-env-action). Both are
independently versioned — updating a pin is a one-line change.
