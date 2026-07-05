# Contributing to supeRpowers

Thanks for your interest in supeRpowers — an R programming plugin for Claude
Code. Contributions are welcome. This guide covers both filing issues and
submitting pull requests.

---

## Status: beta, single maintainer

supeRpowers is in public beta and is currently maintained by a single author.
Two practical consequences:

- **Response times can be days, occasionally longer.** Please be patient.
- **Conventions are still settling.** Frontmatter formats, the routing
  matrix, and content patterns have shifted between minor versions and may
  shift again. For anything bigger than a typo, please open an issue first
  to align before spending time on a PR.

---

## How to contribute

| You want to... | Do this |
|---|---|
| Report a bug | [Open a bug-report issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=bug_report.md) |
| Suggest a new skill, workflow, or agent | [Open a feature-request issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=feature_request.md) |
| Suggest content for an existing skill | [Open a skill-suggestion issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=skill_suggestion.md) |
| Fix a typo or small documentation error | Open a PR directly |
| Fix a bug or add a small feature | Open an issue, then PR (link the issue) |
| Add a new skill, workflow, or agent | Open an issue **first**, then PR |
| Refactor or restructure existing content | Open an issue first |

Issues and PRs are both welcome. Issues are preferred for anything that
needs design discussion before code.

---

## Filing a good issue

The bar is low — please don't let it stop you filing — but issues that
include the following get triaged and resolved fastest.

### Bug reports

- **Plugin version** (`claude plugin list` output)
- **Claude Code version** (`claude --version`)
- **R version** and operating system
- **Reproducer** — a one- or two-line prompt to Claude Code that triggers
  the problem, plus what you expected vs what happened
- **Logs or output** if Claude Code returned an error or the wrong skill
  activated

### Feature / skill suggestions

- **What problem you're trying to solve.** "I have to write a CDISC SDTM
  mapping every week and the plugin doesn't help" is more useful than
  "add a CDISC SDTM skill."
- **What you've tried.** Which existing skills came close, and where they
  fell short.
- **A concrete example prompt** you'd want the plugin to handle well.

### Skill content suggestions

If you want to suggest a fix or addition to an existing skill:

- Name the skill (`r-tdd`, `r-shiny`, ...)
- Describe what's wrong or missing in plain prose
- Link to authoritative sources (CRAN docs, package vignettes, Posit blog
  posts) the maintainer can verify against

You don't need to draft the actual change — describing what should be in
the skill is enough.

---

## Submitting a pull request

### Before you start

- For anything bigger than a typo, please open an issue first so we can
  align on direction before you invest time in code
- Read [`CLAUDE.md`](CLAUDE.md) for content-format requirements (skill,
  workflow-skill, agent, and rule conventions)
- Skim the [R coding conventions](#r-coding-conventions) below

### Workflow

1. Fork the repo and create a branch from `main`
2. Make your change
3. Run the test suite:

   ```bash
   python tests/run_all.py
   ```

   - The full suite must pass cleanly (exit 0). CI fails the PR on any
     structural, convention, or routing failure.

4. Run the convention spot-check:

   ```bash
   grep -rn '%>%' skills/ agents/ rules/ --exclude=eval.md
   ```

   This must produce zero output.

5. Push your branch and open a PR against `main`
6. Fill in the PR template
7. Be patient — review may take a few days

### Adding a new skill / workflow / agent

See [`CLAUDE.md`](CLAUDE.md) for canonical procedures. Briefly:

- **New knowledge skill:** create `skills/<name>/SKILL.md` with `name` +
  `description` + `when_to_use` frontmatter (triggers live in
  `when_to_use`; combined `description` + `when_to_use` ≤ 1536 chars);
  optional `paths`, `references/`, `scripts/`, `eval.md`, `evals/evals.json`.
  Keep SKILL.md ≤ 300 lines; offload detail to `references/`.
- **New workflow skill:** create `skills/<name>/SKILL.md` with `name` +
  one-line `description` + `disable-model-invocation: true`. Invoked only
  as `/r-<name>`; no `when_to_use`, no `Triggers:`, no `eval.md`. ≤ 300 lines.
- **New agent:** create `agents/<name>.md` with `name` + `description`
  frontmatter and Inputs / Output / Procedure sections. ≤ 200 lines.

For new knowledge skills, also update `tests/routing_matrix.json` with at
least one positive test plus 1–2 negative tests against sibling skills.

## Evals

Knowledge skills carry an `evals/evals.json` alongside `SKILL.md` (schema:
`skill_name`, a `scenarios[]` array with `prompt`/`expected_output`/
`expectations[]`, and a `trigger_set[]` of should/should-not-trigger
queries). Two layers exercise them:

- **Cheap, deterministic (CI-gating).** `python tests/run_all.py --layer 3`
  validates the eval files' structure and the trigger-set shape offline. It
  runs on every PR — no API calls, no cost. When you add or edit a skill's
  `evals/evals.json`, this must stay green.
- **Full with/without-skill benchmark (manual/nightly, NOT PR-gating).** Run
  the skill-creator `run_eval.py` benchmark locally or on a nightly job to
  measure whether the skill actually improves Claude's answers on its
  scenarios; archive the resulting `grading.json` as a CI artifact. This is
  expensive (LLM calls) so it never blocks a PR.

When the `r-analysis` workflow's step list changes, regenerate the demo GIF:
record with `asciinema` and render with `agg` (`agg docs/media/r-analysis.cast
docs/media/r-analysis.gif`), committing both the `.cast` and the `.gif`.

---

## R coding conventions

All R code in skills, agents, rules, references, and examples must follow:

- `|>` only, never `%>%` (magrittr)
- `<-` for assignment (not `=`, except in function arguments)
- Tidyverse-first: `dplyr`, `tidyr`, `purrr`, `ggplot2`, `readr`,
  `stringr`, `forcats`, `lubridate`
- `snake_case` for identifiers
- Double quotes for strings
- Target R >= 4.1.0

---

## Commit message format

```
<type>(<scope>): <subject>

<optional body explaining why, not what>
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `perf`. Scope is
the skill, command, or agent name when applicable.

Examples:

```
feat(r-targets): add crew integration reference for parallel pipelines
fix(hooks): resolve session-start hook on Windows
docs(readme): expand installation troubleshooting
```

---

## Code of conduct

Be respectful, be specific, and assume good intent. Discussion stays
focused on the plugin and how to make it better. Personal attacks,
discriminatory language, or off-topic disputes will result in the issue
or PR being locked.

---

## Licensing

supeRpowers is MIT-licensed (see [LICENSE](LICENSE)). By contributing —
whether via issue or PR — you agree that your contribution may be used
under the same MIT licence.

---

## Maintainer

Alexander van Twisk — issues at
https://github.com/alexvantwisk/supeRpowers/issues
