# r-shiny Skill Upgrade — Design Spec

**Date:** 2026-04-28
**Author:** Alexander van Twisk (with Claude)
**Status:** Approved (brainstorm complete; pending implementation plan)
**Target:** `skills/r-shiny/` in the `supeRpowers` Claude Code plugin

---

## Goal

Upgrade the `r-shiny` skill so it (a) conforms to Claude Code skill best practices, (b) covers the four production frameworks practitioners actually use (base Shiny, golem, rhino, teal), and (c) serves as a high-leverage reference for clinical-trial-adjacent Shiny work — interactive data review, safety dashboards, patient profile viewers, ad-hoc exploration tools.

The current skill is solid (256-line SKILL.md + two references) but framework-thin: golem and rhino are mentioned without depth, and **teal — the de-facto pharma standard for clinical-trial dashboards — is absent**. The skill also lacks a structured deployment story and conflates testing layers.

## Non-Goals

- Shiny for Python coverage (boundary line only — kept R-only to match plugin scope).
- A separate `r-shiny-teal` skill (deferred; revisit if `references/teal.md` exceeds ~500 lines).
- New agents (the existing `r-shiny-architect` gets minor framework-aware additions).
- Edits to `r-cmd-shiny-app` workflow command skill (potential follow-up).
- `plugin.json` schema changes (the manifest does not support per-skill file-pattern hooks; routing stays keyword-driven).

## Scope decisions (locked)

| # | Question | Decision |
|---|---|---|
| 1 | Python Shiny scope | **R only.** One-line "for Python Shiny, see [py-shiny] — out of scope" boundary in description. |
| 2 | Boundary with r-visualization / r-tables | **Strict link-out + 4-row reactive-output cheat sheet** (`renderPlot`, `renderPlotly`, `renderDT`, `renderReactable`) with explicit "for plot content / table styling, see r-visualization / r-tables." |
| 3 | UI framework coverage | **bslib primary** + a `shinydashboard` migration table (`dashboardPage`→`page_navbar`, `box`→`card`, `valueBox`→`value_box`, etc.). Alt UIs (bs4Dash, shinyMobile, shiny.semantic) get a lazy reference. |
| 4 | Deployment scope | **Decision table in SKILL.md + Posit Connect & Docker recipes in `references/deployment.md`.** Covers shinyapps.io, Posit Connect (validated/regulated), Docker + ShinyProxy, Shiny Server. `renv` mandated across all targets. |
| 5 | Framework coverage | **Single skill, framework-picker section + per-framework lazy references** (`golem.md`, `rhino.md`, `teal.md`-substantive, `frameworks-decision.md`, `ui-frameworks-alt.md`). teal gets the deepest reference (~330 lines). |
| 6 | Testing scope | **Both layers**: `testServer()` (module unit tests) + `shinytest2::AppDriver` (integration). Decision table in SKILL.md, deep content in `references/testing.md`. |
| 7 | Tidy-data assumption | **Assume dplyr fluency.** Defer data-manipulation patterns to `r-data-analysis`. Add one Shiny-specific reactive data-flow idiom (`data_raw → reactive filter → reactive summary → output`) — not present in `r-data-analysis`. |
| 8 | Trigger surface | **Keywords-only, expanded.** Add: golem, teal, rhino, bs4Dash, shinyManager, AppDriver, testServer, moduleServer, bindCache, bslib, card, value_box, renderUI, reactiveVal, observeEvent, Posit Connect, ShinyProxy, app.R, ui.R, server.R, mod_*.R, R/app_ui.R, R/app_server.R. Explicit negative boundaries against r-visualization, r-tables, r-quarto, r-debugging, r-clinical (ADaM domain), Python Shiny. |

## Approach

**Approach B — SKILL.md rewrite + additive references + eval refresh.**

The structural changes (framework picker, decision tables for outputs/UI/deployment, `shinydashboard` migration block, reactive data-flow idiom) are large enough that surgical edits would leave seams. The new references are clearly additive. The eval refresh is required regardless to cover teal/golem/deployment cases.

## SKILL.md outline (target ≤290 lines)

