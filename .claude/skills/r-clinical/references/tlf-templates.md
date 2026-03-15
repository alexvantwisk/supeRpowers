# TLF Generation Templates

Ready-to-use patterns for clinical trial Tables, Listings, and Figures.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

---

## Table 1 — Demographics & Baseline Characteristics

Standard summary of subject demographics by treatment arm using `gtsummary`.

```r
library(gtsummary)
library(dplyr)

tbl_demographics <- adsl |>
  filter(ITTFL == "Y") |>
  select(TRT01P, AGE, AGEGR1, SEX, RACE, COUNTRY, ECOG) |>
  tbl_summary(
    by = TRT01P,
    statistic = list(
      all_continuous() ~ "{mean} ({sd})",
      all_categorical() ~ "{n} ({p}%)"
    ),
    digits = list(all_continuous() ~ 1),
    label = list(
      AGE ~ "Age (years)",
      AGEGR1 ~ "Age group",
      SEX ~ "Sex",
      RACE ~ "Race",
      COUNTRY ~ "Country",
      ECOG ~ "ECOG Performance Status"
    ),
    missing = "no"
  ) |>
  add_overall(last = TRUE) |>
  add_n() |>
  bold_labels() |>
  modify_header(label = "**Characteristic**") |>
  modify_caption("Table 1. Demographic and Baseline Characteristics (ITT Population)")
```

For p-values (descriptive, not inferential — include with caution per
regulatory convention): add `add_p()`.

Export to Word/RTF:

```r
tbl_demographics |>
  as_flex_table() |>
  flextable::save_as_docx(path = "output/tlf/table_1_demographics.docx")
```

---

## AE Summary Table

Treatment-emergent adverse events by SOC and PT, sorted by frequency.

```r
library(dplyr)
library(tidyr)
library(gtsummary)

# Count subjects with >= 1 TEAE overall
n_subj <- adsl |> filter(SAFFL == "Y") |> count(TRT01P, name = "N")

# Summary of TEAEs (any, serious, related)
ae_summary <- adae |>
  filter(TRTEMFL == "Y") |>
  group_by(TRT01P) |>
  summarise(
    n_any_ae = n_distinct(USUBJID),
    n_sae = n_distinct(USUBJID[AESER == "Y"]),
    n_related = n_distinct(USUBJID[AEREL %in% c("PROBABLE", "POSSIBLE", "DEFINITE")]),
    n_disc = n_distinct(USUBJID[AEACN == "DRUG WITHDRAWN"]),
    .groups = "drop"
  ) |>
  left_join(n_subj, by = "TRT01P") |>
  mutate(across(c(n_any_ae, n_sae, n_related, n_disc),
                \(x) glue::glue("{x} ({round(100 * x / N, 1)}%)"),
                .names = "{.col}_pct"))

# AE by SOC/PT (subjects with >= 5% frequency in any arm)
ae_by_pt <- adae |>
  filter(TRTEMFL == "Y") |>
  distinct(USUBJID, TRT01P, AEBODSYS, AEDECOD) |>
  count(TRT01P, AEBODSYS, AEDECOD) |>
  left_join(n_subj, by = "TRT01P") |>
  mutate(pct = 100 * n / N) |>
  pivot_wider(names_from = TRT01P, values_from = c(n, pct), values_fill = 0) |>
  filter(if_any(starts_with("pct_"), \(x) x >= 5)) |>
  arrange(AEBODSYS, desc(rowMeans(across(starts_with("pct_")))))
```

---

## Efficacy Endpoint Table

Primary and secondary endpoint results (response rates, HR, medians).

