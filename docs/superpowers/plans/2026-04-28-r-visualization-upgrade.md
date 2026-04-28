# r-visualization Skill Upgrade — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `skills/r-visualization/` to current best-practice quality with comprehensive ggplot2-ecosystem coverage, sharper triggers/boundaries, deep patchwork composition, and idiomatic recipes for the modern extension packages.

**Architecture:** SKILL.md (≤300 lines) acts as a routing/orientation layer. Depth lives in four new lazy-loaded reference files (`composition.md`, `extensions.md`, `interactivity-and-animation.md`, `domain-and-palettes.md`) plus two refreshed-in-place existing references. The convention checker, eval suite, and routing matrix are extended in lockstep.

**Tech Stack:** Markdown skill content. R example code (ggplot2 ≥3.5, patchwork, scales, ggrepel, ggtext, ggdist, ggridges, ggbeeswarm, gghighlight, ggforce, ggh4x, ggsurvfit, plotly, ggiraph, gganimate, ggsci). Python test runner (`tests/run_all.py`).

**Spec:** `docs/superpowers/specs/2026-04-28-r-visualization-upgrade-design.md`

**Worktree:** `.worktrees/r-viz-upgrade` on branch `feature/r-visualization-upgrade`

**Conventions for ALL R code in this plan:**
- `|>` only, never `%>%`
- `<-` for assignment, never `=` (except in function arguments)
- `snake_case` identifiers
- Double quotes for strings
- Tidyverse-first

---

## File Structure

| Path | Action | Responsibility |
|------|--------|----------------|
| `skills/r-visualization/SKILL.md` | Rewrite | Routing layer; ≤300 lines; lazy-links to references |
| `skills/r-visualization/eval.md` | Extend | Add binary questions, prompts, boundary tests for new packages |
| `skills/r-visualization/references/ggplot2-layers.md` | Refresh in place | Update deprecated `size`→`linewidth` for line geoms; correct examples |
| `skills/r-visualization/references/theme-guide.md` | Refresh + extend | Append "Scales & Labels" section using `scales::label_*` etc. |
| `skills/r-visualization/references/composition.md` | Create | Patchwork deep dive + cowplot pointer |
| `skills/r-visualization/references/extensions.md` | Create | ggtext, ggdist, ggridges, ggbeeswarm, gghighlight, ggforce, ggh4x, ggrepel — recipe per package |
| `skills/r-visualization/references/interactivity-and-animation.md` | Create | plotly, ggiraph, gganimate decision rules + recipes |
| `skills/r-visualization/references/domain-and-palettes.md` | Create | ggsurvfit, ggsci, colorblind palette catalog, volcano/forest |
| `skills/r-visualization/scripts/check_plot_conventions.R` | Extend | Add survminer / `geom_bar(stat="identity")` / `theme_grey`+`ggsave` checks |
| `tests/routing_matrix.json` | Extend | Add new trigger phrases for r-visualization |

All reference files target ≤400 lines. SKILL.md hard cap 300 lines.

---

## Task 1: Baseline snapshot and pre-flight

**Files:**
- Read-only: existing `skills/r-visualization/` tree
- Read-only: `tests/run_all.py`, `tests/routing_matrix.json`

**Why:** Capture starting state so later verification can compare. Confirm worktree is on the right branch.

- [ ] **Step 1: Confirm worktree branch**

Run from worktree root:

```bash
git rev-parse --abbrev-ref HEAD
```

Expected: `feature/r-visualization-upgrade`

- [ ] **Step 2: Snapshot current line counts**

```bash
wc -l skills/r-visualization/SKILL.md \
      skills/r-visualization/eval.md \
      skills/r-visualization/references/*.md \
      skills/r-visualization/scripts/*.R
```

Note the current values for later comparison. Expected approximate values:
- `SKILL.md` ≈ 260 lines
- `eval.md` ≈ 35 lines
- `references/ggplot2-layers.md` ≈ 375 lines
- `references/theme-guide.md` ≈ 388 lines

- [ ] **Step 3: Run baseline test suite and capture failures**

```bash
python tests/run_all.py 2>&1 | tail -10
```

Expected: 9 pre-existing failures, NONE in r-visualization. Confirm via:

```bash
python tests/run_all.py 2>&1 | grep -E "FAIL.*r-visualization" || echo "no r-visualization failures"
```

Expected: `no r-visualization failures`

- [ ] **Step 4: Verify no `%>%` exists in r-visualization (excluding eval.md)**

```bash
grep -rn '%>%' skills/r-visualization/ --exclude=eval.md || echo "clean"
```

Expected: `clean`

- [ ] **Step 5: No commit. This is observation only.**

---

## Task 2: Refresh `references/ggplot2-layers.md` in place

**Files:**
- Modify: `skills/r-visualization/references/ggplot2-layers.md`

**Why:** Existing file is structurally fine. Update only deprecated APIs (most importantly the ggplot2 ≥3.4 transition where line geoms moved from `size` to `linewidth`).

- [ ] **Step 1: Read the current file end-to-end**

```bash
wc -l skills/r-visualization/references/ggplot2-layers.md
```

Read it fully. Note any places that:
1. Use `size` for line/path/segment/abline/hline/vline/smooth/contour geoms (these should be `linewidth`)
2. Use `size` in `geom_errorbar`, `geom_errorbarh`, `geom_linerange`, `geom_pointrange` for the line component (should be `linewidth`)
3. Reference `aes_string()` (deprecated; should use `.data[[var]]`)
4. Use `qplot()` (deprecated; remove)

- [ ] **Step 2: Replace `size` → `linewidth` for line-style geoms**

For each occurrence in this file where `size = X` is set on a geom that draws a line (geom_line, geom_path, geom_segment, geom_abline/hline/vline, geom_smooth, geom_errorbar*, geom_linerange, geom_pointrange, geom_contour, geom_step, geom_density, geom_freqpoly, geom_curve, geom_function), change to `linewidth = X`.

For `geom_point` keep `size`. For `geom_text`/`geom_label` keep `size`. For `aes(size = ...)` mappings on points, keep.

- [ ] **Step 3: Remove or rewrite any `aes_string` / `qplot` examples**

Replace `aes_string("var")` with `aes(.data[["var"]])`. Delete any lone `qplot()` examples.

- [ ] **Step 4: Add a brief "API conventions (ggplot2 ≥3.4)" callout near the top**

Insert after the existing intro:

```markdown
## API conventions (ggplot2 ≥3.4)

- Line geoms use `linewidth = X`, not `size = X`. `size` controls only point /
  text radius now.
- Prefer `.data[[var]]` over `aes_string()` for programmatic aesthetic mapping.
- `qplot()` is deprecated; use full `ggplot() + geom_*()` calls.
```

- [ ] **Step 5: Verify line count is still ≤400 and file passes structural test**

```bash
wc -l skills/r-visualization/references/ggplot2-layers.md
python tests/run_all.py 2>&1 | grep -E "FAIL.*r-visualization" || echo "still clean"
```

Expected: `still clean`, line count ≤400.

- [ ] **Step 6: Commit**

```bash
git add skills/r-visualization/references/ggplot2-layers.md
git commit -m "refactor: refresh ggplot2-layers.md to ggplot2 >=3.4 API"
```

---

## Task 3: Refresh `references/theme-guide.md` and append "Scales & Labels"

**Files:**
- Modify: `skills/r-visualization/references/theme-guide.md`

**Why:** Theme guide is fine. Add a new section so the SKILL.md "Scales & labels (essentials)" pointer has a target.

- [ ] **Step 1: Read the current file end-to-end and apply the same `size`→`linewidth` corrections** described in Task 2 Steps 1–3, scoped to this file.

- [ ] **Step 2: Append a new top-level section at end of file**

Add the following section AFTER all existing content (before any final empty line):

````markdown
---

## Scales and Labels with `scales`

The `scales` package (a ggplot2 dependency) supplies axis/legend formatters,
breaks helpers, and transformations. Prefer these over hand-rolled functions.

### Common label formatters

