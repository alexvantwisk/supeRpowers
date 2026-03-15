# Release Notes

## 0.2.0 (2026-03-15)

### Added
- **Hooks:** Session-start hook detects R project type (package, Shiny, targets, Quarto, analysis, scripts) and surfaces relevant skills/agents
- **Hooks:** Cross-platform polyglot runner for Windows compatibility
- **Skill:** r-project-setup — scaffold analysis projects, packages, Shiny apps, Quarto documents
- **Skill:** r-tidymodels — machine learning with tidymodels ecosystem (recipes, workflows, tune, yardstick)
- **Skill:** r-targets — reproducible pipeline orchestration with targets, branching, and integrations
- **Docs:** README with badges, architecture diagram, skill/agent catalogs, quick start
- **Docs:** LICENSE (MIT)

### Changed
- plugin.json: added hooks directory, new keywords, bumped version to 0.2.0

## 0.1.0 (2026-03-15)

### Added
- **Foundation:** r-conventions rule (base pipe, tidyverse-first, style guide)
- **Phase 1:** r-data-analysis, r-visualization, r-tdd, r-debugging skills
- **Phase 2:** r-package-dev, r-shiny skills + r-code-reviewer, r-dependency-manager agents
- **Phase 3:** r-stats, r-clinical, r-tables, r-quarto skills + r-statistician, r-pkg-check, r-shiny-architect agents
- **Phase 4:** r-performance, r-package-skill-generator skills
- **Docs:** CLAUDE.md development guide
- **Config:** plugin.json manifest
