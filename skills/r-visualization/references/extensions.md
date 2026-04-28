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

Label only a subset:

```r
ggplot(mtcars, aes(wt, mpg)) +
  geom_point() +
  geom_text_repel(
    data = \(d) dplyr::slice_max(d, mpg, n = 5),
    aes(label = rownames(mtcars)[mpg %in% sort(mpg, decreasing = TRUE)[1:5]]),
    seed = 42
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

For text boxes with wrapping (long subtitles):

```r
labs(subtitle =
  "A long explanatory subtitle that should wrap nicely across multiple lines …") +
  theme(plot.subtitle = element_textbox_simple(
    size = 10, lineheight = 1.2, padding = margin(4, 0, 4, 0)
  ))
```

**Gotcha:** must set the matching `element_markdown()` (or `element_textbox*`)
on every text element that uses markdown. Missing one shows the raw HTML.

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

For dot-distribution plots (alternative to histogram for small n):

```r
stat_dots(quantiles = 100)   # 100 dots representing the distribution
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

For ridgeline gradient fills (the ridge itself is colored by x):

```r
geom_density_ridges_gradient(aes(fill = after_stat(x)), scale = 1.2) +
  scale_fill_viridis_c()
```

**Gotcha:** `scale > 1` causes ridges to overlap (often desired). `scale = 1`
makes ridges just touch. `rel_min_height` cuts the long tails so the ridge
does not spread to the page edge.

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

For points:

```r
ggplot(mtcars, aes(wt, mpg)) +
  geom_point(size = 3) +
  gghighlight(mpg > 25, label_key = rownames(mtcars))
```

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
ggplot(mtcars, aes(wt, mpg)) +
  geom_point() +
  geom_mark_rect(
    aes(filter = mpg > 25, label = "High mpg"),
    expand = unit(2, "mm")
  )
```

Other useful ggforce functions: `geom_arc_bar`, `geom_parallel_sets`,
`geom_link`, `geom_circle`, `geom_voronoi_tile`, `geom_mark_hull`,
`geom_mark_ellipse`.

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
ggplot(d, aes(x, y)) +
  geom_point() +
  facet_wrap(~ panel) +
  facetted_pos_scales(
    y = list(
      scale_y_log10(),
      scale_y_continuous(limits = c(0, 100))
    )
  )

# Truncated axes (Tufte-style minimal axes)
ggplot(d, aes(x, y)) +
  geom_point() +
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
