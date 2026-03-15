# ggplot2 Layers Reference

Detailed reference for geoms, stats, positions, coordinates, scales, and guides.

---

## Geoms — Detailed

### One Variable (Continuous)

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_histogram()` | `bins`, `binwidth`, `boundary` | Use `binwidth` for control |
| `geom_density()` | `bw`, `kernel`, `adjust` | `adjust = 2` for smoother |
| `geom_freqpoly()` | `bins`, `binwidth` | Line version of histogram |
| `geom_dotplot()` | `binwidth`, `method`, `stackdir` | Small datasets only |
| `geom_rug()` | `sides = "b"` | Marginal tick marks |

### One Variable (Discrete)

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_bar()` | `stat = "count"` (default) | Counts occurrences |
| `geom_col()` | none (uses y values directly) | Prefer over `geom_bar(stat = "identity")` |

### Two Variables (Continuous x, Continuous y)

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_point()` | `size`, `shape`, `alpha`, `stroke` | Scatterplots |
| `geom_jitter()` | `width`, `height` | Shortcut for `geom_point(position = "jitter")` |
| `geom_smooth()` | `method`, `formula`, `se`, `span` | `method = "lm"` for linear, `"loess"` for smooth |
| `geom_line()` | `linewidth`, `linetype` | Connects points in x order |
| `geom_path()` | `linewidth`, `linetype` | Connects points in data order |
| `geom_step()` | `direction` | Step function |
| `geom_area()` | `alpha` | Filled area under line |
| `geom_ribbon()` | `ymin`, `ymax` | Confidence bands |

### Two Variables (Discrete x, Continuous y)

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_boxplot()` | `outlier.shape`, `notch`, `varwidth` | `notch = TRUE` for CI |
| `geom_violin()` | `draw_quantiles`, `trim`, `scale` | `scale = "width"` for equal widths |
| `geom_dotplot()` | `binaxis = "y"`, `stackdir = "center"` | Small n distributions |
| `geom_crossbar()` | `ymin`, `ymax`, `fatten` | Error bar with center |
| `geom_errorbar()` | `ymin`, `ymax`, `width` | Vertical error bars |
| `geom_pointrange()` | `ymin`, `ymax` | Point with range |
| `geom_linerange()` | `ymin`, `ymax` | Line range only |

### Two Variables (Both Discrete / Heatmap)

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_tile()` | `width`, `height` | Rectangular heatmap tiles |
| `geom_raster()` | none | Faster than `geom_tile()` for regular grids |
| `geom_contour()` | `bins`, `binwidth` | Contour lines |
| `geom_contour_filled()` | `bins`, `binwidth` | Filled contours |
| `geom_density_2d()` | `bins` | 2D density contours |
| `geom_hex()` | `bins` | Hex-binned scatterplot (large data) |
| `geom_bin_2d()` | `bins` | Rectangular binning |

### Text and Labels

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_text()` | `label`, `size`, `hjust`, `vjust`, `angle` | Plain text |
| `geom_label()` | `label`, `size`, `label.padding`, `label.size` | Text with background |
| `ggrepel::geom_text_repel()` | `max.overlaps`, `force`, `box.padding` | Non-overlapping text |
| `ggrepel::geom_label_repel()` | same as above | Non-overlapping labels |

### Spatial

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_sf()` | `fill`, `color`, `linewidth` | sf objects (maps) |
| `geom_sf_text()` | `label` | Text on sf geometries |
| `geom_sf_label()` | `label` | Labels on sf geometries |

### Reference Lines and Shapes

| Geom | Key Params | Notes |
|------|-----------|-------|
| `geom_hline()` | `yintercept`, `linetype` | Horizontal reference |
| `geom_vline()` | `xintercept`, `linetype` | Vertical reference |
| `geom_abline()` | `slope`, `intercept` | Diagonal line |
| `geom_segment()` | `x`, `y`, `xend`, `yend` | Line segments |
| `geom_curve()` | `x`, `y`, `xend`, `yend`, `curvature` | Curved arrows |
| `geom_rect()` | `xmin`, `xmax`, `ymin`, `ymax` | Rectangles |

---

## Statistical Transformations

Stats compute new values from data before plotting.

```r
# Summarize y at each x — mean and SE
geom_pointrange(stat = "summary", fun = mean,
                fun.min = \(x) mean(x) - se(x),
                fun.max = \(x) mean(x) + se(x))

