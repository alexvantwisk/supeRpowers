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

### Custom hover template

```r
p <- ggplot(d, aes(x, y,
                   text = paste0("<b>", name, "</b><br>",
                                 "value: ", scales::comma(value)))) +
  geom_point()
ggplotly(p, tooltip = "text")
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

### Linked brushing across patchwork panels

```r
p1 <- ggplot(d, aes(x, y, data_id = id)) + geom_point_interactive()
p2 <- ggplot(d, aes(group, value, data_id = id)) + geom_col_interactive()

girafe(ggobj = patchwork::wrap_plots(p1, p2),
       options = list(opts_hover_inv(css = "opacity:0.2;")))
```

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

### Recipe — reveal a line over time

```r
ggplot(d, aes(date, value, group = country, color = country)) +
  geom_line() +
  transition_reveal(date)
```

### Common transitions

| Function | Use for |
|----------|---------|
| `transition_time(t)` | continuous time variable |
| `transition_states(s)` | discrete steps / stages |
| `transition_reveal(t)` | reveal a line over time, keep prior segments |
| `transition_filter()` | cycle through data subsets |
| `transition_layers()` | add layers one at a time |

### Renderers

| Renderer | Output | Requires |
|----------|--------|----------|
| `gifski_renderer()` | GIF | `gifski` package + system lib |
| `av_renderer()` | MP4 | `av` package + ffmpeg |
| `magick_renderer()` | GIF | `magick` package |
| `file_renderer()` | individual frames | none |

### Gotchas

- Renders are slow. Develop with a small `nframes` (e.g. 30) and bump up only
  for the final export.
- `gifski_renderer()` requires the `gifski` system library. For `mp4`, use
  `av_renderer()` (requires `av` package + ffmpeg).
- Save with `anim_save()`, not `ggsave()`. `ggsave` only handles static plots.
- `transition_time` requires a numeric or date variable; coerce factors first.
