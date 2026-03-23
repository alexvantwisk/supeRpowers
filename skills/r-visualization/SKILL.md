---
name: r-visualization
description: >
  Use when creating plots, charts, or visualizations in R using ggplot2, plotly,
  or htmlwidgets. Provides expert guidance on the grammar of graphics,
  publication-quality figures, domain-specific plots, theming, and interactive
  visualization.
  Triggers: ggplot2, plot, chart, visualization, figure, plotly, htmlwidgets,
  histogram, scatter, bar chart, heatmap, publication figure, facet, theme.
  Do NOT use for interactive Shiny dashboards — use r-shiny instead.
  Do NOT use for formatted data tables — use r-tables instead.
---

# R Visualization

Build publication-quality visualizations in R using the ggplot2 grammar of
graphics, with extensions for interactivity and domain-specific plots.

**Core pipeline:** `ggplot()` + `aes()` -> geom layers -> scales -> coords -> facets -> theme

---

## ggplot2 Grammar of Graphics

```r
ggplot(data, aes(x = var1, y = var2)) +
  geom_*() +        # Geometric objects (what to draw)
  scale_*() +       # Map data values to aesthetics
  coord_*() +       # Coordinate system
  facet_*() +       # Subplot panels
  theme_*() +       # Visual styling
  labs()            # Labels and titles
```

Use `+` to add layers (not `|>`). The pipe is for data wrangling before `ggplot()`:

```r
mtcars |>
  filter(cyl %in% c(4, 6)) |>
  ggplot(aes(x = wt, y = mpg, color = factor(cyl))) +
  geom_point(size = 3) +
  geom_smooth(method = "lm", se = FALSE) +
  scale_color_viridis_d(name = "Cylinders") +
  theme_minimal()
```

---

## Common Geoms

| Geom | Use Case | Key Aesthetics |
|------|----------|---------------|
| `geom_point()` | Scatterplots | x, y, color, size, shape, alpha |
| `geom_line()` | Time series, trends | x, y, color, linetype, linewidth |
| `geom_col()` | Bar charts (values) | x, y, fill |
| `geom_boxplot()` | Distributions by group | x, y, fill, color |
| `geom_violin()` | Distribution shape | x, y, fill, trim, scale |
| `geom_histogram()` | Single-variable distribution | x, fill, bins/binwidth |
| `geom_density()` | Smooth distribution | x, fill, alpha, bw |
| `geom_smooth()` | Trend lines | x, y, method, se |
| `geom_tile()` | Heatmaps | x, y, fill |
| `geom_sf()` | Spatial/map data | geometry, fill, color |

Prefer `geom_col()` over `geom_bar(stat = "identity")`.

Read `references/ggplot2-layers.md` for detailed geom/stat/position reference.

---

## Scales

```r
scale_x_continuous(labels = scales::comma)
scale_y_log10(labels = scales::label_log())
scale_x_date(date_breaks = "3 months", date_labels = "%b %Y")
scale_color_manual(values = c("A" = "#E69F00", "B" = "#56B4E9"))
```

### Colorblind-Safe Palettes

**Always prefer colorblind-safe palettes for published figures.**

| Function | Type | Use |
|----------|------|-----|
| `scale_color_viridis_c()` | Continuous | Heatmaps, gradients |
| `scale_color_viridis_d()` | Discrete | Categorical color |
| `scale_fill_brewer(palette = "Set2")` | Discrete | Up to 8 categories |

Viridis options: `"viridis"`, `"magma"`, `"plasma"`, `"inferno"`, `"cividis"`.

```r
# Okabe-Ito palette (8 colors, highly accessible)
okabe_ito <- c("#E69F00", "#56B4E9", "#009E73", "#F0E442",
               "#0072B2", "#D55E00", "#CC79A7", "#999999")
scale_color_manual(values = okabe_ito)
```

---

## Faceting

```r
# Wrap — auto-arrange panels by one variable
facet_wrap(~ group, ncol = 3, scales = "free_y")

# Grid — rows x columns by two variables
facet_grid(row_var ~ col_var, scales = "free", space = "free_x")

# Custom labels
facet_wrap(~ group, labeller = labeller(group = c(a = "Group A", b = "Group B")))
```

`scales = "free"` gives each panel its own axis range.

---

## Labels and Annotations

```r
labs(title = "Main Title", subtitle = "Context", x = "X", y = "Y",
     color = "Legend", caption = "Source: dataset")

annotate("text", x = 5, y = 10, label = "Notable", fontface = "italic")

# Non-overlapping labels
ggrepel::geom_text_repel(aes(label = name), max.overlaps = 10)
```

---

## Publication Themes

```r
theme_minimal(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold", size = 14),
    plot.title.position = "plot",
    legend.position = "bottom",
    panel.grid.minor = element_blank(),
    strip.text = element_text(face = "bold")
  )
```

Read `references/theme-guide.md` for complete theme element hierarchy.

---

## Multi-Panel Figures with patchwork

```r
library(patchwork)
p1 <- ggplot(data, aes(x, y)) + geom_point()
p2 <- ggplot(data, aes(x)) + geom_histogram()
p3 <- ggplot(data, aes(group, y)) + geom_boxplot()

(p1 | p2) / p3 +   # Complex layout: top row | bottom
  plot_layout(ncol = 2, widths = c(2, 1)) +
  plot_annotation(title = "Combined Figure", tag_levels = "A")
```

---