```r
library(scales)

scale_y_continuous(labels = label_comma())            # 1,234,567
scale_y_continuous(labels = label_dollar())           # $1,234
scale_y_continuous(labels = label_percent())          # 12.3%
scale_y_continuous(labels = label_number(scale_cut = cut_short_scale()))
                                                       # 1.2K, 3.4M, 5.6B
scale_x_date(labels = label_date_short())             # Jan 2024
scale_x_log10(labels = label_log())                   # 10^1, 10^2
scale_y_continuous(labels = label_bytes())            # 1.2 MB
scale_y_continuous(labels = label_pvalue())           # p < 0.001
```

### Breaks helpers

```r
scale_x_continuous(breaks = pretty_breaks(n = 6))
scale_x_continuous(breaks = breaks_extended(n = 8))
scale_x_log10(breaks = breaks_log())
scale_x_date(breaks = breaks_pretty(6))
```

### Transformations

```r
scale_y_continuous(trans = "log10")
scale_y_continuous(trans = scales::pseudo_log_trans(base = 10))   # handles 0
scale_y_continuous(trans = scales::sqrt_trans())
```

For a custom transformation use `scales::trans_new(name, transform, inverse,
breaks, format)`.

### Why `scales::label_*` over `formatC` / `sprintf`

- Vectorised and ggplot2-aware.
- Locale-aware (`big.mark`, `decimal.mark`).
- Composes: `label_number(prefix = "USD ", suffix = "/mo")`.
- Cuts (`cut_short_scale`, `cut_si`, `cut_long_scale`) handle order-of-magnitude
  switches without manual branching.
````

- [ ] **Step 3: Verify line count**

```bash
wc -l skills/r-visualization/references/theme-guide.md
```

Expected: ≤400.

- [ ] **Step 4: Verify no `%>%` and no `=` assignment in new content**

```bash
grep -n '%>%' skills/r-visualization/references/theme-guide.md || echo "no %>%"
```

Expected: `no %>%`

- [ ] **Step 5: Commit**

```bash
git add skills/r-visualization/references/theme-guide.md
git commit -m "docs(r-viz): add scales/labels section to theme-guide reference"
```

---

## Task 4: Create `references/composition.md`

**Files:**
- Create: `skills/r-visualization/references/composition.md`

**Why:** Patchwork is the central composition tool for paper figures. SKILL.md needs a deep target. cowplot is the legacy alternative — single-paragraph pointer only.

- [ ] **Step 1: Write the file**

Target ≤400 lines. Use the structure below. Replace `# ...` placeholders with concrete content per the inline guidance.

```markdown
# Multi-Panel Composition

Compose multiple plots into paper-quality figures with `patchwork`. For most
work, patchwork is the only composition tool you need; `cowplot` is mentioned
at the end for legacy interop.

---

## Patchwork algebra

```r
library(patchwork)

p1 + p2                  # side by side, single row
p1 | p2                  # explicit horizontal (synonym for + at top level)
p1 / p2                  # stacked, top over bottom
(p1 | p2) / p3           # parenthesised: top row, bottom full-width
p1 + p2 + p3 + p4 +
  plot_layout(ncol = 2)  # 2x2 grid
```

Operator precedence: `/` binds tighter than `|`. Use parentheses freely; they
are normal R grouping, not patchwork-specific.

---

## `plot_layout()` — the workhorse

```r
(p1 | p2) / p3 +
  plot_layout(
    ncol    = 2,
    widths  = c(2, 1),         # left twice as wide as right
    heights = c(1, 1.5),       # bottom 1.5x top
    guides  = "collect"        # merge all legends into one
  )
```

`guides = "collect"` is the most common quality lift for paper figures: a
single shared legend instead of one per panel. Pair it with
`& theme(legend.position = "bottom")` (note the `&`, see below) to put the
shared legend below the whole composition.

---

## `&` vs `+` — applying themes to the composition

- `+` adds to the **last** plot in the chain.
- `&` adds to **every** plot in the composition.

```r
(p1 | p2) / p3 &
  theme_minimal(base_size = 11) &
  theme(legend.position = "bottom")
```

Use `&` for composition-wide theming. Use `+` to tweak only the most recently
added plot.

---

## Annotation and tags

```r
(p1 | p2) / p3 +
  plot_annotation(
    title    = "Figure 2. Cohort outcomes by treatment",
    subtitle = "n = 1,247",
    caption  = "Error bars: 95% CI",
    tag_levels = "A"          # A, B, C ...; or list("A", "1") for nested
  )
```

For Greek-letter or boxed tags:

```r
plot_annotation(tag_levels = "A", tag_prefix = "(", tag_suffix = ")")
```

---

## `inset_element()` — small plots inside big plots

```r
p_main +
  inset_element(p_zoom,
                left   = 0.6,  bottom = 0.05,
                right  = 0.98, top    = 0.45)
```

Coordinates are 0–1 fractions of the panel. Use this instead of building a
manual viewport with `grid`.

---

## `wrap_elements()` — embed non-ggplot objects

For tables, base-R plots, or pre-rendered grobs:

```r
wrap_elements(grid::textGrob("Note: …")) /
  (p1 | p2)
```

---

## Common paper-figure patterns

### Top scatter, bottom marginal density

```r
p_scatter <- ggplot(d, aes(x, y)) + geom_point() + theme_minimal()
p_density <- ggplot(d, aes(x))    + geom_density() + theme_void()

p_density / p_scatter +
  plot_layout(heights = c(1, 4))
```

### Two-row figure with shared legend

```r
top    <- (p1 | p2 | p3)
bottom <- (p4 | p5)

(top / bottom) +
  plot_layout(guides = "collect", heights = c(1, 1)) &
  theme(legend.position = "bottom")
```

### Large central plot + two stacked sidekicks

```r
p_main + (p_a / p_b) +
  plot_layout(widths = c(3, 1))
```

---

## Saving compositions

`ggsave()` saves the last printed plot, so either assign and pass:

```r
fig <- (p1 | p2) / p3 + plot_layout(guides = "collect")
ggsave("figure-2.pdf", fig, width = 180, height = 120,
       units = "mm", device = cairo_pdf)
```

For very wide compositions, set width to 2x panel width plus margin:
journals typically allow 89 mm (single col) or 183 mm (double col).

---

## When to reach for cowplot instead

`cowplot` is mature, ggplot2-aware, and predates patchwork. Reach for it only
when you need:

- `cowplot::plot_grid()` with mixed grob types and fine-grained `align = "v"` /
  `align = "h"` axis alignment that patchwork's `plot_layout` cannot produce.
- `cowplot::draw_label()` / `cowplot::draw_image()` for absolute-positioned
  annotations or images on top of an arbitrary canvas.
- `cowplot::save_plot()` if a colleague's pipeline already uses it (it is a
  thin wrapper around `ggsave`; either works).

Otherwise: patchwork. Do not mix the two within a single figure — guide
collection and tag inheritance behave differently.

---

## Gotchas

| Trap | Why | Fix |
|------|-----|-----|
| Theme applied with `+` only changes last panel | `+` targets last expression | Use `&` for composition-wide theme |
| Legends differ slightly across panels and won't collect | `guides = "collect"` requires identical scales | Make scales explicit with `scale_*_manual(values = …)` shared across plots |
| Tag letters out of order after rearranging | `tag_levels` walks current layout left-to-right, top-to-bottom | Restate `plot_annotation(tag_levels = "A")` after layout changes |
| `inset_element` clipped at panel edge | `clip = "on"` by default | `inset_element(..., clip = "off")` or `on_top = TRUE` |
| Saved figure has tiny text | Composition base size scales with panel count | Set `base_size` in `theme_*()` applied via `&` |
```

- [ ] **Step 2: Verify line count and conventions**

```bash
wc -l skills/r-visualization/references/composition.md
grep -n '%>%' skills/r-visualization/references/composition.md || echo "no %>%"
```

Expected: ≤400 lines, `no %>%`.

- [ ] **Step 3: Commit**

```bash
git add skills/r-visualization/references/composition.md
git commit -m "docs(r-viz): add composition.md reference for patchwork"
```

---

## Task 5: Create `references/extensions.md`