# Alternative: stat_summary with a geom
stat_summary(fun = mean, geom = "point", size = 3) +
stat_summary(fun.data = mean_se, geom = "errorbar", width = 0.2)
```

| Stat | Purpose | Common Geom |
|------|---------|-------------|
| `stat_summary()` | Aggregate y by x | pointrange, errorbar |
| `stat_summary_bin()` | Aggregate y by binned x | pointrange, col |
| `stat_function()` | Plot a function | line |
| `stat_ecdf()` | Empirical CDF | step |
| `stat_ellipse()` | Confidence ellipses | path |
| `stat_smooth()` | Fitted curve | line + ribbon |
| `stat_count()` | Count at each x | bar |
| `stat_bin()` | Bin continuous x | bar (histogram) |
| `stat_density()` | Kernel density estimate | line, area |
| `stat_bin_2d()` | 2D rectangular binning | tile |
| `stat_bin_hex()` | 2D hexagonal binning | hex |

```r
# Plot a mathematical function
ggplot(data.frame(x = c(-3, 3)), aes(x)) +
  stat_function(fun = dnorm, args = list(mean = 0, sd = 1)) +
  labs(y = "Density")

# Empirical CDF
ggplot(data, aes(x = value, color = group)) +
  stat_ecdf(linewidth = 1) +
  labs(y = "Cumulative Proportion")
```

---

## Position Adjustments

Control how overlapping geoms are arranged.

| Position | Purpose | Common With |
|----------|---------|-------------|
| `position_identity()` | No adjustment (default for most) | geom_point |
| `position_dodge(width)` | Side by side | geom_col, geom_boxplot |
| `position_dodge2(width, padding)` | Side by side (variable width) | geom_boxplot |
| `position_jitter(width, height)` | Random displacement | geom_point |
| `position_jitterdodge()` | Jitter within dodge groups | geom_point on grouped boxplots |
| `position_stack()` | Stack on top of each other | geom_col, geom_area |
| `position_fill()` | Stack normalized to 100% | geom_col, geom_area |
| `position_nudge(x, y)` | Shift by fixed amount | geom_text alongside geom_point |

```r
# Grouped bar chart — dodge
ggplot(data, aes(x = category, y = value, fill = group)) +
  geom_col(position = position_dodge(width = 0.8), width = 0.7)

# Stacked bar chart normalized to 100%
ggplot(data, aes(x = category, fill = group)) +
  geom_bar(position = position_fill()) +
  scale_y_continuous(labels = scales::percent)

# Points with jitter on grouped boxplots
ggplot(data, aes(x = group, y = value, color = subgroup)) +
  geom_boxplot(position = position_dodge(width = 0.8)) +
  geom_point(position = position_jitterdodge(dodge.width = 0.8, jitter.width = 0.15),
             alpha = 0.4)
```

---

## Coordinate Systems

| Coord | Purpose | Key Params |
|-------|---------|-----------|
| `coord_cartesian()` | Zoom without clipping data | `xlim`, `ylim`, `expand` |
| `coord_flip()` | Swap x and y axes | none |
| `coord_fixed()` | Fixed aspect ratio | `ratio` (default 1) |
| `coord_polar()` | Polar coordinates | `theta = "x"` or `"y"` |
| `coord_sf()` | Map projections | `crs`, `xlim`, `ylim` |
| `coord_trans()` | Transformed axes | `x`, `y` (transform names) |

**Important:** Use `coord_cartesian(ylim = ...)` to zoom, NOT `scale_y_continuous(limits = ...)`.
`scale_*` limits remove data outside range (affecting stat computations).
`coord_*` limits only zoom the viewport.

```r
# Zoom into a region without dropping data
ggplot(data, aes(x, y)) +
  geom_boxplot() +
  coord_cartesian(ylim = c(0, 50))

# Horizontal bar chart
ggplot(data, aes(x = reorder(name, value), y = value)) +
  geom_col() +
  coord_flip()

# Pie chart (rarely recommended)
ggplot(data, aes(x = "", y = prop, fill = category)) +
  geom_col(width = 1) +
  coord_polar(theta = "y") +
  theme_void()

# Map with specific projection
ggplot(world_sf) +
  geom_sf() +
  coord_sf(crs = "+proj=robin")  # Robinson projection
```

---

## Scales — Extended Reference

### Continuous Scales

```r
# Numeric formatting
scale_y_continuous(labels = scales::comma)           # 1,000,000
scale_y_continuous(labels = scales::dollar)           # $1,000
scale_y_continuous(labels = scales::percent)          # 100%
scale_y_continuous(labels = scales::label_number(suffix = "K", scale = 1e-3))

