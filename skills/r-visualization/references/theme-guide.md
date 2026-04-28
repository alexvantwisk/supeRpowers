# ggplot2 Theme Element Hierarchy

Complete reference for customizing every visual element of a ggplot2 plot.

---

## Element Types

All theme elements are set using one of four functions:

| Function | Controls | Key Params |
|----------|----------|-----------|
| `element_text()` | Text elements | `family`, `face`, `colour`, `size`, `hjust`, `vjust`, `angle`, `lineheight`, `margin` |
| `element_line()` | Lines and ticks | `colour`, `linewidth`, `linetype`, `lineend`, `arrow` |
| `element_rect()` | Rectangles/backgrounds | `fill`, `colour`, `linewidth`, `linetype` |
| `element_blank()` | Remove element entirely | none |

```r
# Example: bold title, no minor gridlines, light grey background
theme(
  plot.title = element_text(face = "bold", size = 14),
  panel.grid.minor = element_blank(),
  panel.background = element_rect(fill = "grey98")
)
```

---

## Complete Theme Element Tree

### Plot-Level Elements (outermost)

```r
theme(
  # Overall plot
  plot.background = element_rect(),    # Entire figure background
  plot.title = element_text(),         # Main title
  plot.title.position = "plot",        # "plot" aligns to full plot, "panel" to panel
  plot.subtitle = element_text(),      # Subtitle below title
  plot.caption = element_text(),       # Caption (bottom-right by default)
  plot.caption.position = "plot",      # "plot" or "panel"
  plot.tag = element_text(),           # Panel tag (e.g., "A", "B")
  plot.tag.position = "topleft",       # "topleft", "top", "topright", etc.
  plot.margin = margin(t, r, b, l, unit = "pt")  # Outer margins
)
```

### Panel Elements (the plotting area)

```r
theme(
  panel.background = element_rect(),   # Panel background
  panel.border = element_rect(),       # Panel border
  panel.grid = element_line(),         # All gridlines
  panel.grid.major = element_line(),   # Major gridlines (both axes)
  panel.grid.major.x = element_line(), # Major gridlines (x only)
  panel.grid.major.y = element_line(), # Major gridlines (y only)
  panel.grid.minor = element_line(),   # Minor gridlines (both axes)
  panel.grid.minor.x = element_line(), # Minor gridlines (x only)
  panel.grid.minor.y = element_line(), # Minor gridlines (y only)
  panel.spacing = unit(0.5, "lines"),  # Space between facet panels
  panel.spacing.x = unit(0.5, "lines"),
  panel.spacing.y = unit(0.5, "lines"),
  panel.ontop = FALSE                  # Draw panel on top of data?
)
```

### Axis Elements

```r
theme(
  # All axes
  axis.title = element_text(),         # Both axis titles
  axis.title.x = element_text(),       # X-axis title
  axis.title.x.top = element_text(),   # X-axis title (top)
  axis.title.x.bottom = element_text(),# X-axis title (bottom)
  axis.title.y = element_text(),       # Y-axis title
  axis.title.y.left = element_text(),  # Y-axis title (left)
  axis.title.y.right = element_text(), # Y-axis title (right)

  axis.text = element_text(),          # Both axis tick labels
  axis.text.x = element_text(),        # X tick labels
  axis.text.x.top = element_text(),
  axis.text.x.bottom = element_text(),
  axis.text.y = element_text(),        # Y tick labels
  axis.text.y.left = element_text(),
  axis.text.y.right = element_text(),

  axis.ticks = element_line(),         # All tick marks
  axis.ticks.x = element_line(),
  axis.ticks.y = element_line(),
  axis.ticks.length = unit(0.15, "cm"),# Tick mark length

  axis.line = element_line(),          # Axis lines
  axis.line.x = element_line(),
  axis.line.y = element_line()
)
```

### Legend Elements

```r
theme(
  legend.background = element_rect(),  # Legend background
  legend.key = element_rect(),         # Background of legend keys
  legend.key.size = unit(1.2, "lines"),# Key size (width and height)
  legend.key.height = unit(1, "lines"),# Key height only
  legend.key.width = unit(1, "lines"), # Key width only
  legend.text = element_text(),        # Legend item labels
  legend.title = element_text(),       # Legend title
  legend.title.align = 0,             # 0 = left, 0.5 = center, 1 = right

  legend.position = "right",           # "top", "bottom", "left", "right", "none"
  legend.position = c(0.9, 0.1),       # Inside plot (0-1 coordinates)
  legend.direction = "vertical",       # "horizontal" or "vertical"
  legend.justification = c(1, 0),      # Anchor point for legend.position
  legend.box = "vertical",             # Arrangement of multiple legends
  legend.box.just = "left",            # Justification of legend box
  legend.margin = margin(0, 0, 0, 0),
  legend.spacing = unit(0.5, "lines")
)
```