**Files:**
- Create: `skills/r-visualization/references/extensions.md`

**Why:** Eight extension packages, one canonical recipe each. Task-oriented, lazy-loaded depth.

- [ ] **Step 1: Write the file with the structure below**

Target ≤400 lines. For each package: *what it solves* (1-2 sentences), *idiomatic recipe* (1-2 code blocks), *gotcha*.

```markdown
# ggplot2 Extension Packages

Task-oriented reference. Each section: when to use it, the canonical recipe,
and the gotcha that bites first-time users.

Extension packages reach for ggplot2 hooks not exposed by the core API. They
compose with `+` like any layer.

---

## `ggrepel` — non-overlapping text labels

**Use when:** scatter or point plot has overlapping `geom_text` / `geom_label`.

```r
library(ggrepel)

ggplot(mtcars, aes(wt, mpg, label = rownames(mtcars))) +
  geom_point() +
  geom_text_repel(
    max.overlaps = 15,
    box.padding  = 0.4,
    seed         = 42
  )
```

**Gotcha:** different `seed` produces different label positions. Always set a
seed for reproducible figures. `max.overlaps = Inf` will draw every label
even if illegible — prefer a finite cap.

---

## `ggtext` — markdown / HTML in text elements

**Use when:** axis labels, titles, legends, or facet strips need bold, italic,
colored, or super/subscripted text.

```r
library(ggtext)

ggplot(d, aes(x, y)) +
  geom_point() +
  labs(
    title = "Effect of *treatment* on **outcome**",
    x     = "Dose (mg kg<sup>-1</sup>)",
    y     = "Response (Δ from baseline)"
  ) +
  theme(
    plot.title = element_markdown(),
    axis.title = element_markdown()
  )
```

For per-category colored axis text:

```r
ggplot(d, aes(group, value)) +
  geom_col(aes(fill = group)) +
  scale_x_discrete(labels = c(
    A = "<span style='color:#E69F00'>**A**</span>",
    B = "<span style='color:#56B4E9'>**B**</span>"
  )) +
  theme(axis.text.x = element_markdown())
```

**Gotcha:** must set the matching `element_markdown()` on every text element
that uses markdown. Missing one shows the raw HTML.

---

## `ggdist` — distributional and uncertainty visualizations

**Use when:** showing a distribution (raincloud, halfeye, intervals) instead of
just summary stats.

```r
library(ggdist)

# Raincloud: half-eye + boxplot + dots
ggplot(iris, aes(x = Species, y = Sepal.Length, fill = Species)) +
  stat_halfeye(adjust = .5, justification = -.2, .width = 0,
               point_colour = NA) +
  geom_boxplot(width = .12, outlier.shape = NA) +
  stat_dots(side = "left", justification = 1.1,
            binwidth = .05, dotsize = .5) +
  scale_fill_viridis_d() +
  coord_flip() +
  theme_minimal()
```

For posterior intervals:

```r
stat_interval(aes(y = estimate))
stat_pointinterval(.width = c(.5, .95))
```

**Gotcha:** `stat_halfeye` density is normalized per group, not per panel.
Use `normalize = "panels"` for cross-group comparison.

---

## `ggridges` — ridgeline plots

**Use when:** comparing many distributions stacked vertically.

```r
library(ggridges)

ggplot(diamonds, aes(x = price, y = cut, fill = cut)) +
  geom_density_ridges(scale = 1.2, alpha = .8, rel_min_height = .01) +
  scale_x_continuous(labels = scales::label_dollar()) +
  scale_fill_viridis_d(guide = "none") +
  theme_minimal()
```

For ridgeline gradient fills:

```r
geom_density_ridges_gradient(aes(fill = stat(x)), scale = 1.2) +
  scale_fill_viridis_c()
```

**Gotcha:** `scale > 1` causes ridges to overlap (often desired). `scale = 1`
makes ridges just touch. `rel_min_height` cuts the long tails.

---

## `ggbeeswarm` — beeswarm and quasirandom plots

**Use when:** many points per category and you want every point visible without
the artificial structure of `position_jitter`.

```r
library(ggbeeswarm)

ggplot(iris, aes(Species, Sepal.Length, color = Species)) +
  geom_quasirandom(method = "smiley", width = .25) +
  scale_color_viridis_d(guide = "none") +
  theme_minimal()
```

Methods: `"quasirandom"` (default), `"pseudorandom"`, `"smiley"`,
`"frowney"`, `"minout"`, `"tukey"`. Use `geom_beeswarm()` when categorical
spacing matters more than density preservation.

**Gotcha:** with very large n (>5,000 per group) beeswarm becomes slow and
visually noisy — switch to `geom_violin()` or `ggdist::stat_halfeye()`.

---

## `gghighlight` — auto-highlighting subsets

**Use when:** you have many lines/points and want one or two to stand out
without manually filtering and re-plotting.

```r
library(gghighlight)

ggplot(d, aes(year, value, color = country, group = country)) +
  geom_line() +
  gghighlight(max(value) > 100, label_key = country) +
  theme_minimal()
```

The unhighlighted series are kept in faint grey for context, and labels are
auto-placed on the highlighted ones.

**Gotcha:** `gghighlight` consumes the `color` aesthetic for the
highlight/grey distinction. If you want to color-code highlighted series by
something else, set `use_direct_label = FALSE` and add a separate
`scale_color_*()` for the highlighted set.

---

## `ggforce` — extra geoms and panel utilities

**Use when:** sina plots, parallel sets / alluvial flows (within ggplot2),
zoom-into-a-region facets, or marking specific regions.

```r
library(ggforce)

# Sina plot: violin shape from points
ggplot(iris, aes(Species, Sepal.Length, color = Species)) +
  geom_sina(maxwidth = .6) +
  theme_minimal()

# Zoom into a region with linked panel
ggplot(mtcars, aes(wt, mpg)) +
  geom_point() +
  facet_zoom(xlim = c(2.5, 3.5))

# Highlight a region
geom_mark_rect(aes(filter = group == "target", label = "Target zone"))
```

Other useful ggforce functions: `geom_arc_bar`, `geom_parallel_sets`,
`geom_link`, `geom_circle`, `geom_voronoi_tile`.

**Gotcha:** `facet_zoom` requires linked panels and does not compose with
`patchwork` in the obvious way — keep zoom plots standalone.

---

## `ggh4x` — nested facets and advanced strips/guides

**Use when:** you have a 2-level grouping (e.g., Region > Country) and
`facet_grid` collapses it; or you need different scales per panel that
`scales = "free"` cannot express.

```r
library(ggh4x)

# Nested strip: Region groups Country
ggplot(d, aes(x, y)) +
  geom_point() +
  facet_nested(~ region + country)

# Per-panel scale specification
facetted_pos_scales(
  y = list(
    scale_y_log10(),
    scale_y_continuous(limits = c(0, 100))
  )
)

# Truncated axes (clean Tufte-style)
guides(x = "axis_truncated", y = "axis_truncated")
```

**Gotcha:** `facet_nested` does not interact cleanly with `coord_flip`. Use
`facet_nested_wrap` if you need flipping.

---

## When to use which

| You want… | Reach for |
|-----------|-----------|
| Distribution per group, expressive | `ggdist::stat_halfeye` (or raincloud) |
| Stacked distributions over many groups | `ggridges` |
| Every point visible per category | `ggbeeswarm::geom_quasirandom` |
| One or two series to pop out of many | `gghighlight` |
| Markdown / colored / sub-super in text | `ggtext` |
| Non-overlapping text labels | `ggrepel` |
| Sina, zoom, parallel sets, region marks | `ggforce` |
| Nested facets, per-panel scales, truncated axes | `ggh4x` |
```

- [ ] **Step 2: Verify**

```bash
wc -l skills/r-visualization/references/extensions.md
grep -n '%>%' skills/r-visualization/references/extensions.md || echo "no %>%"
```

Expected: ≤400 lines, `no %>%`.

- [ ] **Step 3: Commit**

```bash
git add skills/r-visualization/references/extensions.md
git commit -m "docs(r-viz): add extensions.md reference covering 8 ggplot2 extensions"
```

