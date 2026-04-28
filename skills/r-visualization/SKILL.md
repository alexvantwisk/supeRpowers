---
name: r-visualization
description: >
  Use when creating plots, charts, figures, or visualizations in R with
  ggplot2 and its ecosystem — patchwork, scales, ggrepel, ggtext, ggdist,
  ggridges, ggbeeswarm, gghighlight, ggforce, ggh4x, ggsurvfit, ggsci, plotly,
  ggiraph, gganimate. Covers grammar of graphics, publication-quality figures,
  multi-panel composition, domain plots (KM, volcano, forest), colorblind
  palettes, theming, and interactive / animated visualization.
  Triggers: ggplot2, plot, chart, figure, publication figure, facet, theme,
  patchwork, multi-panel, raincloud, ridgeline, beeswarm, ggrepel, ggtext,
  markdown title, ggdist, ggridges, gghighlight, ggh4x, ggsurvfit,
  Kaplan-Meier, risk table, volcano plot, forest plot, ggsci, NEJM palette,
  colorblind, ggiraph, plotly, gganimate, animated plot.
  Do NOT use for Shiny dashboards (use r-shiny), formatted tables (r-tables),
  FDA/regulatory KM analysis (r-clinical owns the analytical layer), or
  Quarto report layout (r-quarto).
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
ggsave("figure.png", plot = fig, width = 180, height = 120,
       units = "mm", dpi = 300)
ggsave("figure.pdf", plot = fig, width = 180, height = 120,
       units = "mm", device = cairo_pdf)
```

Journal specs: 300 DPI minimum; single col 89 mm, double col 183 mm. Always
set `width`/`height` explicitly — defaults produce poorly-sized figures.
Verify with `colorblindr::cvd_grid(p)` before submission.

---

## Gotchas

| Trap | Fix |
|------|-----|
| `+` at start of next line — silent no-op | End previous line with `+` |
| `color` on a bar/area — colors only the border | Use `fill` for bars/areas/boxes |
| `xlim()`/`ylim()` to zoom drops data before stats | Use `coord_cartesian(xlim = …)` |
| `size` on line geoms — deprecated in ggplot2 ≥3.4 | Use `linewidth` |
| `geom_bar(stat = "identity")` | Use `geom_col()` |
| `theme_grey` on a publication figure | Use `theme_minimal`/`theme_bw`/custom |
| Discrete scale on continuous data | Match scale type to data type |
| Grouped bars stack by default | `position = "dodge"` |
| Default ggplot2 hue scale — not colorblind-safe | Okabe-Ito / viridis / Set2 |
| `survminer` for new KM code | Use `ggsurvfit` |
| `theme()` with `+` on a patchwork — only last panel | Use `&` for composition-wide |
| `ggsave` with no width/height | Set `width`, `height`, `dpi` explicitly |
| Scope creep — redesigning when asked to tweak | Show minimal diff for the asked change |

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

**More example prompts:**

- "Paper figure: scatter top-left, density top-right, boxplot full bottom row, shared legend (patchwork)"
- "Build a raincloud plot with ggdist; highlight top three series with gghighlight"
- "Plot a Kaplan-Meier survival curve with risktable using ggsurvfit"
- "Add markdown formatting to my axis title with ggtext; swap to NEJM palette via ggsci"
- "Make my ggplot interactive for an HTML report with ggiraph; animate over years with gganimate"