### Strip Elements (facet labels)

```r
theme(
  strip.background = element_rect(),   # Facet label background
  strip.background.x = element_rect(), # Top strip only
  strip.background.y = element_rect(), # Right strip only
  strip.text = element_text(),         # All strip text
  strip.text.x = element_text(),       # Top strip text
  strip.text.y = element_text(),       # Right strip text
  strip.placement = "inside",          # "inside" or "outside" axis
  strip.switch.pad.grid = unit(0.1, "cm"),
  strip.switch.pad.wrap = unit(0.1, "cm")
)
```

---

## Margins and Spacing

The `margin()` function controls spacing around elements:

```r
# margin(top, right, bottom, left, unit)
# Same order as CSS (clockwise from top)

theme(
  plot.margin = margin(10, 15, 10, 15, "pt"),
  axis.title.x = element_text(margin = margin(t = 10)),
  axis.title.y = element_text(margin = margin(r = 10)),
  plot.title = element_text(margin = margin(b = 10)),
  legend.margin = margin(5, 5, 5, 5),
  panel.spacing = unit(1, "lines")
)
```

---

## Legend Positioning Recipes

```r
# Bottom, single row
theme(legend.position = "bottom", legend.direction = "horizontal")

# Inside plot, top-right corner
theme(
  legend.position = c(0.95, 0.95),
  legend.justification = c(1, 1),
  legend.background = element_rect(fill = alpha("white", 0.8))
)

# Inside plot, bottom-left
theme(
  legend.position = c(0.05, 0.05),
  legend.justification = c(0, 0)
)

# No legend
theme(legend.position = "none")

# Multiple legends stacked
theme(legend.box = "vertical", legend.box.just = "left")
```

---

## Creating Reusable Custom Themes

Define a theme function for consistent styling across a project:

```r
theme_project <- function(base_size = 11, base_family = "") {
  theme_minimal(base_size = base_size, base_family = base_family) %+replace%
    theme(
      # Title styling
      plot.title = element_text(
        face = "bold", size = rel(1.2),
        margin = margin(b = 8), hjust = 0
      ),
      plot.title.position = "plot",
      plot.subtitle = element_text(
        color = "grey40", margin = margin(b = 12)
      ),
      plot.caption = element_text(
        color = "grey50", size = rel(0.8), hjust = 1
      ),

      # Panel
      panel.grid.minor = element_blank(),
      panel.grid.major.x = element_blank(),

      # Axes
      axis.title = element_text(size = rel(0.9), color = "grey30"),
      axis.text = element_text(size = rel(0.85), color = "grey40"),

      # Legend
      legend.position = "bottom",
      legend.title = element_text(face = "bold", size = rel(0.9)),

      # Facets
      strip.text = element_text(face = "bold", size = rel(0.9)),
      strip.background = element_rect(fill = "grey95", colour = NA),

      # Margins
      plot.margin = margin(12, 12, 12, 12)
    )
}

# Usage
ggplot(data, aes(x, y)) +
  geom_point() +
  theme_project()
```

**Key notes:**
- Use `%+replace%` (not `+`) to fully replace elements from the parent theme
- Use `rel()` for relative sizing so `base_size` scales everything
- Export the theme function if building a package

---

## Journal-Specific Theme Recipes

### Nature Style

```r
theme_nature <- function(base_size = 7, base_family = "Helvetica") {
  theme_classic(base_size = base_size, base_family = base_family) %+replace%
    theme(
      plot.title = element_text(face = "bold", size = 8),
      axis.title = element_text(size = 7),
      axis.text = element_text(size = 6, color = "black"),
      axis.line = element_line(linewidth = 0.4, color = "black"),
      axis.ticks = element_line(linewidth = 0.3, color = "black"),
      legend.title = element_text(size = 7, face = "bold"),
      legend.text = element_text(size = 6),
      legend.key.size = unit(0.3, "cm"),
      strip.text = element_text(size = 7, face = "bold"),
      strip.background = element_blank(),
      panel.grid = element_blank()
    )
}
# Width: single column = 89mm, double = 183mm, 1.5 = 120mm
# DPI: 300 minimum, 600 for line art
# Font: Helvetica or Arial, 5-7pt
```

### Science Style

