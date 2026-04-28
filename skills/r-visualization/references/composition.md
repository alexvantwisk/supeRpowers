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

For boxed or prefixed tags:

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

For overlay placement that may extend beyond the panel:

```r
inset_element(p_zoom, 0.6, 0.05, 0.98, 0.45,
              clip = "off", on_top = TRUE)
```

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

### Large central plot with two stacked sidekicks

```r
p_main + (p_a / p_b) +
  plot_layout(widths = c(3, 1))
```

### 2x2 grid with a single shared colorbar

```r
(p1 + p2) / (p3 + p4) +
  plot_layout(guides = "collect") &
  scale_color_viridis_c(limits = c(0, 100)) &
  theme(legend.position = "right")
```

---

## Saving compositions

`ggsave()` saves the last printed plot, so either assign first and pass:

```r
fig <- (p1 | p2) / p3 + plot_layout(guides = "collect")
ggsave("figure-2.pdf", fig,
       width = 180, height = 120, units = "mm",
       device = cairo_pdf)
```

For very wide compositions, set width to 2x panel width plus margin: journals
typically allow 89 mm (single col) or 183 mm (double col).

---

## When to reach for cowplot instead

`cowplot` is mature, ggplot2-aware, and predates patchwork. Reach for it only
when you need:

- `cowplot::plot_grid()` with mixed grob types and fine-grained `align = "v"`
  / `align = "h"` axis alignment that patchwork's `plot_layout` cannot
  produce.
- `cowplot::draw_label()` / `cowplot::draw_image()` for absolute-positioned
  annotations or images on top of an arbitrary canvas.
- `cowplot::save_plot()` if a colleague's pipeline already uses it (it is a
  thin wrapper around `ggsave`; either works).

Otherwise: patchwork. Do not mix the two within a single figure — guide
collection and tag inheritance behave differently.

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|--------------|-----|
| Theme applied with `+` only changes last panel | `+` targets last expression | Use `&` for composition-wide theme |
| Legends differ slightly across panels and won't collect | `guides = "collect"` requires identical scales | Make scales explicit with `scale_*_manual(values = …)` shared across plots |
| Tag letters out of order after rearranging | `tag_levels` walks current layout left-to-right, top-to-bottom | Restate `plot_annotation(tag_levels = "A")` after layout changes |
| `inset_element` clipped at panel edge | `clip = "on"` by default | `inset_element(..., clip = "off")` or `on_top = TRUE` |
| Saved figure has tiny text | Composition base size scales with panel count | Set `base_size` in `theme_*()` applied via `&` |
| Mixed `cowplot` + `patchwork` figure | Different guide and tag systems | Pick one tool per figure |
| `ggsave` without explicit plot arg | Saves whatever was last printed | Assign composition to `fig` and pass `ggsave(..., fig)` |
