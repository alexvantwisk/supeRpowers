# Plan: r-data-analysis Skill Expansion

## Summary

Expand the `r-data-analysis` skill so its body matches the seven tidyverse
packages it advertises in the frontmatter, plus the maximalist supplementary
set (janitor, naniar, pointblank). Today the skill is dplyr- and join-heavy;
stringr/forcats/lubridate/purrr are named in triggers but barely covered in
references, and tidy-data principles are scattered. Keep `SKILL.md` tight
(target ≤220 lines, hard cap 300) and push all new depth into lazy-loaded
references. Deliverables: 7 new reference files, a small expansion of
`SKILL.md`, light edits to `references/dplyr-patterns.md`, new entries in
`tests/routing_matrix.json`, and new questions in `eval.md`.

## Prerequisites

Read first: `tasks/handoff-r-data-analysis.md` (brief), `tasks/plan-1-workflow-commands.md`
(format), all of `skills/r-data-analysis/` (`SKILL.md`, both references,
`eval.md`), `rules/r-conventions.md`, `tests/routing_matrix.json` (entries
`route-016`/`-018`/`-039`/`-040` plus the `route-024` pointblank collision),
and `plugin.json` (skills load via `skills/*/SKILL.md` glob — no manifest
change needed for new references).

## 1. Findings — current coverage

`skills/r-data-analysis/` inventory:

- `SKILL.md` — 195 lines; description 513/1024 chars
  - Frontmatter L1–14 · lazy refs L21–23 · agent dispatch L25–28 · MCP block
    L30–33 · readr import L37–51 · dplyr+tidyr conventions L55–66 · Joins
    L69–84 · stringr/forcats/lubridate L88–93 (6 lines for 3 packages) ·
    Missing data L96–103 · data.table boundary L107–122 · Verification
    L125–127 · Gotchas L129–141 · Examples L144–196
- `references/dplyr-patterns.md` — 208 lines (across, pick, .by, reframe,
  consecutive_id, case_match, window functions, rowwise, .data/.env)
- `references/join-guide.md` — 186 lines (decision tree, join_by, inequality,
  rolling, relationship arg, diagnostics, gotchas)
- `eval.md` — 50 lines, 7 binary questions, 13 prompts
- `scripts/check_join_safety.R` — 52 lines

Per-package depth audit: dplyr extensive (SKILL + dedicated reference); tidyr
moderate (pivots and `separate_wider_delim` only; `nest()` mentioned but not
elaborated); readr moderate-good (`read_csv` + `col_types`/locale); stringr,
forcats, purrr minimal — each effectively one sentence; lubridate moderate
(parsers + `floor/ceiling_date`; no time zones, no periods).

## 2. Gaps — ordered by triggering frequency

Frequency ranked using routing-matrix entries (`route-016`, `route-018`,
`route-039`, `route-040`) and tidyverse usage frequency in real workflows:

1. **purrr** — `route-040` ("learn purrr") routes here; advertised in triggers
   but body is empty
2. **stringr** — pervasive in cleaning; one sentence today
3. **tidyr depth** — `unnest_longer/wider`, `hoist`, `complete`, `fill`,
   `expand`, `expand_grid`, `separate_*` family
4. **lubridate depth** — time zones (`with_tz`, `force_tz`), periods vs
   durations, `%m+%`/`%m-%`, `parse_date_time` with multi-format orders
5. **forcats depth** — full reorder/lump/recode/collapse/explicit_na family
6. **janitor cleaning idioms** — `clean_names`, `tabyl`, `remove_empty`,
   `get_dupes`
7. **naniar missing-data EDA** — `miss_var_summary`, `vis_miss`, `gg_miss_*`
8. **pointblank/validate** — usage-side data validation pipelines (rules,
   `agent`, `interrogate`); flag boundary with `route-024`
9. **Tidy-data principles** — currently scattered; needs a foundational
   anchor in the body

## 3. Proposed structure

### SKILL.md changes (target ≤220 lines)