# Transforms
scale_y_log10()                                      # Log10 axis
scale_y_sqrt()                                       # Square root axis
scale_y_continuous(trans = "reverse")                 # Reversed axis

# Custom breaks
scale_x_continuous(breaks = c(1, 5, 10, 50, 100))
scale_x_continuous(breaks = scales::breaks_log(n = 6))
```

### Discrete Scales

```r
# Reorder levels
scale_x_discrete(limits = c("Low", "Medium", "High"))

# Rename labels
scale_x_discrete(labels = c(trt1 = "Treatment A", ctrl = "Control"))

# Drop unused levels
scale_x_discrete(drop = TRUE)
```

### Date/Time Scales

```r
scale_x_date(
  date_breaks = "1 month",
  date_labels = "%b %Y",            # "Jan 2025"
  date_minor_breaks = "1 week"
)

scale_x_datetime(
  date_breaks = "6 hours",
  date_labels = "%H:%M"
)

# Common date_labels format codes:
# %Y = 2025, %y = 25, %m = 01, %b = Jan, %B = January
# %d = 01, %e = 1, %H = 14, %M = 30, %S = 00
```

### Color/Fill Scales

```r
# Continuous gradient
scale_fill_gradient(low = "white", high = "darkred")
scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0)
scale_fill_gradientn(colors = terrain.colors(7))

# Viridis family (colorblind-safe, perceptually uniform)
scale_color_viridis_c(option = "plasma")     # Continuous
scale_color_viridis_d(option = "viridis")    # Discrete

# Brewer palettes (colorblind-safe options)
scale_fill_brewer(palette = "Set2")          # Qualitative
scale_fill_brewer(palette = "Blues")          # Sequential
scale_fill_brewer(palette = "RdYlBu")        # Diverging

# Grey scale
scale_color_grey(start = 0.2, end = 0.8)
```

### Size and Shape Scales

```r
# Size mapping
scale_size_continuous(range = c(1, 10))
scale_size_area(max_size = 10)     # 0 maps to size 0 (preferred for counts)

# Shape mapping (max ~6 distinguishable shapes)
scale_shape_manual(values = c(16, 17, 15, 3, 4, 8))
# 16 = filled circle, 17 = filled triangle, 15 = filled square
# 3 = plus, 4 = cross, 8 = asterisk
```

---

## Guide and Legend Customization

```r
# Remove a legend
guides(color = "none")

# Customize legend appearance
guides(
  color = guide_legend(
    title = "My Legend",
    nrow = 2,
    override.aes = list(size = 4, alpha = 1)
  ),
  fill = guide_colorbar(
    title = "Value",
    barwidth = 15,
    barheight = 1,
    title.position = "top"
  )
)

# Legend position via theme
theme(
  legend.position = "bottom",                          # "top", "left", "right", "none"
  legend.position = c(0.85, 0.15),                     # Inside plot (x, y in 0-1)
  legend.direction = "horizontal",
  legend.title = element_text(face = "bold", size = 10),
  legend.text = element_text(size = 9),
  legend.key.size = unit(0.8, "cm")
)

# Reverse legend order
guides(fill = guide_legend(reverse = TRUE))
```

---

## Combining Layers — Patterns

### Overlay Points on Boxplots

```r
ggplot(data, aes(x = group, y = value)) +
  geom_boxplot(outlier.shape = NA, width = 0.5) +
  geom_jitter(width = 0.15, alpha = 0.4, size = 1.5)
```

### Mean + SE on Top of Raw Data

```r
ggplot(data, aes(x = group, y = value)) +
  geom_jitter(width = 0.1, alpha = 0.3) +
  stat_summary(fun = mean, geom = "point", size = 4, color = "red") +
  stat_summary(fun.data = mean_se, geom = "errorbar", width = 0.2, color = "red")
```

### Dual-Axis (Use Sparingly)

```r
# ggplot2 supports secondary axes only as transformations of the primary
coeff <- 10
ggplot(data, aes(x = date)) +
  geom_col(aes(y = rainfall), fill = "steelblue", alpha = 0.6) +
  geom_line(aes(y = temperature * coeff), color = "red", linewidth = 1) +
  scale_y_continuous(
    name = "Rainfall (mm)",
    sec.axis = sec_axis(~ . / coeff, name = "Temperature (C)")
  )
```

### Highlight Subset

```r
ggplot(full_data, aes(x, y)) +
  geom_point(color = "grey80") +
  geom_point(data = subset_data, aes(x, y), color = "#D55E00", size = 3)
```