---

## Task 6: Create `references/interactivity-and-animation.md`

**Files:**
- Create: `skills/r-visualization/references/interactivity-and-animation.md`

**Why:** Three packages with overlapping use cases. The decision rule matters more than any single recipe.

- [ ] **Step 1: Write the file**

Target ≤350 lines.

```markdown
# Interactivity and Animation

Three packages, three jobs.

| Package | Output | When to use |
|---------|--------|-------------|
| `plotly` | HTML widget (htmlwidgets) | Standalone interactive plot, 3D, linked brushing, 100k+ points with WebGL |
| `ggiraph` | SVG with JS interactions | Static-feel HTML report or PDF (interactivity degrades gracefully); smaller files than plotly |
| `gganimate` | GIF / MP4 | Time-evolving or transition-based explanatory plots |

For plots inside Shiny, use **r-shiny** instead.

---

## Decision rule (pick one)

- Need 3D or linked brushing across plots? → `plotly` native (`plot_ly`)
- Have a finished `ggplot` and want hover tooltips for an HTML report? → `ggiraph`
  (smaller, faster, more elegant typography)
- Want hover + zoom + pan + crosstalk on the same ggplot? → `plotly::ggplotly`
- Have time/grouping you want to animate? → `gganimate`
- Need to embed in a Quarto/R Markdown HTML and care about page weight? → `ggiraph`
- Need to embed in a static PDF or print? → none. Keep it static.

---

## `plotly`

### `ggplotly` — convert any ggplot

```r
library(plotly)

p <- ggplot(d, aes(x, y, color = group, text = label)) +
  geom_point(size = 3)

ggplotly(p, tooltip = c("text", "x", "y"))
```

`tooltip` accepts column names from the ggplot mapping.

### Native `plot_ly` — when ggplotly isn't enough

```r
plot_ly(d, x = ~x, y = ~y, z = ~z, color = ~group,
        type = "scatter3d", mode = "markers")

# WebGL for >100k points
plot_ly(d, x = ~x, y = ~y, type = "scattergl", mode = "markers")
```

### Gotchas

- `ggplotly` does not preserve every ggplot extension — `ggtext`, custom legend
  titles, and complex theme tweaks may render incorrectly. Test before
  shipping.
- HTML output can be 1–5 MB per plot — use `ggiraph` for lighter reports.
- `ggplotly(p, tooltip = "text")` only shows columns named in `aes(text = …)`;
  add a `text =` aesthetic with the formatted hover string you actually want.

---

## `ggiraph`

### Recipe — interactive scatter for an HTML report

```r
library(ggiraph)

p <- ggplot(d, aes(x, y, tooltip = paste0(name, ": ", value),
                   data_id = name)) +
  geom_point_interactive(size = 3) +
  theme_minimal()

girafe(ggobj = p, width_svg = 6, height_svg = 4,
       options = list(
         opts_hover(css = "fill:#D55E00;stroke:black;"),
         opts_tooltip(opacity = .9)
       ))
```

Most ggiraph geoms mirror a ggplot2 geom: `geom_*_interactive`. They accept
two extra aesthetics:

- `tooltip` — text shown on hover
- `data_id` — links elements across panels (linked brushing)

### Why pick ggiraph over plotly

- SVG output is small and crisp at any zoom.
- Plays well with `patchwork` — interactivity survives composition.
- Tooltips can contain HTML, including `ggtext`-style markup.

### Gotcha

- Interactivity is JS-injected into the SVG. If embedded in a context that
  strips scripts (some email clients, GitHub READMEs) the tooltips disappear
  but the static SVG remains valid. This is a feature, not a bug.

---

## `gganimate`

### Recipe — animate over time

```r
library(gganimate)

p <- ggplot(d, aes(x, y, color = group)) +
  geom_point(size = 3) +
  transition_time(year) +
  labs(title = "Year: {frame_time}") +
  ease_aes("linear")

anim <- animate(p, fps = 20, duration = 8,
                width = 800, height = 600,
                renderer = gifski_renderer())
anim_save("trend.gif", animation = anim)
```

### Recipe — transition between states

```r
ggplot(d, aes(group, value, fill = group)) +
  geom_col() +
  transition_states(stage, transition_length = 1, state_length = 2) +
  enter_fade() + exit_shrink()
```

### Common transitions

| Function | Use for |
|----------|---------|
| `transition_time(t)` | continuous time variable |
| `transition_states(s)` | discrete steps / stages |
| `transition_reveal(t)` | reveal a line over time, keep prior segments |
| `transition_filter()` | cycle through data subsets |

### Gotchas

- Renders are slow. Develop with a small `nframes` (e.g. 30) and bump up only
  for the final export.
- `gifski_renderer()` requires the `gifski` system library. For `mp4`, use
  `av_renderer()` (requires `av` package + ffmpeg).
- Save with `anim_save()`, not `ggsave()`. `ggsave` only handles static plots.
```

- [ ] **Step 2: Verify**

```bash
wc -l skills/r-visualization/references/interactivity-and-animation.md
grep -n '%>%' skills/r-visualization/references/interactivity-and-animation.md || echo "no %>%"
```

Expected: ≤350 lines, `no %>%`.

- [ ] **Step 3: Commit**

```bash
git add skills/r-visualization/references/interactivity-and-animation.md
git commit -m "docs(r-viz): add interactivity-and-animation reference"
```

---

## Task 7: Create `references/domain-and-palettes.md`

**Files:**
- Create: `skills/r-visualization/references/domain-and-palettes.md`

**Why:** Modern KM (ggsurvfit), journal palettes (ggsci), the colorblind palette catalog, plus the canonical volcano and forest recipes.

- [ ] **Step 1: Write the file**

Target ≤400 lines.

```markdown
# Domain Plots and Palettes

Domain-specific recipes (KM, volcano, forest) and the curated palette catalog
this skill recommends.

> r-visualization owns the **plotting mechanics**. For regulatory or
> trial-specific KM (stratified bands, FDA submission formatting, endpoint
> definitions), defer to **r-clinical**.

---

## Kaplan-Meier with `ggsurvfit` (modern, recommended)

`ggsurvfit` is the actively-maintained, ggplot2-native KM tool. Prefer it over
`survminer` for new code.

```r
library(survival)
library(ggsurvfit)

fit <- survfit2(Surv(time, status) ~ treatment, data = clinical_data)

fit |>
  ggsurvfit(linewidth = 1) +
  add_confidence_interval() +
  add_risktable(
    risktable_stats = c("n.risk", "n.event"),
    stats_label = list(n.risk = "At risk", n.event = "Events")
  ) +
  add_pvalue(caption = "Log-rank {p.value}") +
  scale_color_manual(values = c("#E69F00", "#56B4E9")) +
  scale_y_continuous(labels = scales::label_percent(),
                     limits = c(0, 1)) +
  labs(x = "Months from randomization", y = "Overall survival") +
  theme_ggsurvfit_default()
```

**Why ggsurvfit over survminer:**

- ggplot2-native: composes with `+`, themes, scales, patchwork.
- Active maintenance; survminer is in low-activity mode.
- Risktable is a layer (`add_risktable`) instead of a separate object glued
  with `cowplot::plot_grid`.

**Survminer is acceptable** if you are extending an existing pipeline that
uses it; do not introduce it for new work.

---

## Volcano plot (differential expression / two-group comparison)

```r
de_results |>
  dplyr::mutate(
    sig = dplyr::case_when(
      adj_p_val < 0.05 & log2fc >  1 ~ "Up",
      adj_p_val < 0.05 & log2fc < -1 ~ "Down",
      TRUE ~ "NS"
    )
  ) |>
  ggplot(aes(log2fc, -log10(adj_p_val), color = sig)) +
  geom_point(alpha = 0.6, size = 1.5) +
  scale_color_manual(
    values = c(NS = "grey70", Up = "#D55E00", Down = "#0072B2"),
    name   = NULL
  ) +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed",
             color = "grey50") +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed",
             color = "grey50") +
  ggrepel::geom_text_repel(
    data = \(d) dplyr::slice_max(d, abs(log2fc), n = 10),
    aes(label = gene), seed = 42, max.overlaps = 15
  ) +
  labs(x = expression(log[2]~"fold change"),
       y = expression(-log[10]~"adjusted p-value")) +
  theme_minimal()