1. Frontmatter — `name`, `description` (700–900 chars; expanded triggers + 5 negative boundaries).
2. One-paragraph intro — R conventions reaffirmed (`|>`, `<-`, `snake_case`, `""`).
3. Lazy reference index — 7 references, one line each.
4. Agent dispatch — `r-shiny-architect`.
5. MCP integration — `btw_tool_env_describe_data_frame`, `btw_tool_docs_help_page`.
6. **Framework picker (new, ~25 lines)** — decision table over base / golem / rhino / teal; clinical-trial steer ("ADaM/SDTM data → teal first"); pointers to `references/{frameworks-decision,golem,rhino,teal}.md`.
7. Minimal `app.R` example (~15 lines).
8. Reactivity decision guide (~20 lines) → pointer to `references/reactivity-guide.md`.
9. Modules — `NS()`, `moduleServer()`, return-reactive contract (~25 lines) → pointer to `references/modules-patterns.md`.
10. **UI with bslib + `shinydashboard` migration table (new, ~25 lines)** → pointer to `references/ui-frameworks-alt.md`.
11. Dynamic UI table (~10 lines).
12. **Reactive data-flow idiom (new, ~15 lines)** — `req()` / `validate()` / `bindCache()` placement; defers dplyr basics to `r-data-analysis`.
13. **Outputs cheat sheet (new, ~10 lines)** — 4-row table; boundary to r-visualization / r-tables.
14. Performance + JS integration (~10 lines).
15. **Testing — restructured (~20 lines)** — decision table; tiny example each → pointer to `references/testing.md`.
16. **Deployment — restructured (~20 lines)** — decision table; `renv` universal → pointer to `references/deployment.md`.
17. Gotchas table — kept rows + 2 new (teal data schema mismatch, async without promises).
18. Examples — kept happy path + edge case; add 1 teal example, 1 golem example.

## References inventory

| File | Status | Target lines | Contents |
|---|---|---|---|
| `references/reactivity-guide.md` | kept (398) | — | Reactivity anti-patterns, debugging, bindCache/debounce/throttle |
| `references/modules-patterns.md` | kept (538) | — | Module communication, nesting, testing, common patterns |
| `references/frameworks-decision.md` | new | ~120 | Side-by-side comparison (base/golem/rhino/teal): file layout, learning curve, deployment fit, when to migrate, switch signals |
| `references/golem.md` | new | ~250 | `create_golem()`, `add_module()`, `add_fct_*` / `add_utils_*`, `golem-config.yml` env profiles, `run_app()` options, `add_dockerfile()`, dev vs prod, gotchas (golden_path, `inst/` data, namespacing) |
| `references/rhino.md` | new | ~180 | `rhino::init()`, `app/main.R`, `app/view/`, `app/logic/`, `box::use()`, Sass pipeline, Cypress + shinytest2, `rhino.yml`, when rhino > golem |
| `references/teal.md` | new | ~330 | `teal.data::cdisc_data()` and `cdisc_dataset()`; ADaM/SDTM ingestion; `teal::init()` declarative pipelines; standard `teal.modules.clinical` modules (mod_a_patient_profile, mod_t_summary, etc.); custom modules via `teal::module()`; `teal.slice` filter panels; `teal.transform` choices/variable selectors; joining keys; validation reports; bridge to r-clinical for domain semantics |
| `references/ui-frameworks-alt.md` | new | ~70 | bs4Dash, shinyMobile, shiny.semantic, argonDash — install, hello-world, when to pick, gotchas |
| `references/testing.md` | new | ~250 | testServer fundamentals (`setInputs`/`getReturned`/`session`); shinytest2 (`AppDriver`, `expect_values`, snapshots, headless Chrome on CI); fixtures and shinyloadtest; mocking external services with mockery / httptest2; golem-specific test layout; teal app testing; flake patterns; GitHub Actions matrix |
| `references/deployment.md` | new | ~220 | Posit Connect (publishing flow, `manifest.json`, env vars, content settings, validated/qualified envs for clinical); shinyapps.io (account, slug limits, free vs paid); Docker (golem dockerfile, multi-stage build, ShinyProxy `application.yml`, ldap/oauth); Shiny Server / Shiny Server Pro (legacy on-prem); `renv` across all four; log access; scaling notes (workers, autoscale) |

**Total references after upgrade:** 9 files (~2,356 lines combined, all lazy-loaded).

## Scripts

| File | Status | Notes |
|---|---|---|
| `scripts/check_modules.R` | kept | Static check for missing `ns()` wrapping in module UI |

## eval.md refresh

**Preserved verbatim:** all existing prompts (Quarto/visualization deferral cases stay — they are proven boundary tests).

**New binary eval questions (8–12):**
- 8. Clinical-trial dashboard on ADaM/SDTM data → recommends teal (`teal::init()` + `teal.modules.clinical`) rather than building modules from scratch?
- 9. Production scaffolding with multiple modules and tests → recommends golem (or rhino if box-modules requested)?
- 10. "How do I test this" prompts → covers both `testServer()` and `shinytest2::AppDriver`?
- 11. Validated/regulated deployment → recommends Posit Connect or Docker+ShinyProxy with `renv` (not shinyapps.io)?
- 12. Assumes dplyr fluency? (Does not restate tidyverse basics inside Shiny code.)

**New test prompts:**

