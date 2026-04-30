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
| Suggest a new skill, command, or agent | [Open a feature-request issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=feature_request.md) |
| Suggest content for an existing skill | [Open a skill-suggestion issue](https://github.com/alexvantwisk/supeRpowers/issues/new?template=skill_suggestion.md) |
| Fix a typo or small documentation error | Open a PR directly |
| Fix a bug or add a small feature | Open an issue, then PR (link the issue) |
| Add a new skill, command, or agent | Open an issue **first**, then PR |
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
  command, agent, and rule conventions)
- Skim the [R coding conventions](#r-coding-conventions) below

### Workflow

1. Fork the repo and create a branch from `main`
2. Make your change
3. Run the test suite:

   ```bash
   python tests/run_all.py
   ```

   - Routing tests should remain at 141/141 (or higher if you added a
     skill and routing entries)
   - No NEW structural or convention failures. Ten pre-existing structural
     failures (in `r-mcp-setup`, agent frontmatters, and one rule
     line-limit) are documented as known issues for the 0.2.x patch
     series — those don't block your PR.

4. Run the convention spot-check:

   ```bash
   grep -rn '%>%' skills/ commands/ agents/ rules/ --exclude=eval.md
   ```

   This must produce zero output.

5. Push your branch and open a PR against `main`
6. Fill in the PR template
7. Be patient — review may take a few days

### Adding a new skill / command / agent

See [`CLAUDE.md`](CLAUDE.md) for canonical procedures. Briefly:

- **New skill:** create `skills/<name>/SKILL.md` with `name` + `description`
  frontmatter; optional `references/`, `scripts/`, `eval.md`. Keep
  SKILL.md ≤ 300 lines; offload detail to `references/`.
- **New command:** create `commands/<name>.md` with single-field
  `description:` frontmatter. ≤ 200 lines including frontmatter.
- **New agent:** create `agents/<name>.md` with `name` + `description`
  frontmatter and Inputs / Output / Procedure sections. ≤ 200 lines.

For new skills, also update `tests/routing_matrix.json` with at least one
positive test plus 1–2 negative tests against sibling skills.

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