```

---

## Forest plot (meta-analysis / regression coefficients)

```r
forest_data |>
  ggplot(aes(estimate, reorder(study, estimate))) +
  geom_vline(xintercept = 1, linetype = "dashed", color = "grey50") +
  geom_errorbarh(aes(xmin = ci_lower, xmax = ci_upper),
                 height = 0.2, linewidth = 0.5) +
  geom_point(size = 3, shape = 15) +
  scale_x_log10(breaks = c(0.25, 0.5, 1, 2, 4),
                labels = scales::label_number(accuracy = 0.01)) +
  labs(x = "Odds Ratio (95% CI)", y = NULL) +
  theme_minimal() +
  theme(panel.grid.minor.x = element_blank())
```

For RR / HR plots, swap axis labels and reference line as needed.

---

## Colorblind-safe palette catalog

Always prefer one of these for published figures.

### Okabe-Ito (8 categories, gold standard)

```r
okabe_ito <- c("#E69F00", "#56B4E9", "#009E73", "#F0E442",
               "#0072B2", "#D55E00", "#CC79A7", "#999999")
scale_color_manual(values = okabe_ito)
```

Order matters: the first six are designed to be safely paired in any
combination. Keep `#999999` (grey) for "other / not significant".

### viridis (continuous, perceptually uniform)

```r
scale_color_viridis_c(option = "viridis")   # default
scale_color_viridis_c(option = "magma")     # darker low end
scale_color_viridis_c(option = "plasma")
scale_color_viridis_c(option = "cividis")   # explicitly colorblind-tested
scale_color_viridis_d()                      # discrete variant
```

`cividis` is the safest choice when in doubt; designed to be perceptually
identical for trichromat and dichromat viewers.

### ColorBrewer (qualitative)

```r
scale_color_brewer(palette = "Set2")    # 8 colors, soft, colorblind-safe
scale_color_brewer(palette = "Dark2")   # 8 colors, saturated
scale_color_brewer(palette = "Paired")  # 12 colors, paired pastel/saturated
```

`Set1` is **not** colorblind-safe (red/green collision); avoid.

### Sequential and diverging

```r
scale_fill_distiller(palette = "Blues",  direction = 1)        # sequential
scale_fill_distiller(palette = "RdBu",   direction = 1)        # diverging
scale_fill_gradient2(low = "#0072B2", mid = "white",
                     high = "#D55E00", midpoint = 0)
```

---

## Journal-themed palettes — `ggsci`

For figures destined for specific journals.

```r
library(ggsci)

scale_color_lancet()
scale_color_nejm()
scale_color_jco()      # Journal of Clinical Oncology
scale_color_aaas()     # Science (AAAS)
scale_color_npg()      # Nature Publishing Group
scale_color_jama()
scale_fill_lancet()    # corresponding fill scales
```

ggsci palettes are not always colorblind-safe (the Lancet palette has a
red/green pair). Verify with `colorblindr::cvd_grid()` before final
submission.

---

## Verification

```r
library(colorblindr)
cvd_grid(p)   # renders deuteranopia/protanopia/tritanopia/desaturated
```

If categories collapse in any panel, swap to Okabe-Ito or cividis.
```

- [ ] **Step 2: Verify**

```bash
wc -l skills/r-visualization/references/domain-and-palettes.md
grep -n '%>%' skills/r-visualization/references/domain-and-palettes.md || echo "no %>%"
```

Expected: ≤400 lines, `no %>%`.

- [ ] **Step 3: Commit**

```bash
git add skills/r-visualization/references/domain-and-palettes.md
git commit -m "docs(r-viz): add domain-and-palettes reference (KM, volcano, forest, palettes)"
```

---

## Task 8: Rewrite `SKILL.md`

**Files:**
- Modify (rewrite): `skills/r-visualization/SKILL.md`

**Why:** SKILL.md is now a routing/orientation layer. Depth lives in references created in Tasks 4–7.

- [ ] **Step 1: Write the new SKILL.md**

Hard cap: 300 lines including frontmatter. Target ~280.

```markdown
---
name: r-visualization
description: >
  Use when creating plots, charts, figures, or visualizations in R with
  ggplot2 and its ecosystem (patchwork, scales, ggrepel, ggtext, ggdist,
  ggridges, ggbeeswarm, gghighlight, ggforce, ggh4x, ggsurvfit, ggsci) or
  with plotly / ggiraph / gganimate. Provides expert guidance on the grammar
  of graphics, publication-quality figures, multi-panel composition,
  domain-specific plots (KM, volcano, forest), colorblind-safe palettes,
  theming, and interactive / animated visualization.
  Triggers: ggplot2, plot, chart, visualization, figure, plotly, htmlwidgets,
  histogram, scatter, bar chart, heatmap, boxplot, violin, raincloud,
  ridgeline, beeswarm, sina, publication figure, facet, nested facet, theme,
  patchwork, multi-panel, composed figure, ggrepel, ggtext, markdown title,
  ggdist, ggridges, ggbeeswarm, gghighlight, ggforce, ggh4x, ggsurvfit,
  Kaplan-Meier, KM curve, risk table, volcano plot, forest plot, ggsci,
  Lancet palette, NEJM palette, colorblind, ggiraph, interactive ggplot,
  gganimate, animated plot.
  Do NOT use for interactive Shiny dashboards — use r-shiny instead.
  Do NOT use for formatted data tables — use r-tables instead.
  Do NOT use for FDA / regulatory survival analysis — use r-clinical for
  the analytical layer (this skill may help with the ggplot mechanics).
  Do NOT use for Quarto/RMarkdown report layout — use r-quarto instead.
---

# R Visualization

Build publication-quality visualizations in R using the ggplot2 grammar of
graphics, with curated extensions for composition, theming, statistics,
domain-specific plots, interactivity, and animation.

**Core pipeline:** `ggplot()` + `aes()` -> geom layers -> scales -> coords -> facets -> theme

**Agent dispatch:** Dispatch to **r-code-reviewer** for complex multi-panel
figure review.

**MCP integration (when R session available):**
- Before writing ggplot code: `btw_tool_env_describe_data_frame` to check
  variable types and choose appropriate geoms (continuous vs discrete vs date)
- When uncertain about a geom, scale, or extension function:
  `btw_tool_docs_help_page` to read current argument signatures

---

## Picking the right tool

| You want… | Use | See |
|-----------|-----|-----|
| Standard scatter / bar / line / box | `ggplot2` core geoms | `references/ggplot2-layers.md` |
| Multi-panel composed figure | `patchwork` | `references/composition.md` |
| Axis label formatters (currency, %, dates) | `scales::label_*` | `references/theme-guide.md` |
| Non-overlapping text labels | `ggrepel` | `references/extensions.md` |
| Markdown / HTML in titles or labels | `ggtext` | `references/extensions.md` |
| Raincloud, halfeye, posterior intervals | `ggdist` | `references/extensions.md` |
| Stacked density (ridgeline) plots | `ggridges` | `references/extensions.md` |
| Beeswarm / sina / quasirandom | `ggbeeswarm`, `ggforce::geom_sina` | `references/extensions.md` |
| Highlight a subset of many series | `gghighlight` | `references/extensions.md` |
| Nested facets / per-panel scales | `ggh4x` | `references/extensions.md` |
| Modern KM survival curve | `ggsurvfit` | `references/domain-and-palettes.md` |
| Journal-themed palette (Lancet, NEJM, …) | `ggsci` | `references/domain-and-palettes.md` |
| Volcano / forest plot | `ggplot2` + `ggrepel` | `references/domain-and-palettes.md` |
| Interactive plot in HTML report | `ggiraph` | `references/interactivity-and-animation.md` |
| 3D / linked brushing / WebGL | `plotly::plot_ly` | `references/interactivity-and-animation.md` |
| Animated transitions over time | `gganimate` | `references/interactivity-and-animation.md` |