*Happy Path:*
- "Scaffold a golem app with a `mod_filter` module and a `mod_chart` module that share a filtered dataset."
- "Build a teal app for an ADaM ADSL dataset showing demographics and a treatment-by-arm summary table."

*Edge Cases:*
- "Migrate this `shinydashboard` app (`dashboardPage` + `box` + `valueBox`) to bslib." (must produce mapping, not rewrite UX)
- "Add a `bindCache()` to my expensive plot — what should the cache keys be?" (must list reactive inputs the plot depends on)
- "My teal app fails with 'no datasets defined' — what's wrong?" (must point at `teal.data::cdisc_data()` schema)

*Adversarial:*
- "Convert this Shiny app to Python." (must defer / decline)
- "Style my DT table with conditional coloring and rowgroup totals." (must defer to r-tables)

**New success criteria:**
- Clinical/ADaM dashboard prompts MUST recommend teal; building from raw `moduleServer` is a failure.
- Production scaffolding prompts MUST recommend golem (or rhino if box-modules signaled), not raw `app.R`.
- Validated/regulated deployment prompts MUST recommend Posit Connect or Docker+ShinyProxy with `renv`.
- Python Shiny prompts MUST defer/decline; generating R Shiny code in response is a failure.
- DT styling prompts MUST defer to r-tables.

## Agent updates — `r-shiny-architect`

Stays ≤200 lines. Two surgical additions:

- **Step 1 ("Scan app structure"):** add teal pattern detection — `teal::init()` calls, `teal.data` usage, `app/teal_app.R` layout.
- **Step 6 ("Assess framework adherence"):** add teal subsection — datasets defined via `cdisc_data()`, modules registered, `teal.slice` config present, custom modules use `teal::module()` not raw `moduleServer`.
- Severity guide: no changes.

## Rule and hook updates

- `rules/r-conventions.md`: no changes.
- `hooks/session-start`: no changes (current detection covers Shiny/golem/rhino; teal apps register as Shiny and the new skill content surfaces teal guidance).

## Isolation

Implementation will run in a git worktree at `.claude/worktrees/r-shiny-upgrade/` on branch `feature/r-shiny-upgrade`, leaving `main` untouched until merge. The worktree is created during the writing-plans → executing-plans handoff, not as part of the spec doc.

## Verification before completion

1. `python tests/run_all.py` — all routing/structural/conventions tests pass.
2. `grep -rn '%>%' skills/r-shiny/ agents/r-shiny-architect.md --exclude=eval.md` — zero hits.
3. `wc -l skills/r-shiny/SKILL.md` — ≤300.
4. SKILL.md `description` length ≤1024 chars.
5. Boundary lines mention r-visualization, r-tables, r-quarto, r-debugging, r-clinical, Python Shiny.
6. Cross-link sanity: every `references/*.md` referenced in SKILL.md exists.
7. All R code in skill content uses `|>`, `<-`, `snake_case`, double quotes (skill-auditor pass).

## Out-of-scope clarifications

- Does **not** introduce a `py-shiny` skill (mentioned only as a boundary).
- Does **not** split teal into its own skill (revisit threshold: `teal.md` > 500 lines or routing collisions surface).
- Does **not** modify the `r-cmd-shiny-app` workflow command skill.
- Does **not** modify other supeRpowers skills (r-clinical, r-data-analysis, r-tables, r-visualization, r-quarto, r-debugging) — only references them across boundary lines.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| `references/teal.md` becomes the single largest reference and feels disproportionate | Cap at ~330 lines; if growing past 500, promote to `r-shiny-teal` skill |
| Routing collision with `r-clinical` for ADaM/SDTM dashboard prompts | Boundary line in description: r-shiny owns "build a Shiny/teal app on clinical data"; r-clinical owns "what is ADaM ADSL / how do I derive avisitn"; teal reference cross-links both |
| SKILL.md drifts above 300 lines after adding new sections | Aggressive condensation of existing sections (reactivity guide, modules) — push detail to existing references; final `wc -l` check before commit |
| New eval prompts add cost without catching real regressions | All new criteria match observed Shiny project failure modes; binary eval questions are pass/fail and cheap |
| Existing users relying on current SKILL.md section anchors | SKILL.md anchors are not part of the public API of the plugin; routing is description-keyword-based; no migration concern |

## Deliverables

1. Rewritten `skills/r-shiny/SKILL.md` (≤290 lines).
2. Seven new references (`frameworks-decision.md`, `golem.md`, `rhino.md`, `teal.md`, `ui-frameworks-alt.md`, `testing.md`, `deployment.md`).
3. Refreshed `skills/r-shiny/eval.md` with new binary questions, prompts, and success criteria.
4. Minor edits to `agents/r-shiny-architect.md` (teal awareness in steps 1 and 6).
5. All tests passing under `python tests/run_all.py`.