## Saving Figures

```r
ggsave("figure.png", width = 8, height = 6, dpi = 300)
ggsave("figure.pdf", plot = p1, width = 180, height = 120, units = "mm",
       device = cairo_pdf)

# Journal requirements: 300 DPI min, single col = 89mm, double = 183mm
ggsave("figure.tiff", width = 89, height = 89, units = "mm", dpi = 300,
       compression = "lzw")
```

---

## Interactive Plots

```r
# Convert any ggplot to interactive with plotly
p <- ggplot(data, aes(x, y, color = group, text = label)) + geom_point()
plotly::ggplotly(p, tooltip = c("text", "x", "y"))
```

Use native `plot_ly()` for 3D plots, animations, complex hover templates,
linked brushing, or >100k points.

---

## Domain-Specific Plots

### Kaplan-Meier Survival Curves

```r
library(survival)
library(survminer)

fit <- survfit(Surv(time, status) ~ treatment, data = clinical_data)
ggsurvplot(fit, data = clinical_data, pval = TRUE, risk.table = TRUE,
           conf.int = TRUE, palette = c("#E69F00", "#56B4E9"),
           xlab = "Time (months)", ggtheme = theme_minimal())
```

### Forest Plot

```r
forest_data |>
  ggplot(aes(x = estimate, y = reorder(study, estimate))) +
  geom_point(size = 3) +
  geom_errorbarh(aes(xmin = ci_lower, xmax = ci_upper), height = 0.2) +
  geom_vline(xintercept = 1, linetype = "dashed", color = "grey50") +
  scale_x_log10() +
  labs(x = "Odds Ratio (95% CI)", y = NULL) +
  theme_minimal()
```

### Volcano Plot

```r
de_results |>
  mutate(sig = ifelse(adj_p_val < 0.05 & abs(log2fc) > 1, "Sig", "NS")) |>
  ggplot(aes(x = log2fc, y = -log10(adj_p_val), color = sig)) +
  geom_point(alpha = 0.6, size = 1.5) +
  scale_color_manual(values = c("grey70", "#D55E00")) +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed") +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed") + theme_minimal()
```

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `+` at start of next line | ggplot2 thinks the expression ended; next line is a no-op | Always end the previous line with `+` |
| `color` when `fill` is needed | Bar/area geoms use `fill` for interior; `color` is the border | Use `fill` for bars, areas, boxplots; `color` for points, lines |
| `xlim()`/`ylim()` to zoom | Removes data outside range before stat computation | Use `coord_cartesian(xlim = ..., ylim = ...)` to zoom without dropping data |
| No `fig.width`/`fig.height` set | Default dimensions produce poorly sized publication figures | Set explicit `width`/`height` in `ggsave()` or chunk options |
| Discrete scale on continuous data | `scale_color_manual()` on a numeric column throws cryptic error | Match scale type to data type: `_continuous()` vs `_discrete()` |
| Grouped bars stack by default | `geom_col()` stacks groups unless told otherwise | Add `position = "dodge"` or `position = position_dodge(width = 0.9)` |
| Colorblind-unsafe palette | Default ggplot2 hue scale is hard to distinguish for ~8% of men | Use `scale_color_viridis_*()` or `scale_color_brewer(palette = "Set2")` |
| Scope creep | Claude redesigns entire plot when asked to tweak one element | Fix only the identified issue; show minimal diff |

---

## Examples

### Happy Path: Faceted scatter with colorblind palette and theme

**Prompt:** "Scatter of wt vs mpg faceted by gear, colorblind-safe, publication theme."

```r
# Input
library(ggplot2)

# Output
mtcars |>
  ggplot(aes(x = wt, y = mpg, color = factor(cyl))) +
  geom_point(size = 2.5, alpha = 0.8) +
  geom_smooth(method = "lm", se = FALSE, linewidth = 0.8) +
  scale_color_viridis_d(name = "Cylinders", option = "cividis") +
  facet_wrap(~ gear, labeller = labeller(gear = c("3" = "3 Gears", "4" = "4 Gears", "5" = "5 Gears"))) +
  labs(x = "Weight (1000 lbs)", y = "Miles per Gallon", title = "Fuel Efficiency by Weight") +
  theme_minimal(base_size = 11) +
  theme(plot.title.position = "plot", legend.position = "bottom",
        strip.text = element_text(face = "bold"))
```

### Edge Case: Overlapping labels fixed with ggrepel

**Prompt:** "Label the top 5 cars by mpg, but labels overlap badly."

```r
# Input
library(ggrepel)
top5 <- mtcars |> tibble::rownames_to_column("car") |>
  dplyr::slice_max(mpg, n = 5)

# Output — geom_text() would overlap; ggrepel pushes labels apart
mtcars |>
  tibble::rownames_to_column("car") |>
  ggplot(aes(x = wt, y = mpg)) +
  geom_point(color = "grey60") +
  geom_point(data = top5, color = "#D55E00", size = 3) +
  geom_text_repel(data = top5, aes(label = car),
                  max.overlaps = 10, nudge_y = 1, seed = 42) +
  theme_minimal()
```

**More example prompts:**
- "Make a grouped bar chart with dodged bars and Set2 palette"
- "Build a multi-panel figure (scatter + density + boxplot) with patchwork for a paper"
- "Plot a Kaplan-Meier survival curve with risk table using survminer"
- "Convert my ggplot to an interactive plotly chart with custom tooltips"
