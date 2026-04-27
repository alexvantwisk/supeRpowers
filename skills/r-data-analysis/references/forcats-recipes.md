# forcats Recipes

Factor manipulation: reorder, lump, recode, collapse, and explicit NA
handling. Always prefer forcats over base `factor(..., levels = ...)`
gymnastics. All code uses `|>` and `<-`.

---

## Reorder Family

```r
# Reorder by a summary statistic — most common for plots
df |>
  mutate(category = fct_reorder(category, value, .fun = median)) |>
  ggplot(aes(category, value)) + geom_boxplot()

# Reorder by frequency
df |> mutate(category = fct_infreq(category))

# Reorder by order of first appearance in the data
df |> mutate(category = fct_inorder(category))

# Manually move levels to the front
df |> mutate(category = fct_relevel(category, "Control", "Placebo"))

# Reverse current order
df |> mutate(category = fct_rev(category))

# Reorder by a second variable in a 2D plot (e.g. interaction plots)
df |> mutate(x = fct_reorder2(x, time, value))
```

**Rule:** For a boxplot or bar chart, `fct_reorder()` by the displayed
statistic gives a self-sorting plot — no manual `levels =` argument needed.

---

## Lump Family — Collapse Rare Levels

```r
# Keep the top n by frequency; collapse the rest into "Other"
df |> mutate(country = fct_lump_n(country, n = 5))

# Keep levels with at least k observations
df |> mutate(country = fct_lump_min(country, min = 50))

# Keep levels covering a proportion of the data
df |> mutate(country = fct_lump_prop(country, prop = 0.05))

# Custom "Other" label
df |> mutate(country = fct_lump_n(country, n = 5, other_level = "Rest"))
```

`fct_lump_n()` is the workhorse — pair it with `fct_infreq()` to put levels
in descending frequency order before plotting.

---

## Modification: Collapse, Recode, Other

```r
# Collapse multiple levels into named groups
df |> mutate(
  region = fct_collapse(region,
    North = c("ME", "NH", "VT", "MA"),
    South = c("FL", "GA", "AL"),
    other_level = "Rest"
  )
)

# 1-to-1 renaming (new = old)
df |> mutate(group = fct_recode(group,
  "Treatment" = "trt",
  "Control"   = "ctrl"
))

# Collapse a list of levels into a single "Other"
df |> mutate(category = fct_other(category, keep = c("A", "B", "C")))

# Add levels that don't yet appear in the data
df |> mutate(arm = fct_expand(arm, "Placebo"))
```

---

## Missing Data in Factors

```r
# Convert NA to an explicit factor level (visible in tables/plots)
df |> mutate(group = fct_na_value_to_level(group, level = "Missing"))

# Drop unused levels (e.g. after filtering)
df |> mutate(group = fct_drop(group))
```

`fct_na_value_to_level()` (renamed from `fct_explicit_na()` in forcats >=
1.0) makes NA a first-class level so it appears in `count()`, `tabyl()`,
and ggplot legends.

---

## Gotchas

| Trap | Fix |
|------|-----|
| `factor(x, levels = sort(unique(x)))` for reordering | Use `fct_reorder()` / `fct_infreq()` — declarative |
| `levels(x) <- new` mutates in place | Use `fct_recode()` — immutable, named, explicit |
| Filtered data still has unused factor levels | `fct_drop()` to remove unused levels |
| NAs invisible in factor counts | `fct_na_value_to_level()` to make them explicit |
| `fct_lump()` (deprecated alias) | Use `fct_lump_n()` / `fct_lump_min()` / `fct_lump_prop()` |
| Naming `...` arguments in `fct_relevel()` / `fct_cross()` / `fct_expand()` | Errors since forcats 1.0.0 — pass levels positionally or via a vector |
| `fct_lump_n()` partial arg name `n_min` etc. | Removed in 1.0.0 — use the full argument name |
| Reorder lost after a join | Re-apply `fct_reorder()` after the join, or convert factor to character before joining and back after |
| Different factor encodings between data sets | Standardise to character before joins; convert to factor at the plotting stage |