```r
library(survival)
library(broom)
library(dplyr)

# Overall response rate (primary endpoint)
orr_table <- adrs |>
  filter(PARAMCD == "BRSRSP", ANL01FL == "Y") |>
  count(TRT01P, AVALC) |>
  group_by(TRT01P) |>
  mutate(
    N = sum(n),
    pct = 100 * n / N
  ) |>
  filter(AVALC %in% c("CR", "PR")) |>
  group_by(TRT01P) |>
  summarise(
    responders = sum(n), N = first(N),
    orr_pct = sum(pct),
    .groups = "drop"
  )

# Exact 95% CI for ORR (Clopper-Pearson)
orr_ci <- orr_table |>
  mutate(
    ci = purrr::map2(responders, N, \(x, n) {
      binom.test(x, n)$conf.int * 100
    }),
    ci_lo = purrr::map_dbl(ci, 1),
    ci_hi = purrr::map_dbl(ci, 2)
  ) |>
  select(-ci)

# Median OS with 95% CI (per arm)
os_km <- survfit(Surv(AVAL, CNSR == 0) ~ TRT01P, data = adtte |> filter(PARAMCD == "OS"))
os_summary <- summary(os_km)$table |>
  as.data.frame() |>
  tibble::rownames_to_column("TRT01P") |>
  select(TRT01P, median, `0.95LCL`, `0.95UCL`)

# Cox model for HR
cox_os <- coxph(Surv(AVAL, CNSR == 0) ~ TRT01P, data = adtte |> filter(PARAMCD == "OS")) |>
  tidy(exponentiate = TRUE, conf.int = TRUE) |>
  select(term, estimate, conf.low, conf.high, p.value)
```

---

## Kaplan-Meier Figure with Risk Table

```r
library(survival)
library(survminer)
library(ggplot2)

adtte_os <- adtte |>
  filter(PARAMCD == "OS", ITTFL == "Y") |>
  mutate(TRT01P = factor(TRT01P))

km_fit <- survfit(Surv(AVAL, CNSR == 0) ~ TRT01P, data = adtte_os)

km_plot <- ggsurvplot(
  km_fit,
  data = adtte_os,
  pval = TRUE,
  pval.method = TRUE,
  conf.int = TRUE,
  risk.table = TRUE,
  risk.table.col = "strata",
  risk.table.height = 0.28,
  xlab = "Time (Months)",
  ylab = "Overall Survival Probability",
  title = "Figure 1. Kaplan-Meier Curve for Overall Survival (ITT Population)",
  legend.labs = levels(adtte_os$TRT01P),
  palette = c("#0072B2", "#D55E00"),
  break.time.by = 3,
  xlim = c(0, 24),
  ggtheme = theme_classic(base_size = 11),
  surv.median.line = "hv"
)

# Save at regulatory-quality resolution
ggsave("output/tlf/figure_1_km_os.png",
       plot = print(km_plot), width = 8, height = 6, dpi = 300)
```

---

## Forest Plot — Subgroup Analysis

```r
library(survival)
library(ggplot2)
library(dplyr)

subgroups <- list(
  Overall     = quote(TRUE),
  "Sex: Male" = quote(SEX == "M"),
  "Sex: Female" = quote(SEX == "F"),
  "Age <65"   = quote(AGE < 65),
  "Age >=65"  = quote(AGE >= 65),
  "ECOG 0"    = quote(ECOG == 0),
  "ECOG 1-2"  = quote(ECOG %in% c(1, 2))
)

forest_data <- purrr::imap_dfr(subgroups, \(cond, label) {
  sub_data <- adtte |>
    filter(PARAMCD == "OS", ITTFL == "Y") |>
    filter(!!cond)
  n <- nrow(sub_data)
  if (n < 10) return(NULL)
  fit <- coxph(Surv(AVAL, CNSR == 0) ~ TRT01P, data = sub_data)
  s <- summary(fit)
  tibble::tibble(
    subgroup = label, n = n,
    hr = s$conf.int[1, "exp(coef)"],
    ci_lo = s$conf.int[1, "lower .95"],
    ci_hi = s$conf.int[1, "upper .95"],
    pval = s$coefficients[1, "Pr(>|z|)"]
  )
})

forest_plot <- forest_data |>
  mutate(
    subgroup = forcats::fct_rev(factor(subgroup, levels = rev(names(subgroups)))),
    label_text = glue::glue("{hr |> round(2)} ({ci_lo |> round(2)}-{ci_hi |> round(2)})")
  ) |>
  ggplot(aes(x = hr, y = subgroup)) +
  geom_vline(xintercept = 1, linetype = "dashed", colour = "grey50") +
  geom_errorbarh(aes(xmin = ci_lo, xmax = ci_hi), height = 0.25, linewidth = 0.6) +
  geom_point(aes(size = n), shape = 15, colour = "#0072B2") +
  geom_text(aes(x = 3.5, label = label_text), hjust = 1, size = 3) +
  scale_x_log10(breaks = c(0.25, 0.5, 1, 2, 4)) +
  labs(x = "Hazard Ratio (95% CI)", y = NULL,
       title = "Figure 2. Forest Plot — Overall Survival Subgroup Analysis") +
  theme_classic(base_size = 11) +
  theme(legend.position = "none")

ggsave("output/tlf/figure_2_forest_os.png",
       plot = forest_plot, width = 9, height = 5, dpi = 300)
```

