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

### Add a censoring tick

```r
ggsurvfit(linewidth = 1) +
  add_censor_mark(size = 2, alpha = 0.6) +
  add_confidence_interval()
```

### Why ggsurvfit over survminer

- ggplot2-native: composes with `+`, themes, scales, `patchwork`.
- Active maintenance; survminer is in low-activity mode.
- Risktable is a layer (`add_risktable`) instead of a separate object glued
  with `cowplot::plot_grid`.
- Works directly with the modern `survfit2()` interface.

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

For RR / HR plots, swap axis labels and reference line as needed. For pooled
estimates with a diamond, add a separate `geom_point(shape = 18, size = 5)`
on the pooled row.

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

---

## See also

- `bayesplot` — `ggplot2`-based posterior diagnostics for Stan / brms.
- `ggcorrplot` — correlation matrix heatmaps.
- `ggalluvial` — alluvial / sankey-style flow diagrams.
- `ggraph` — network and tree visualizations.

These are out of scope for this skill but slot into ggplot2 workflows
naturally.