```r
theme_science <- function(base_size = 8, base_family = "Arial") {
  theme_classic(base_size = base_size, base_family = base_family) %+replace%
    theme(
      plot.title = element_text(face = "bold", size = 9),
      axis.title = element_text(size = 8),
      axis.text = element_text(size = 7, color = "black"),
      axis.line = element_line(linewidth = 0.5),
      axis.ticks = element_line(linewidth = 0.3),
      legend.position = "right",
      legend.title = element_text(size = 7),
      legend.text = element_text(size = 6),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", size = 8)
    )
}
# Width: single column = 55mm, double = 120mm, full = 174mm
# DPI: 300 for halftones, 600 for combination, 1200 for line art
# Font: Arial or Helvetica
```

### NEJM / Medical Journal Style

```r
theme_nejm <- function(base_size = 8, base_family = "Arial") {
  theme_classic(base_size = base_size, base_family = base_family) %+replace%
    theme(
      plot.title = element_text(face = "bold", size = 9, hjust = 0),
      axis.title = element_text(size = 8, face = "bold"),
      axis.text = element_text(size = 7, color = "black"),
      axis.line = element_line(linewidth = 0.4),
      axis.ticks = element_line(linewidth = 0.3),
      legend.position = "bottom",
      legend.direction = "horizontal",
      legend.title = element_blank(),
      legend.text = element_text(size = 7),
      panel.grid.major.y = element_line(color = "grey90", linewidth = 0.3),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", size = 8)
    )
}
# NEJM palette (from ggsci): "#BC3C29", "#0072B5", "#E18727", "#20854E",
#   "#7876B1", "#6F99AD", "#FFDC91", "#EE4C97"
# Width: single column = 86mm, 1.5 = 133mm, double = 180mm
# DPI: 300 minimum
```

---

## Common Theme Adjustments — Quick Reference

| Goal | Code |
|------|------|
| Remove all gridlines | `panel.grid = element_blank()` |
| Remove minor gridlines only | `panel.grid.minor = element_blank()` |
| Remove x gridlines only | `panel.grid.major.x = element_blank()` |
| Rotate x labels 45 degrees | `axis.text.x = element_text(angle = 45, hjust = 1)` |
| Rotate x labels 90 degrees | `axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1)` |
| Bold title | `plot.title = element_text(face = "bold")` |
| Center title | `plot.title = element_text(hjust = 0.5)` |
| Move legend to bottom | `legend.position = "bottom"` |
| Remove legend | `legend.position = "none"` |
| Remove legend title | `legend.title = element_blank()` |
| Increase text size globally | Use `base_size` param in `theme_*()` |
| Remove axis titles | `axis.title = element_blank()` |
| Black axis lines (classic look) | `axis.line = element_line(color = "black")` |
| Remove facet label background | `strip.background = element_blank()` |
| Bold facet labels | `strip.text = element_text(face = "bold")` |
| Increase panel spacing | `panel.spacing = unit(1.5, "lines")` |
| White plot background | `plot.background = element_rect(fill = "white", colour = NA)` |

---

## Inheritance Chain

Theme elements inherit from parent elements. Setting a parent affects all children:

```
text (all text)
├── axis.title (both axis titles)
│   ├── axis.title.x
│   │   ├── axis.title.x.top
│   │   └── axis.title.x.bottom
│   └── axis.title.y
│       ├── axis.title.y.left
│       └── axis.title.y.right
├── axis.text (both axis labels)
│   ├── axis.text.x → .top, .bottom
│   └── axis.text.y → .left, .right
├── legend.text
├── legend.title
├── strip.text → .x, .y
├── plot.title
├── plot.subtitle
├── plot.caption
└── plot.tag

line (all lines)
├── axis.line → .x, .y
├── axis.ticks → .x, .y
├── panel.grid
│   ├── panel.grid.major → .x, .y
│   └── panel.grid.minor → .x, .y
└── (other line elements)

rect (all rectangles)
├── panel.background
├── panel.border
├── plot.background
├── legend.background
├── legend.key
└── strip.background → .x, .y
```

Setting `theme(text = element_text(family = "Helvetica"))` changes the font
for ALL text elements. Override specific children as needed.

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

For a custom transformation use
`scales::trans_new(name, transform, inverse, breaks, format)`.

### Why `scales::label_*` over `formatC` / `sprintf`

- Vectorised and ggplot2-aware.
- Locale-aware (`big.mark`, `decimal.mark`).
- Composable: `label_number(prefix = "USD ", suffix = "/mo")`.
- Cuts (`cut_short_scale`, `cut_si`, `cut_long_scale`) handle order-of-magnitude
  switches without manual branching.

### Composing formatters

```r
# Currency abbreviated to short scale: $1.2K, $3.4M
scale_y_continuous(labels = label_dollar(scale_cut = cut_short_scale()))

# Percent with one decimal, locale-aware comma
scale_y_continuous(labels = label_percent(accuracy = 0.1, big.mark = ","))
```