---

## Waterfall Plot — Tumour Response

Best percent change from baseline per subject.

```r
library(ggplot2)
library(dplyr)

waterfall_data <- adrs |>
  filter(PARAMCD == "PCHG", ANL01FL == "Y") |>
  select(USUBJID, TRT01P, AVAL) |>  # AVAL = % change
  arrange(AVAL) |>
  mutate(
    USUBJID = factor(USUBJID, levels = USUBJID),
    response_cat = dplyr::case_when(
      AVAL <= -30 ~ "Response (>=30% decrease)",
      AVAL >= 20  ~ "Progression (>=20% increase)",
      TRUE        ~ "Stable Disease"
    )
  )

waterfall_plot <- waterfall_data |>
  ggplot(aes(x = USUBJID, y = AVAL, fill = response_cat)) +
  geom_col(width = 0.8) +
  geom_hline(yintercept = c(-30, 20), linetype = "dashed",
             colour = c("#009E73", "#D55E00")) +
  scale_fill_manual(values = c(
    "Response (>=30% decrease)" = "#009E73",
    "Stable Disease"            = "#56B4E9",
    "Progression (>=20% increase)" = "#D55E00"
  )) +
  scale_y_continuous(labels = scales::label_percent(scale = 1)) +
  labs(
    x = "Subject", y = "Best % Change from Baseline",
    fill = "Response Category",
    title = "Figure 3. Waterfall Plot — Best Tumour Response"
  ) +
  theme_classic(base_size = 11) +
  theme(axis.text.x = element_blank(), axis.ticks.x = element_blank())

ggsave("output/tlf/figure_3_waterfall.png",
       plot = waterfall_plot, width = 10, height = 5, dpi = 300)
```

---

## CONSORT Flow Diagram

```r
library(DiagrammeR)

consort_diagram <- grViz("
  digraph consort {
    graph [rankdir=TB, fontname=Arial]
    node [shape=box, fontname=Arial, fontsize=11, width=3]

    assessed   [label='Assessed for eligibility\\n(n=XXX)']
    excluded   [label='Excluded (n=XXX)\\n  Not meeting criteria (n=XXX)\\n  Declined to participate (n=XXX)\\n  Other reasons (n=XXX)']
    rand       [label='Randomised (n=XXX)']
    arm_a_alloc [label='Allocated to Arm A (n=XXX)\\n  Received treatment (n=XXX)\\n  Did not receive (n=XXX)']
    arm_b_alloc [label='Allocated to Arm B (n=XXX)\\n  Received treatment (n=XXX)\\n  Did not receive (n=XXX)']
    arm_a_fu   [label='Lost to follow-up (n=XXX)\\nDiscontinued (n=XXX)']
    arm_b_fu   [label='Lost to follow-up (n=XXX)\\nDiscontinued (n=XXX)']
    arm_a_itt  [label='Analysed — ITT (n=XXX)']
    arm_b_itt  [label='Analysed — ITT (n=XXX)']

    assessed -> excluded [style=invis]
    assessed -> rand
    assessed -> excluded [constraint=false, style=dashed]
    rand -> arm_a_alloc
    rand -> arm_b_alloc
    arm_a_alloc -> arm_a_fu
    arm_b_alloc -> arm_b_fu
    arm_a_fu -> arm_a_itt
    arm_b_fu -> arm_b_itt
  }
")

# Export to PNG via DiagrammeRsvg + rsvg
DiagrammeRsvg::export_svg(consort_diagram) |>
  chartr("\n", " ", x = _) |>   # flatten for rsvg
  rsvg::rsvg_png("output/tlf/figure_0_consort.png", width = 900)
```

Replace `XXX` placeholders with counts derived from ADSL:

```r
n_assessed  <- nrow(dm)
n_excluded  <- nrow(dm) - nrow(adsl |> filter(RANDFL == "Y"))
n_rand      <- nrow(adsl |> filter(RANDFL == "Y"))
n_arm_a     <- nrow(adsl |> filter(TRT01P == "Arm A"))
n_arm_b     <- nrow(adsl |> filter(TRT01P == "Arm B"))
```
