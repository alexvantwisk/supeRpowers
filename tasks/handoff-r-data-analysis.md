# Handoff: Plan work on `r-data-analysis`

## Goal for this session

Produce a written plan (not an implementation) for expanding the
`r-data-analysis` skill. Save the plan to `tasks/plan-r-data-analysis.md`
in the same imperative style as `tasks/plan-1-workflow-commands.md`. Do not
edit the skill itself — that is a follow-up session.

## Why this skill

Among the 22 skills, `r-data-analysis` is one of the most heavily-triggered
(it owns dplyr, tidyr, readr, stringr, forcats, lubridate, purrr workflows)
but is comparatively thin:

- `skills/r-data-analysis/SKILL.md` — 195 lines (cap is 300)
- `skills/r-data-analysis/references/dplyr-patterns.md` — 208 lines
- `skills/r-data-analysis/references/join-guide.md` — 186 lines

The frontmatter advertises seven tidyverse packages, but the references only
cover dplyr depth and joins. There is room — and likely a need — for more.

## Current state to read first

1. `skills/r-data-analysis/SKILL.md` (frontmatter, lazy refs, MCP block, body)
2. `skills/r-data-analysis/references/*.md` (existing depth content)
3. `skills/r-data-analysis/eval.md` (binary eval questions and test prompts —
   tells you what the skill is *supposed* to do)
4. `rules/r-conventions.md` (non-negotiable style rules)
5. `tests/routing_matrix.json` (which prompts route here vs. siblings)
6. `tasks/plan-1-workflow-commands.md` (example of the plan format to imitate)

## Likely gaps worth investigating

Treat these as hypotheses, not a checklist — verify against the SKILL.md body
before recommending any of them:

- `tidyr` reshape patterns: `pivot_longer`/`pivot_wider`, `unnest`, `separate_*`,
  rectangling JSON
- `stringr` + regex recipes (separate from dplyr-patterns)
- `lubridate` date/time arithmetic, time zones, intervals
- `forcats` factor reordering and lumping
- `readr` import: `col_types`, locale, `problems()`, encoding pitfalls
- Data validation handoff (pointblank, validate) — possibly its own reference
- Missing-data handling (`tidyr::drop_na`, `naniar`)
- `janitor` cleaning idioms (`clean_names`, `tabyl`, `remove_empty`)
- `purrr` functional patterns where they overlap with data wrangling
- Tidy-data principles section — currently absent or shallow
- Boundary clarity vs. `r-stats`, `r-performance`, `r-cmd-analysis`,
  `r-tidymodels`, `r-targets`

## Constraints the plan must respect

- SKILL.md hard cap: 300 lines including frontmatter. Push depth to
  `references/`.
- Frontmatter shape: only `name` + `description`; description ≤ 1024 chars
  with "Use when…", 5+ trigger phrases, and negative boundaries to siblings.
- All R code: `|>`, `<-`, snake_case, double quotes, R ≥ 4.1.
- New references must be lazy-loaded via `Read \`references/<file>.md\` for…`
  pointers in SKILL.md.
- Convention checks must still pass: `python tests/run_all.py`.

## Deliverable

`tasks/plan-r-data-analysis.md` containing:

1. Findings — what the skill currently covers, with line counts per section
2. Gaps — concrete missing topics, ordered by triggering frequency
3. Proposed structure — final SKILL.md outline + list of new/expanded
   reference files with target line budgets
4. Routing implications — any new trigger phrases or boundary changes
5. Eval implications — eval.md questions to add or revise
6. Open questions for the human before implementation begins

Keep the plan under ~200 lines. Do not start implementing.

## Branch

This handoff itself is on `main`. The planning session should create a fresh
branch (e.g. `claude/plan-r-data-analysis-<id>`) before writing the plan.