---

## ggplot2 grammar (cheat sheet)

```r
ggplot(data, aes(x = var1, y = var2)) +
  geom_*() +        # what to draw
  scale_*() +       # data → aesthetic mapping
  coord_*() +       # coordinate system
  facet_*() +       # subplots
  theme_*() +       # styling
  labs()            # titles and axis labels
```

Use `+` to add layers. Use `|>` for data wrangling **before** `ggplot()`:

```r
mtcars |>
  filter(cyl %in% c(4, 6)) |>
  ggplot(aes(wt, mpg, color = factor(cyl))) +
  geom_point(size = 3) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 0.8) +
  scale_color_viridis_d(name = "Cylinders") +
  theme_minimal()
```

**ggplot2 ≥3.4 note:** line geoms use `linewidth`, not `size`. `size` now
controls only point and text radius.

---

## Multi-panel composition with patchwork

```r
library(patchwork)

(p1 | p2) / p3 +
  plot_layout(widths = c(2, 1), guides = "collect") +
  plot_annotation(title = "Figure 2", tag_levels = "A") &
  theme_minimal(base_size = 11) &
  theme(legend.position = "bottom")
```

Use `&` (not `+`) to apply theme/layer to **every** plot in the composition.
See `references/composition.md` for `inset_element`, paper-figure templates,
and gotchas.

---

## Scales and labels

```r
scale_y_continuous(labels = scales::label_dollar())
scale_y_continuous(labels = scales::label_percent())
scale_x_date(labels = scales::label_date_short())
scale_y_continuous(labels = scales::label_number(
  scale_cut = scales::cut_short_scale()))    # 1.2K, 3.4M
```

Prefer `scales::label_*` over hand-rolled formatters. See
`references/theme-guide.md` for the full catalog.

---

## Colorblind-safe palettes (required for publication)

```r
# Okabe-Ito — gold standard, 8 colors
okabe_ito <- c("#E69F00", "#56B4E9", "#009E73", "#F0E442",
               "#0072B2", "#D55E00", "#CC79A7", "#999999")
scale_color_manual(values = okabe_ito)
```

Alternatives: `scale_color_viridis_d(option = "cividis")` (discrete),
`scale_color_viridis_c()` (continuous), `scale_color_brewer(palette = "Set2")`.
For journal palettes (Lancet, NEJM, JCO, AAAS, NPG) see `ggsci` in
`references/domain-and-palettes.md`.

---

## Faceting and labels

```r
# Panel widths proportional to data range
facet_grid(row_var ~ col_var, scales = "free", space = "free_x")

# Non-overlapping labels (ggrepel)
ggrepel::geom_text_repel(aes(label = name), max.overlaps = 10, seed = 42)

# Nested facets (ggh4x)
ggh4x::facet_nested(~ region + country)
```

---

## Publication theme

```r
theme_minimal(base_size = 11) +
  theme(
    plot.title          = element_text(face = "bold", size = 14),
    plot.title.position = "plot",
    legend.position     = "bottom",
    panel.grid.minor    = element_blank(),
    strip.text          = element_text(face = "bold")
  )
```

For markdown in titles use `ggtext::element_markdown()`. See
`references/theme-guide.md` for the full element hierarchy and
`scales::label_*` formatters.

---

## Interactive plots

> **Boundary:** Standalone interactive plots only. For interactive plots
> *inside* Shiny apps, use **r-shiny**.

| Need | Use |
|------|-----|
| Hover tooltip on existing ggplot, lightweight HTML report | `ggiraph` |
| Hover + zoom + pan + crosstalk on existing ggplot | `plotly::ggplotly` |
| 3D, linked brushing, > 100k points | `plotly::plot_ly` (native, WebGL) |

```r
# ggiraph — small SVG, ggplot2-native
p <- ggplot(d, aes(x, y, tooltip = name, data_id = name)) +
  ggiraph::geom_point_interactive(size = 3)
ggiraph::girafe(ggobj = p)

# plotly — full interactive featureset
plotly::ggplotly(ggplot(d, aes(x, y)) + geom_point())
```

See `references/interactivity-and-animation.md` for the decision rules.

---

## Animation

```r
library(gganimate)

ggplot(d, aes(x, y, color = group)) +
  geom_point(size = 3) +
  transition_time(year) +
  labs(title = "Year: {frame_time}")
```

See `references/interactivity-and-animation.md` for `transition_states`,
`transition_reveal`, and renderer choice.

---

## Domain plots

| Plot | Recommended |
|------|-------------|
| Kaplan-Meier survival | `ggsurvfit` (modern, replaces `survminer`) |
| Volcano (DE / two-group) | `ggplot2` + `ggrepel` |
| Forest (meta-analysis / coef) | `ggplot2` + `geom_errorbarh` |

> KM for FDA/regulatory work: defer the analytical layer to **r-clinical**.

See `references/domain-and-palettes.md` for full recipes.

---

## Saving figures

```r
ggsave("figure.png", plot = fig,
       width = 180, height = 120, units = "mm", dpi = 300)
ggsave("figure.pdf", plot = fig,
       width = 180, height = 120, units = "mm", device = cairo_pdf)

# Journal: 300 DPI min, single col 89 mm, double col 183 mm
ggsave("figure.tiff", width = 89, height = 89, units = "mm", dpi = 300,
       compression = "lzw")
```

Always set `width` and `height` explicitly. Default dimensions produce
poorly-sized publication figures.

---

## Verification

After publication figure: confirm dimensions match journal spec, run
`colorblindr::cvd_grid(p)` for colorblind safety, verify font sizes.

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|--------------|-----|
| `+` at start of next line | ggplot2 thinks expression ended | End previous line with `+` |
| `color` when `fill` is needed | `fill` is interior; `color` is border | Use `fill` for bars/areas/box; `color` for points/lines |
| `xlim()` / `ylim()` to zoom | Drops data before stats compute | Use `coord_cartesian(xlim = …)` |
| `size` on line geoms | Deprecated since ggplot2 3.4 | Use `linewidth` for lines |
| `geom_bar(stat = "identity")` | Verbose; reads as count | Use `geom_col()` |
| `theme_grey` on publication figure | Default grey is not publication-ready | Use `theme_minimal` / `theme_bw` / custom |
| Discrete scale on continuous data | Cryptic error | Match scale type to data type |
| Grouped bars stack by default | `geom_col` stacks | `position = "dodge"` |
| Default ggplot2 hue scale | Hard to distinguish for ~8% of men | Okabe-Ito / viridis / Set2 |
| `survminer` for new KM code | Low maintenance | Use `ggsurvfit` |
| Theme applied with `+` to a patchwork | Targets last panel only | Use `&` for composition-wide |
| `ggsave` with no width/height | Default dims fail journal spec | Set `width`, `height`, `dpi` |
| Scope creep | Redesigning when asked to tweak | Show minimal diff for the asked change |

---

## Examples

### Faceted scatter, colorblind palette, publication theme

**Prompt:** "Scatter of wt vs mpg faceted by gear, colorblind-safe, publication theme."

```r
mtcars |>
  ggplot(aes(wt, mpg, color = factor(cyl))) +
  geom_point(size = 2.5, alpha = 0.8) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 0.8) +
  scale_color_viridis_d(name = "Cylinders", option = "cividis") +
  facet_wrap(~ gear, labeller = labeller(
    gear = c("3" = "3 Gears", "4" = "4 Gears", "5" = "5 Gears"))) +
  labs(x = "Weight (1000 lbs)", y = "Miles per Gallon",
       title = "Fuel Efficiency by Weight") +
  theme_minimal(base_size = 11) +
  theme(plot.title.position = "plot",
        legend.position     = "bottom",
        strip.text          = element_text(face = "bold"))
```

### Multi-panel paper figure with patchwork

**Prompt:** "Paper figure: scatter top-left, density top-right, boxplot full bottom row, shared legend."

```r
library(patchwork)

(p_scatter | p_density) / p_box +
  plot_layout(widths = c(1, 1), heights = c(1, 1),
              guides = "collect") +
  plot_annotation(tag_levels = "A") &
  theme_minimal(base_size = 11) &
  theme(legend.position = "bottom")
```