- [ ] Extend frontmatter `description` toward ~750/1024 chars to add triggers:
      `nested data`, `list-columns`, `regex`, `time zone`, `factor reorder`,
      `clean names`, `data validation`, `missing data EDA`. Preserve existing
      negative boundaries; add: `Do NOT use for pipeline orchestration — use
      r-targets instead.`
- [ ] Add a 12-line "Tidy-data principles" anchor section (observation per
      row, variable per column, value per cell) with a lazy pointer to
      `references/tidyr-reshape.md`
- [ ] Replace L88–93 (6-line "stringr/forcats/lubridate" block) with three
      sub-blocks of 3–5 lines each, each terminating in a lazy reference
      pointer
- [ ] Add a purrr sub-block (5 lines) → `references/purrr-patterns.md`
- [ ] Add a data-cleaning sub-block (6 lines) → `references/data-cleaning-toolkit.md`
- [ ] Add a validation sub-block (4 lines) → `references/data-validation.md`
      with the explicit note that *package-introduction* questions still go to
      `r-package-skill-generator`
- [ ] Verification, Gotchas, Examples sections unchanged

### New reference files

| File | Lines | Scope |
| ---- | ----- | ----- |
| `references/purrr-patterns.md` | 160 | `map`/`map2`/`pmap`/`map_*` typed variants, `walk`, `reduce`/`accumulate`, list-columns + `nest() + map() + broom`, `safely`/`possibly`/`quietly`, list rectangling, when to prefer `across()` over `map()` |
| `references/stringr-recipes.md` | 120 | `str_detect`/`extract`/`replace`/`replace_all`, `str_split_*`, `str_pad`/`squish`/`trim`, `str_to_*`, regex fundamentals, `regex()` flags, `glue` interop note |
| `references/lubridate-recipes.md` | 120 | parsers (`ymd`, `ymd_hms`, `parse_date_time` with multi-orders), components (`year`, `wday`, `week`), durations vs periods vs intervals, `%m+%`/`%m-%`, time zones (`with_tz`, `force_tz`), rounding family |
| `references/forcats-recipes.md` | 90 | reorder family (`fct_reorder`, `fct_relevel`, `fct_inorder`, `fct_infreq`), lump family (`fct_lump_*`), modification (`fct_collapse`, `fct_recode`, `fct_other`, `fct_expand`), missing (`fct_na_value_to_level`) |
| `references/tidyr-reshape.md` | 140 | `pivot_longer`/`pivot_wider` deep dive (`names_pattern`, `names_sep`, `values_fn`, `values_drop_na`), `unnest_longer` vs `unnest_wider`, `hoist`, `separate_wider_*`/`separate_longer_*`, `complete`, `fill`, `expand`, `expand_grid`, `nest(.by =)` |
| `references/data-cleaning-toolkit.md` | 120 | `janitor::clean_names`/`tabyl`/`remove_empty`/`get_dupes`, `naniar::miss_var_summary`/`vis_miss`/`gg_miss_*`, missing-data bias decision tree, when to defer imputation modeling to r-stats / r-tidymodels |
| `references/data-validation.md` | 110 | `pointblank::create_agent`, rule fns, `interrogate()`, `validate` package overview, expectation-style validation in pipelines; explicit boundary: package-introduction questions still route to `r-package-skill-generator` |

Each reference must:

- [ ] Use `|>`, `<-`, `snake_case`, double quotes; target R ≥ 4.1
- [ ] Stay ≤200 lines (hard ceiling)
- [ ] Be linked from `SKILL.md` via `Read \`references/<file>.md\` for ...`
      pointers — never inline-loaded
- [ ] Contain a small "Gotchas" section at the end mirroring the existing
      reference style

### Light edits to existing references

- [ ] `references/dplyr-patterns.md` — add ~15 lines on `nest() + unnest()`
      with list-columns; cross-link to `references/purrr-patterns.md` for
      `map()`-on-nested patterns
- [ ] `references/join-guide.md` — no changes

Net delta: +7 reference files, modest `SKILL.md` edits, no new agents, no new
scripts.

## 4. Routing implications

Update `tests/routing_matrix.json`:

- [ ] Add five trigger entries that all expect `r-data-analysis`: stringr
      (`"extract the domain from these emails with a regex"`), lubridate
      (`"convert UTC timestamps to America/New_York"`), forcats (`"reorder a
      boxplot's factor levels by median"`), purrr (`"apply a fitting routine
      to each nested group and collect coefficients"`), janitor (`"clean
      these ugly column names from a messy CSV"`)
- [ ] Add a pointblank **usage** entry: `"validate that no order has a
      negative amount using pointblank rules"` → `r-data-analysis`, with a
      discriminator distinguishing it from `route-024` (package-introduction)
- [ ] Add a `r-targets` boundary entry: `"orchestrate this cleaning step as a
      target in my pipeline"` → `r-targets` (mirrors the new negative
      boundary)
- [ ] Confirm `route-024` still routes to `r-package-skill-generator`

## 5. Eval implications

Add binary questions to `skills/r-data-analysis/eval.md`:

- [ ] Does the skill use `parse_date_time()` with a format vector when dates
      are mixed-format, never a single `as.Date()` that silently drops values?
- [ ] Does the skill prefer `nest() + map()` (or `across()` where
      appropriate) over a `for` loop for per-group model fitting, returning a
      list-column?
- [ ] For email/URL extraction, does the skill use `stringr::str_extract()`
      with a regex rather than base `strsplit` + indexing?
- [ ] For factor reordering, does the skill use `fct_reorder()` (or related
      forcats) rather than `factor(..., levels = ...)`?
- [ ] For ugly column names from import, does the skill suggest
      `janitor::clean_names()` rather than manual `gsub` / `tolower`?
- [ ] For time-zone-aware timestamps, does the skill distinguish `with_tz()`
      from `force_tz()` and pick the right one for the user's intent?
- [ ] For pipeline data validation, does the skill use `pointblank::create_agent` +
      rule functions + `interrogate()` rather than ad-hoc `stopifnot()`
      chains?

Add prompts:

- [ ] One happy-path prompt per new reference file (7 total)
- [ ] One adversarial prompt that defers correctly: e.g. `"build a validation
      skill from the pointblank GitHub repo"` → must defer to
      `r-package-skill-generator`

## 6. Open questions for the human

1. **pointblank routing collision** — `route-024` currently sends pointblank
   questions to `r-package-skill-generator`. The proposed usage-vs-package-
   introduction discriminator is reasonable but not the only option. OK to
   ship?
2. **Branch directive** — this handoff suggests
   `claude/plan-r-data-analysis-<id>`; the harness pinned planning to
   `claude/review-latest-task-eNKSf`. Re-branch when the implementation
   session begins, or stay?
3. **`glue` package** — proposed home is inside `stringr-recipes.md`. Should
   it instead live in a tiny dedicated reference, or stay folded?
4. **`data.table` boundary** — currently SKILL.md L107–122. Keep there, or
   move to `references/datatable-boundary.md` to free body lines for the new
   sub-blocks?
5. **Frontmatter expansion** — proposal grows description from 513 → ~750
   chars. Acceptable, or hold tighter?
6. **Scripts directory** — `check_join_safety.R` exists. Add new helper
   scripts (e.g. `inspect_missingness.R`, `validate_keys.R`) or keep this
   round documentation-only?

## Verification Checklist

- [ ] `wc -l skills/r-data-analysis/SKILL.md` ≤ 220 (hard cap 300)
- [ ] Each new `references/*.md` ≤ 200 lines
- [ ] No `%>%` introduced anywhere:
      `grep -rn '%>%' skills/ agents/ rules/ --exclude=eval.md`
- [ ] All R code in new content uses `<-`, `|>`, `snake_case`, double quotes
- [ ] Every new reference has a `Read \`references/<file>.md\` for ...` entry
      in `SKILL.md`
- [ ] Frontmatter description ≤ 1024 chars and still starts with `Use when`
- [ ] `tests/routing_matrix.json` parses as valid JSON and new entries follow
      existing schema (`id`, `prompt`, `expected_skill`, `must_not_fire`,
      `discriminator`, `category`)
- [ ] `python tests/run_all.py` passes
- [ ] Manual smoke test: invoke the skill with one prompt per new reference
      and confirm the relevant lazy reference is the one Claude reaches for
