# r-visualization Skill Upgrade — Design

**Date:** 2026-04-28
**Branch:** `feature/r-visualization-upgrade`
**Worktree:** `.worktrees/r-viz-upgrade`
**Author:** Alexander (with Claude)

---

## 1. Goals & non-goals

**Goals.** Bring `skills/r-visualization/` to current best-practice quality:
comprehensive ggplot2-ecosystem coverage, sharper triggers and boundaries, deep
patchwork composition guidance, and idiomatic recipes for the modern extension
packages most useful for publication-quality and analytical work in R.

**Non-goals.**

- No new domain skills.
- No expansion into Shiny / tables / clinical territory beyond clear handoffs.
- No exotic packages (`ggraph`, `ggalluvial`, `ggcorrplot`, `bayesplot` etc.) —
  they are deferred to a future targeted skill or a "see also" mention.

## 2. Final package set

**Core.** `ggplot2`, `patchwork`, `scales`, `ggrepel`.

**Extensions.** `ggtext`, `ggdist`, `ggridges`, `ggbeeswarm`, `gghighlight`,
`ggforce`, `ggh4x`, `ggsurvfit`.

**Interactive / animation.** `plotly`, `ggiraph`, `gganimate`.

**Palettes.** `ggsci` (Lancet, NEJM, JCO, AAAS, NPG palettes).

**Out-of-skill (boundary handoffs).**

- `gt`, `flextable` → `r-tables`
- `tmap`, `leaflet` → spatial-specific (no skill yet)
- Plots inside Shiny apps → `r-shiny`
- FDA / regulatory KM → `r-clinical`

## 3. File layout

All paths under `skills/r-visualization/`:

```
SKILL.md                              # rewritten, ~280 lines (hard cap 300)
eval.md                               # extended
references/
  ggplot2-layers.md                   # refresh, keep core geom/stat tables
  theme-guide.md                      # refresh + scales/labels merged in
  composition.md                      # NEW — patchwork deep + cowplot brief
  extensions.md                       # NEW — ggtext, ggdist, ggridges,
                                      #        ggbeeswarm, gghighlight, ggforce,
                                      #        ggh4x, ggrepel
  interactivity-and-animation.md      # NEW — plotly vs ggiraph vs gganimate
  domain-and-palettes.md              # NEW — ggsurvfit, ggsci, colorblind
                                      #        palettes, volcano/forest recipes
scripts/
  check_plot_conventions.R            # extended (modest)
```

Reference target: ≤400 lines each, task-oriented headings, lazy-linked from
SKILL.md.

## 4. SKILL.md outline (rewritten)

1. **Frontmatter** — broadened triggers (patchwork, ggdist, ggtext, ggridges,
   beeswarm, raincloud, ridgeline, ggsurvfit, gganimate, ggiraph, journal
   palette) and explicit negative boundaries to `r-shiny`, `r-tables`,
   `r-clinical`, `r-quarto`.
2. **One-paragraph orientation** — grammar of graphics + when to reach for an
   extension package.
3. **Core pipeline cheat sheet** (kept).
4. **Picking the right tool — decision table** *(new)*. "I want X → use package
   Y. See `references/Z.md`." Covers ridgeline, raincloud, beeswarm,
   highlight-subset, markdown-formatted text, nested facets, animated
   transitions, interactive HTML, journal palette swap.
5. **Patchwork composition (essentials)** — `|`, `/`, `plot_layout`,
   `plot_annotation` tag levels, collected guides; pointer to `composition.md`.
6. **Scales & labels (essentials)** — `scales::label_*`,
   `scales::pretty_breaks`, transformations; pointer to `theme-guide.md`.
7. **Colorblind-safe palettes** — kept; ggsci pointer added for journal-themed
   alternatives.
8. **Faceting & non-overlapping labels** — kept; ggh4x and ggrepel pointers.
9. **Publication theme recipe** — kept, refined.
10. **Interactivity** — plotly vs ggiraph one-line decision rule; pointer to
    `interactivity-and-animation.md`.
11. **Animation** — gganimate single recipe + pointer.
12. **Domain plots** — KM (ggsurvfit-first; survminer noted as legacy), forest,
    volcano; pointer to `domain-and-palettes.md`.
13. **Saving figures** — kept, refined.
14. **Verification, gotchas, examples** — kept; gotchas extended (ggsurvfit vs
    survminer; `theme_grey` for publication; `geom_bar(stat="identity")`).
15. **MCP integration block** — kept.

## 5. Reference content (one line each)

- **`composition.md`** — patchwork algebra (`+`, `|`, `/`, `*`), `plot_layout`
  (widths/heights/guides/tag_levels), `inset_element`, `wrap_elements`, common
  multi-panel paper figures. When to reach for cowplot's `plot_grid`,
  `draw_label`, `save_plot` instead.
- **`extensions.md`** — for each of `{ggtext, ggdist, ggridges, ggbeeswarm,
  gghighlight, ggforce, ggh4x, ggrepel}`: *what it solves*, *2–3 idiomatic
  recipes*, *gotcha or interaction with ggplot2*.
- **`interactivity-and-animation.md`** — plotly (`ggplotly` + native `plot_ly`),
  ggiraph (`geom_*_interactive` + `girafe`, when it beats plotly for HTML
  reports), gganimate (`transition_*`, `enter_*`/`exit_*`, `anim_save`),
  decision rules.
