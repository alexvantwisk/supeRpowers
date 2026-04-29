# Release Notes

## 0.2.0 (2026-04-29)

First marketplace-ready release. supeRpowers is now a four-layer R programming plugin for Claude Code: 17 skills, 5 slash commands, 5 agents, 1 foundation rule, and a session-start hook — installable with one command.

### Highlights

- **Slash commands.** Five guided workflows are now first-class plugin commands: `/r-tdd-cycle`, `/r-debug`, `/r-pkg-release`, `/r-shiny-app`, `/r-analysis`. Each orchestrates the right skills and agents for a multi-step task.
- **Marketplace install.** Add the repo as a marketplace and install with two commands. Verified end-to-end on macOS.
- **Project-aware session start.** A hook detects R project type (package, Shiny, targets, Quarto, analysis, scripts) and surfaces the most relevant skills, commands, and agents for that project. Cross-platform via a polyglot runner.
- **Toolchain breadth.** Coverage now spans data analysis, visualization, statistics, biostatistics, Shiny, package development, tables, Quarto, performance, machine learning (tidymodels), pipelines (targets), MCP setup, TDD, debugging, and package-skill generation.

### Installation

```bash
claude plugin marketplace add alexvantwisk/supeRpowers
claude plugin install supeRpowers@supeRpowers
```

Or from a local clone:

```bash
claude plugin marketplace add /path/to/supeRpowers
claude plugin install supeRpowers@supeRpowers
```

### Added

#### Skills (4 new since 0.1.0)

- **r-project-setup** — scaffold analysis projects, packages, Shiny apps, Quarto documents (`usethis`, `renv`, `golem`, `quarto`)
- **r-tidymodels** — machine learning workflow: recipes, workflows, tune, yardstick
- **r-targets** — reproducible pipelines, branching, crew integration
- **r-mcp-setup** — MCP server setup for live R session awareness (`btw`, `mcptools`)

(Plus the 13 skills shipped in 0.1.0: r-data-analysis, r-visualization, r-tdd, r-debugging, r-package-dev, r-shiny, r-stats, r-clinical, r-tables, r-quarto, r-performance, r-package-skill-generator, and the meta-skill r-skill-auditor.)

#### Commands (5 new — first appearance)

- **/r-tdd-cycle** — Red, Green, Refactor, Review for testthat 3e packages
- **/r-debug** — reproduce, isolate, diagnose, fix, regression test, verify
- **/r-pkg-release** — audit deps, test, document, R CMD check, version bump, review, submit
- **/r-shiny-app** — scaffold, design modules, wire reactivity, test, architecture review
- **/r-analysis** — import, clean, explore, model, visualize, report

#### Plugin infrastructure

- `.claude-plugin/plugin.json` — manifest in the location required by the current Claude Code plugin schema
- `.claude-plugin/marketplace.json` — declares the repo as a Claude Code marketplace so `claude plugin install` works
- `hooks/session-start` — R project type detection + MCP server probing, cross-platform via `hooks/run-hook.cmd`
- `hooks/detect-mcp.sh` — MCP availability helper used by the session-start hook
- All 5 agents now have YAML frontmatter (`name`, `description`) so Claude Code can dispatch them on intent

#### Documentation

- README with version/license/skills/commands/R badges, four-layer architecture diagram, full skill and command tables, agent catalog, quick-start prompts, install verified end-to-end
- CLAUDE.md development guide covering content formats (skills, commands, agents, rules), R coding conventions, and a verification checklist
- LICENSE (MIT)

### Changed

- **Plugin layout migrated to `commands/`.** The 5 workflow files that previously lived as `skills/r-cmd-*/SKILL.md` are now native plugin commands at `commands/r-*.md`. The redundant `cmd-` infix was dropped: `/r-cmd-tdd-cycle` → `/r-tdd-cycle`, etc. Body content is unchanged — these are the same workflows in a more idiomatic location.
- **Manifest schema updated.** Removed the legacy `claude_code` wrapper from `plugin.json`; content is auto-discovered from the standard directories. `author` is now the object form the validator expects.
- **CLAUDE.md content formats** — agents now require frontmatter (`name`, `description`); commands documented as a new content type alongside skills, rules, and agents.
- **Sibling skill cross-references** updated so the negative-boundary text in `r-data-analysis`, `r-debugging`, `r-tdd`, `r-shiny`, and `r-package-dev` points at the new `/r-*` slash commands.
- **Session-start hook** recommends the new slash command names, not the deprecated `/r-cmd-*` form.

### Fixed

- `tests/test_structural.py` no longer references the removed `claude_code` wrapper. The obsolete glob-coverage and hook-presence tests were dropped (auto-discovery makes the first redundant; `claude plugin validate` covers the second).
- `tests/test_structural.py` gained a new "Command Files" section that validates frontmatter, required `description` field, and the 200-line limit on every file in `commands/`.

### Deprecated / Removed

- The 5 `skills/r-cmd-*/` directories were removed in this release. They had no installed users — the plugin had not yet been published to a marketplace before now. Any prior in-development reference to `/r-cmd-<name>` should be updated to `/r-<name>`.

### Known Issues

- The plugin name `supeRpowers` is not kebab-case. Claude Code accepts it for local and GitHub-marketplace installs (verified in this release), but the public claude.ai marketplace sync requires kebab-case. A future major version may rename for that purpose.
- A small number of pre-existing test failures remain in `python tests/run_all.py` (e.g. `agent-no-frontmatter` checks that conflict with the new requirement, `r-mcp-setup` description format gaps, a couple of line-limit overruns). These do not affect plugin behavior at runtime; tracked for the 0.2.x patch series.

### Documentation Pointers

- Migration plan and rationale: `docs/superpowers/plans/2026-04-29-cmd-skills-to-commands-migration.md`
- Superseded design: `docs/superpowers/specs/2026-04-01-commands-layer-design.md` (kept for historical context — the assumption that plugins didn't support a `commands/` directory turned out to be wrong)
- Development conventions: `CLAUDE.md`

---

## 0.1.0 (2026-03-15)

Initial scaffold release.

### Added

- **Foundation:** r-conventions rule (base pipe, tidyverse-first, style guide)
- **Phase 1:** r-data-analysis, r-visualization, r-tdd, r-debugging skills
- **Phase 2:** r-package-dev, r-shiny skills + r-code-reviewer, r-dependency-manager agents
- **Phase 3:** r-stats, r-clinical, r-tables, r-quarto skills + r-statistician, r-pkg-check, r-shiny-architect agents
- **Phase 4:** r-performance, r-package-skill-generator skills
- **Docs:** CLAUDE.md development guide
- **Config:** plugin.json manifest