**More example prompts:**
- "Build a raincloud plot of Sepal.Length by Species with ggdist"
- "Highlight the top three time series in this 30-line plot with gghighlight"
- "Plot a Kaplan-Meier survival curve with risktable using ggsurvfit"
- "Add markdown bold/italic to my axis title with ggtext"
- "Make my ggplot interactive for an HTML report with ggiraph"
- "Animate this scatter plot over years with gganimate"
- "Swap my colors to the NEJM palette with ggsci"
```

- [ ] **Step 2: Verify line count is ≤300**

```bash
wc -l skills/r-visualization/SKILL.md
```

Expected: ≤300 (target ~280). If over, trim the gotchas table or the Examples section first.

- [ ] **Step 3: Verify conventions**

```bash
grep -n '%>%' skills/r-visualization/SKILL.md || echo "no %>%"
```

Expected: `no %>%`.

- [ ] **Step 4: Run structural test**

```bash
python tests/run_all.py 2>&1 | grep -E "FAIL.*r-visualization" || echo "no r-visualization failures"
```

Expected: `no r-visualization failures`.

- [ ] **Step 5: Commit**

```bash
git add skills/r-visualization/SKILL.md
git commit -m "feat(r-viz): rewrite SKILL.md as routing layer with ecosystem coverage"
```

---

## Task 9: Extend `eval.md`

**Files:**
- Modify: `skills/r-visualization/eval.md`

**Why:** Add binary questions, prompts, and boundary tests covering the new packages. All existing content is retained.

- [ ] **Step 1: Read current `eval.md` and append new content**

Append to the **Binary Eval Questions** section (preserve numbering, continue):

```markdown
7. Does the skill prefer `ggsurvfit` over `survminer` for new KM code?
8. Does the skill use `scales::label_*` over hand-rolled `formatC` / `sprintf` for axis labels?
9. Does the skill prefer `geom_col()` over `geom_bar(stat = "identity")`?
10. When asked for markdown / bold / italic in axis or title text, does the skill route through `ggtext::element_markdown()`?
11. When asked for a raincloud plot, does the skill use `ggdist`?
12. When asked for ridgeline / stacked density plots, does the skill use `ggridges`?
13. For >100k points, does the skill suggest `geom_hex()` / aggregation / `plot_ly` WebGL rather than dropping a static `plotly::ggplotly`?
14. For a multi-panel paper figure, does the skill reach for `patchwork` and use `&` for composition-wide theme?
```

Append to the **Test Prompts → Happy Path** section:

```markdown
- "Build a raincloud plot of Sepal.Length by Species using ggdist."
- "Make a ridgeline plot of diamond price by cut using ggridges."
- "Compose a 2x2 paper figure of four scatter plots with a shared legend at the bottom using patchwork."
- "Highlight the top three time series in this 30-line plot using gghighlight."
- "Add markdown formatting (bold, italic, superscript units) to my axis title using ggtext."
- "Plot a Kaplan-Meier survival curve with a risktable using ggsurvfit."
- "Swap my plot's colors to the NEJM palette using ggsci."
- "Make my static ggplot interactive for an HTML report using ggiraph."
- "Animate a scatter plot over years using gganimate."
- "Build nested facets (Region > Country) using ggh4x."
```

Append to the **Test Prompts → Boundary Tests** section:

```markdown
- "Build a Shiny dashboard with an animated bar chart that updates on user input." (boundary -> r-shiny)
- "Render a styled table with sparkline columns using gt." (boundary -> r-tables)
- "Generate a Kaplan-Meier curve formatted to FDA submission standards with stratification." (boundary -> r-clinical for analytical layer; this skill handles ggplot mechanics only)
```

Append to the **Success Criteria** section:

```markdown
- New KM code MUST use `ggsurvfit`. Generating `survminer::ggsurvplot` for a new request without explicit user preference is a failure.
- Markdown text in titles/labels MUST route through `ggtext::element_markdown()` (or `element_textbox`); using `parse = TRUE` plotmath instead is a failure when markdown is requested.
- Raincloud requests MUST use `ggdist::stat_halfeye` / `stat_dots` (with optional `geom_boxplot`); a violin-only or box-only plot is a failure.
- Ridgeline requests MUST use `ggridges`; stacking densities with `position = "stack"` is a failure.
- Multi-panel paper-figure requests MUST use `patchwork` (or `cowplot::plot_grid` only when explicitly asked); using `gridExtra::grid.arrange` for new code is a failure.
- Composition-wide theming MUST use `&`, not `+`. Applying `theme()` with `+` to a patchwork object and expecting it on every panel is a failure.
- Bar / line / segment geoms MUST use `linewidth` for line widths in any new code (ggplot2 ≥3.4); using `size` on lines is a failure.
- Highlight requests MUST use `gghighlight`; manually filtering and re-plotting twice is acceptable but suboptimal — `gghighlight` is preferred.
```

- [ ] **Step 2: Verify**

```bash
wc -l skills/r-visualization/eval.md
grep -c "^- " skills/r-visualization/eval.md
```

Expected: file is longer; routing tests still apply.

- [ ] **Step 3: Run test suite**

```bash
python tests/run_all.py 2>&1 | grep -E "FAIL.*r-visualization" || echo "still clean"
```

Expected: `still clean`.

- [ ] **Step 4: Commit**

```bash
git add skills/r-visualization/eval.md
git commit -m "test(r-viz): extend eval.md with new package coverage and boundaries"
```

---

## Task 10: Extend `scripts/check_plot_conventions.R`

**Files:**
- Modify: `skills/r-visualization/scripts/check_plot_conventions.R`

**Why:** Add three new checks. Keep existing checks intact.

- [ ] **Step 1: Read the current script**

```bash
cat skills/r-visualization/scripts/check_plot_conventions.R
```

Note the structure: a `for (f in r_files)` loop with per-line checks calling `add_issue(file, ln, type, detail)`.

- [ ] **Step 2: Add new checks inside the per-line loop**

Inside the existing `for (i in seq_along(lines))` loop, after the existing checks but before the loop closes, add:

```r
    # Check 5: survminer used without ggsurvfit (file-level signal)
    if (grepl("library\\(survminer\\)", line)) {
      add_issue(f, i, "legacy-survminer",
                "Prefer ggsurvfit (modern, ggplot2-native) over survminer for new KM code")
    }

    # Check 6: geom_bar(stat = "identity") instead of geom_col
    if (grepl("geom_bar\\s*\\(\\s*stat\\s*=\\s*[\"']identity[\"']", line)) {
      add_issue(f, i, "use-geom-col",
                "Prefer geom_col() over geom_bar(stat = \"identity\")")
    }

    # Check 7: theme_grey / theme_gray used with ggsave (publication context)
    # (Detected at file level after the loop — see below.)
```

- [ ] **Step 3: Add file-level check 7 after the per-line loop**

After the `for (i in seq_along(lines))` block closes but before `for (f in r_files)` closes, add:

```r
  joined <- paste(lines, collapse = "\n")
  uses_default_theme <- grepl("theme_gr[ae]y\\s*\\(", joined)
  uses_ggsave        <- grepl("ggsave\\s*\\(", joined)
  if (uses_default_theme && uses_ggsave) {
    add_issue(f, NA_integer_, "default-theme-on-save",
              "theme_grey/theme_gray detected with ggsave — likely publication context using default theme; prefer theme_minimal / theme_bw / custom")
  }
