---
name: r-visualization
description: >
  Use when creating plots, charts, or visualizations in R using ggplot2, plotly,
  or htmlwidgets. Includes publication-quality figures and domain-specific plots.
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

p1 + p2            # Side by side
p1 / p2            # Stacked vertically
(p1 | p2) / p3     # Complex layout

(p1 + p2 + p3) +
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
  mutate(significance = case_when(
    adj_p_val < 0.05 & abs(log2fc) > 1 ~ "Significant",
    TRUE ~ "Not significant"
  )) |>
  ggplot(aes(x = log2fc, y = -log10(adj_p_val), color = significance)) +
  geom_point(alpha = 0.6, size = 1.5) +
  scale_color_manual(values = c("grey70", "#D55E00")) +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed") +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed") +
  theme_minimal()
```

### Manhattan Plot

```r
gwas_results |>
  mutate(pos_index = row_number()) |>
  ggplot(aes(x = pos_index, y = -log10(p_value), color = factor(chromosome))) +
  geom_point(alpha = 0.7, size = 0.8) +
  geom_hline(yintercept = -log10(5e-8), linetype = "dashed", color = "red") +
  scale_color_manual(values = rep(c("#1B9E77", "#7570B3"), 11), guide = "none") +
  labs(x = "Chromosome", y = "-Log10(P-Value)") +
  theme_minimal()
```

---

## Examples

**"Create a scatterplot with trend line"**
```r
mtcars |>
  ggplot(aes(x = wt, y = mpg, color = factor(cyl))) +
  geom_point(size = 3) +
  geom_smooth(method = "lm", color = "grey30", se = TRUE) +
  scale_color_viridis_d(name = "Cylinders") +
  labs(x = "Weight (1000 lbs)", y = "Miles per Gallon") +
  theme_minimal()
```

**"Make a grouped bar chart"**
```r
survey_data |>
  ggplot(aes(x = category, y = count, fill = group)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.7) +
  scale_fill_brewer(palette = "Set2") +
  labs(x = NULL, y = "Count", fill = "Group") +
  theme_minimal() +
  theme(legend.position = "top")
```

**"Build a multi-panel figure for a paper"**
```r
library(patchwork)
p_scatter <- ggplot(data, aes(x, y)) + geom_point() + theme_classic()
p_dist <- ggplot(data, aes(x)) + geom_density(fill = "steelblue", alpha = 0.5) + theme_classic()
p_box <- ggplot(data, aes(group, y)) + geom_boxplot() + theme_classic()

(p_scatter | p_dist) / p_box +
  plot_annotation(tag_levels = "A", title = "Figure 1")
ggsave("figure1.pdf", width = 183, height = 160, units = "mm", device = cairo_pdf)
```

**"Plot a Kaplan-Meier curve with risk table"**
```r
fit <- survfit(Surv(time, status) ~ arm, data = trial_data)
ggsurvplot(fit, data = trial_data, pval = TRUE, risk.table = TRUE,
           palette = "jco", ggtheme = theme_minimal())
```

**"Create an interactive version of my ggplot"**
```r
p <- ggplot(data, aes(x, y, text = paste("ID:", id))) +
  geom_point(aes(color = group)) + theme_minimal()
plotly::ggplotly(p, tooltip = "text")
```