- **`domain-and-palettes.md`** — ggsurvfit modern KM + risktable, ggsci journal
  palettes (`scale_color_lancet`, `_nejm`, `_jco`, `_aaas`, `_npg`), colorblind
  palette catalog (Okabe-Ito, viridis variants, ColorBrewer Set2 / Dark2 /
  Paired with safe-for-print notes), volcano and forest recipes.
- **`theme-guide.md`** *(refreshed)* — current element hierarchy + new section
  on `scales::label_*`, `scales::pretty_breaks`, `scales::trans_new`,
  `scales::cut_short_scale`.
- **`ggplot2-layers.md`** *(refreshed)* — corrections, modern
  `linewidth`/`linetype` notes, position adjustments review.

## 6. eval.md additions

**Binary questions (added):**

- Does the skill prefer `ggsurvfit` over `survminer` for new code?
- Does the skill use `scales::label_*` over hand-rolled formatters?
- Does the skill prefer `geom_col()` over `geom_bar(stat = "identity")`?
- Does markdown axis/legend text route through `ggtext`?
- Does the skill route raincloud requests through `ggdist`?
- Does the skill route ridgeline requests through `ggridges`?
- For >100k points, does the skill suggest `geom_hex()` / aggregation rather
  than handing the work to `plotly`?

**Test prompts (added):**

- ggdist raincloud
- ggtext markdown title
- patchwork 2-row paper figure with collected legend
- gghighlight subset
- gganimate transition over time
- ggsurvfit KM with risktable
- ggh4x nested facets
- ggsci NEJM palette swap

**Boundary tests (added):**

- Animated dashboard → `r-shiny`
- Styled gt table with sparklines → `r-tables`
- FDA submission KM → `r-clinical`

## 7. `check_plot_conventions.R` extensions

Add detection for:

- `library(survminer)` without `ggsurvfit` (warn, suggest replacement)
- `geom_bar(stat = "identity")` (suggest `geom_col()`)
- `theme_grey` / `theme_gray` in same file as `ggsave` (warn — likely
  publication context using default theme)

Keep existing checks: `+` at line start, `xlim`/`ylim` zoom, risky palettes,
missing `ggsave` dimensions.

## 8. Routing matrix and tests

`tests/routing_matrix.json` gets new routing rows for these trigger phrases
(non-exhaustive examples):

- "ridgeline plot"
- "raincloud plot"
- "beeswarm"
- "markdown title in plot"
- "highlight a subset"
- "nested facets"
- "animate the plot"
- "interactive ggplot for HTML report"
- "modern KM plot with risk table"

Verification: `python tests/run_all.py` must keep `r-visualization` at 100%
pass. The 9 pre-existing baseline failures (in `r-mcp-setup`, `r-conventions`,
and `r-cmd-*` skills) are out of scope and stay quarantined.

## 9. Decisions and risks

| ID | Type | Note |
|----|------|------|
| D1 | decision | `scales` lives in `theme-guide.md` (new section), not its own file. Rationale: it is mostly axis/legend formatting, conceptually adjacent to theme. |
| D2 | decision | `ggalluvial`, `ggraph`, `ggcorrplot`, `bayesplot` deferred to "see also" mentions only. |
| D3 | decision | `cowplot` is a pointer-only mention inside `composition.md`. `patchwork` is the recommended default. |
| D4 | decision | `ggsurvfit` replaces `survminer` as the recommended modern KM tool. `survminer` kept as a "legacy / known" mention only. Rationale: ggsurvfit is actively maintained, ggplot2-native, and current best practice. |
| R1 | risk | SKILL.md exceeds 300 lines. Mitigation: aggressive lazy-linking, drop redundant prose, decision tables instead of paragraphs. |
| R2 | risk | ggsurvfit examples drift into r-clinical territory. Mitigation: r-visualization owns ggplot2 mechanics; r-clinical owns analytical/regulatory choices. SKILL.md cites this boundary explicitly. |
| R3 | risk | Too many packages, shallow on each. Mitigation: SKILL.md mentions one canonical recipe per package; depth lives in `extensions.md`. |

## 10. Verification (definition of done)

- [ ] SKILL.md ≤ 300 lines, frontmatter passes structural test
- [ ] All reference files ≤ 400 lines
- [ ] `python tests/run_all.py` — r-visualization at 100%; pre-existing 9
      failures unchanged
- [ ] No `%>%` in any new file
      (`grep -rn '%>%' skills/r-visualization/ --exclude=eval.md`)
- [ ] `Rscript skills/r-visualization/scripts/check_plot_conventions.R skills/r-visualization/`
      clean on the skill's own example code
- [ ] All R code examples use `|>`, `<-`, snake_case, double quotes
- [ ] Manual smoke: every reference file is lazy-linked from at least one
      SKILL.md mention; every SKILL.md mention of a package matches a reference

## 11. Out of scope

- Refactor of unrelated skills (no touching `r-shiny`, `r-tables`,
  `r-clinical`, `r-quarto` content).
- Fixing the 9 pre-existing baseline test failures.
- New helper scripts beyond the modest extension to
  `check_plot_conventions.R`.
- Adding `ggalluvial`, `ggraph`, `ggcorrplot`, `bayesplot`, `tmap`, `leaflet`
  beyond brief "see also" mentions.