```

- [ ] **Step 4: Update any output / summary section to handle the new check types**

If the script has a final formatting block that filters issue types, ensure the new types (`legacy-survminer`, `use-geom-col`, `default-theme-on-save`) are not filtered out. Most likely the script just prints all issues — verify with a smoke test.

- [ ] **Step 5: Smoke-test the script**

```bash
Rscript skills/r-visualization/scripts/check_plot_conventions.R skills/r-visualization/
```

Expected: script runs without R syntax errors. It may flag issues in references/ — that is fine; the goal is to confirm the script does not crash. If it flags issues in the skill's own example R code, those are real and must be fixed in the source files.

- [ ] **Step 6: Verify R conventions in the script itself**

```bash
grep -n '%>%' skills/r-visualization/scripts/check_plot_conventions.R || echo "no %>%"
```

Expected: `no %>%`.

- [ ] **Step 7: Commit**

```bash
git add skills/r-visualization/scripts/check_plot_conventions.R
git commit -m "feat(r-viz): extend convention checker with survminer, geom_col, default-theme detections"
```

---

## Task 11: Extend `tests/routing_matrix.json`

**Files:**
- Modify: `tests/routing_matrix.json`

**Why:** New trigger phrases must route to `r-visualization`. The structural test (`test_routing.py`) reads from this file.

- [ ] **Step 1: Inspect the routing matrix shape**

```bash
python -c "import json; d=json.load(open('tests/routing_matrix.json')); print(type(d), list(d)[:5] if isinstance(d, dict) else d[:2])"
```

Note the schema (likely a list of `{prompt, expected_skills}` entries or similar).

- [ ] **Step 2: Find existing r-visualization routing entries**

```bash
grep -n "r-visualization" tests/routing_matrix.json | head -20
```

Use one as a template for new entries.

- [ ] **Step 3: Add new routing entries**

For each of the following prompts, add an entry that routes to `r-visualization` and explicitly does NOT route to other R skills (matching the existing convention in the file):

- "Build a raincloud plot of measurements by group."
- "Make a ridgeline plot showing distributions across categories."
- "Add a beeswarm plot with one point per observation."
- "Use markdown formatting in my plot title."
- "Highlight a subset of lines in a multi-line plot."
- "Build a multi-panel paper figure with shared legend using patchwork."
- "Build nested facets with two grouping variables."
- "Animate a ggplot over time."
- "Make my ggplot interactive for an HTML report."
- "Plot a modern Kaplan-Meier curve with a risk table."
- "Swap my plot to a journal-themed palette like Lancet or NEJM."

Follow the exact JSON shape and field names already used in the file. If
`expected_skills` is a list and `not_skills` is a separate list, match that. If
the file uses `routes_to` and `does_not_route_to`, match those.

- [ ] **Step 4: Validate JSON**

```bash
python -c "import json; json.load(open('tests/routing_matrix.json')); print('valid')"
```

Expected: `valid`.

- [ ] **Step 5: Run routing tests**

```bash
python tests/run_all.py 2>&1 | grep "Layer 2"
```

Expected: `Layer 2: Skill Routing Matrix: <N>/<N> passed` with `<N>` increased by the number of new routing entries (each may produce 1–2 test rows).

If any new prompt is misrouted, the test output will show the failing prompt — adjust the SKILL.md description triggers in Task 8 (revisit and re-commit) until it routes correctly. Do NOT change the test to make it pass.

- [ ] **Step 6: Commit**

```bash
git add tests/routing_matrix.json
git commit -m "test: add routing entries for r-visualization ecosystem triggers"
```

---

## Task 12: Full verification pass

**Files:**
- Read-only: entire `skills/r-visualization/` tree, plus tests

**Why:** Confirm the definition-of-done from spec §10 is met.

- [ ] **Step 1: Line counts**

```bash
wc -l skills/r-visualization/SKILL.md \
      skills/r-visualization/references/*.md
```

Expected:
- `SKILL.md` ≤ 300
- Each reference file ≤ 400

If any file is over, trim aggressively. SKILL.md priority order for trimming:
gotchas table → "More example prompts" list → optional decision tables → never trim the picking-the-right-tool table.

- [ ] **Step 2: No `%>%`**

```bash
grep -rn '%>%' skills/r-visualization/ --exclude=eval.md || echo "clean"
```

Expected: `clean`.

- [ ] **Step 3: No `=` for assignment in R example code**

```bash
grep -rEn "^[[:space:]]*[a-z_][a-z0-9_]*[[:space:]]*=[^=]" skills/r-visualization/ \
  --include="*.md" --include="*.R" || echo "no = assignment"
```

Expected: `no = assignment`. False positives may appear from `aes(x = …)` or function arguments — manually inspect each match. Fix any genuine `<-` violations.

- [ ] **Step 4: Convention checker on the skill's own example code**

```bash
Rscript skills/r-visualization/scripts/check_plot_conventions.R skills/r-visualization/
```

Inspect output. Any flags on the skill's own example code must be fixed in the source markdown / R files; flags from the references that point to *teaching-by-counterexample* code should be eliminated by rewriting the example to be conformant.

- [ ] **Step 5: Full test suite**

```bash
python tests/run_all.py 2>&1 | tail -10
```

Expected: total **failures unchanged at 9** (the pre-existing baseline). r-visualization itself must be at 100%. Confirm with:

```bash
python tests/run_all.py 2>&1 | grep -E "FAIL.*r-visualization" || echo "r-visualization clean"
```

Expected: `r-visualization clean`.

- [ ] **Step 6: Manual smoke — every reference is lazy-linked from SKILL.md**

```bash
grep -nE "references/(composition|extensions|interactivity-and-animation|domain-and-palettes|theme-guide|ggplot2-layers)\.md" skills/r-visualization/SKILL.md
```

Expected: every one of the six references is mentioned at least once.

- [ ] **Step 7: Manual smoke — every package mentioned in SKILL.md is covered in a reference**

```bash
for pkg in patchwork scales ggrepel ggtext ggdist ggridges ggbeeswarm gghighlight ggforce ggh4x ggsurvfit ggsci plotly ggiraph gganimate; do
  hits=$(grep -rln "\b$pkg\b" skills/r-visualization/references/ 2>/dev/null | wc -l)
  printf "%-12s %s\n" "$pkg" "$hits reference file(s)"
done
```

Expected: every package has at least 1 reference hit.

- [ ] **Step 8: Commit (only if any small fixes were needed in earlier files during verification)**

```bash
git status
# If any files changed in this verification round:
git add -A && git commit -m "fix(r-viz): verification-round corrections"
# Otherwise, no commit. Move on.
```

---

## Task 13: Branch finalization

**Files:** none

**Why:** Hand off the feature branch for review.

- [ ] **Step 1: Confirm branch state**

```bash
git log --oneline main..HEAD
git status
```

Expected: a clean commit chain on `feature/r-visualization-upgrade`, working tree clean.

- [ ] **Step 2: Show summary diff stats**

```bash
git diff --stat main..HEAD
```

Sanity-check that the changed files match the file structure table at the top of this plan.

- [ ] **Step 3: Stop and ask the user how to integrate**

Per superpowers:finishing-a-development-branch: present merge / PR / cleanup options to the user. Do NOT auto-merge or auto-push.

---

## Self-Review (filled in during plan-writing)

**Spec coverage check.**

| Spec §  | Covered by |
|---------|------------|
| §2 package set | Tasks 4–7 (extensions, composition, interactivity-and-animation, domain-and-palettes), Task 8 (SKILL.md mentions all) |
| §3 file layout | Task tables + Tasks 2–7 |
| §4 SKILL.md outline | Task 8 |
| §5 reference content | Tasks 4–7 (each has a complete file body in the plan) |
| §6 eval.md additions | Task 9 |
| §7 check_plot_conventions extensions | Task 10 |
| §8 routing matrix updates | Task 11 |
| §9 decisions/risks | Reflected throughout (ggsurvfit-first in Task 7/8; cowplot-pointer-only in Task 4; scales-in-theme-guide in Task 3) |
| §10 verification | Task 12 |
| §11 out of scope | No tasks touch the listed out-of-scope items |

No gaps.

**Placeholder scan.** No "TBD" / "TODO" / "implement later" remains. Each step has either exact code, exact commands, or exact file content.

**Type / signature consistency.** Function names referenced consistently across tasks: `ggsurvfit::ggsurvfit()`, `add_risktable()`, `scales::label_*`, `patchwork::plot_layout()`, `gghighlight()`, `ggtext::element_markdown()`. The `&` vs `+` distinction is stated identically in Task 4 (composition.md), Task 8 (SKILL.md), and Task 9 (eval success criteria).
