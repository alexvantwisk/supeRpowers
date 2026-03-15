# gtsummary Themes Reference

Complete guide to gtsummary theming: built-in journal themes, compact
variants, custom themes, language settings, and theme stacking.

---

## Built-In Themes

### Journal Themes

Apply **before** building any table in a session:

```r
library(gtsummary)

# JAMA — no bold, specific p-value formatting
theme_gtsummary_journal("jama")

# Lancet — bold p-values, specific CI format
theme_gtsummary_journal("lancet")

# NEJM — continuous variables as median [IQR] by default
theme_gtsummary_journal("nejm")

# The BMJ
theme_gtsummary_journal("bmj")

# Quarterly Journal of Economics
theme_gtsummary_journal("qjecon")
```

| Theme | Default continuous | P-value style | Notes |
|-------|-------------------|---------------|-------|
| jama | Mean (SD) | <0.001 threshold | No bold labels |
| lancet | Median (IQR) | XX.X format | Bold p < 0.05 |
| nejm | Median (IQR) | <0.001 threshold | Compact spacing |
| bmj | Mean (SD) | Exact | Bold headers |

### Compact and Utility Themes

```r
# Compact — reduced padding, smaller font, for supplements
theme_gtsummary_compact()

# Printer-friendly — removes color, uses black/white styling
theme_gtsummary_printer_friendly()

# Language — change default labels
theme_gtsummary_language(
  language       = "es",      # ISO 639-1 code ("fr", "de", "zh-cn", etc.)
  decimal.mark   = ",",
  big.mark       = "."
)
```

---

## Stacking Themes

Multiple themes can be stacked — last applied wins on conflicts:

```r
# Compact JAMA theme
theme_gtsummary_journal("jama")
theme_gtsummary_compact()

# Now build table — both themes are active
trial |>
  tbl_summary(by = trt) |>
  add_p() |>
  bold_labels()
```

Reset all themes to defaults:

```r
reset_gtsummary_theme()
```

---

## Custom Theme Creation

Use `set_gtsummary_theme()` with a named list of gtsummary function
arguments to override defaults project-wide:

```r
my_theme <- list(
  # tbl_summary defaults
  "tbl_summary-str:default_con_type"  = "continuous2",
  "tbl_summary-str:continuous2_stats" = c(
    "{median} ({p25}, {p75})",
    "{min}, {max}",
    "{N_nonmiss}"
  ),
  "tbl_summary-str:categorical_stat"  = "{n} / {N} ({p}%)",

  # add_p defaults
  "add_p.tbl_summary-attr:test.continuous_by2" = "t.test",

  # tbl_regression defaults
  "tbl_regression-str:coef_header"    = "OR",

  # Styling
  "pkgwide-str:ci.sep"                = ", ",
  "pkgwide-fn:pvalue_fun"             = label_style_pvalue(digits = 3)
)

set_gtsummary_theme(my_theme)
```

### Common Customizable Keys

| Key pattern | Controls |
|-------------|----------|
| `tbl_summary-str:default_con_type` | Default stat type: `"continuous"` or `"continuous2"` |
| `tbl_summary-str:continuous_stat` | Stat for `continuous` type |
| `tbl_summary-str:continuous2_stats` | Stats for `continuous2` type (vector = multiple rows) |
| `tbl_summary-str:categorical_stat` | Stat for categorical variables |
| `pkgwide-str:ci.sep` | CI separator (default `", "`) |
| `pkgwide-fn:pvalue_fun` | Global p-value formatter |
| `pkgwide-fn:percent_fun` | Global percent formatter |
| `add_p.tbl_summary-attr:test.continuous_by2` | Default 2-group continuous test |
| `add_p.tbl_summary-attr:test.categorical` | Default categorical test |

---

## Statistic Display Patterns

### Glue-style stat strings

```r
# Single-row display
tbl_summary(statistic = all_continuous() ~ "{mean} ({sd})")
tbl_summary(statistic = all_continuous() ~ "{median} ({p25}, {p75})")
tbl_summary(statistic = all_continuous() ~ "{mean} (95% CI {conf.low}, {conf.high})")

# Multi-row display (continuous2 type)
tbl_summary(
  type      = all_continuous() ~ "continuous2",
  statistic = all_continuous() ~ c(
    "N = {N_nonmiss}",
    "{median} ({p25}, {p75})",
    "{min}, {max}"
  )
)

# Categorical
tbl_summary(statistic = all_categorical() ~ "{n} ({p}%)")
tbl_summary(statistic = all_categorical() ~ "{n} / {N} ({p}%)")
```

### Available Stat Tokens

**Continuous:** `{mean}`, `{sd}`, `{median}`, `{p25}`, `{p75}`, `{min}`,
`{max}`, `{sum}`, `{var}`, `{N_obs}`, `{N_nonmiss}`, `{N_miss}`,
`{p_nonmiss}`, `{p_miss}`, `{conf.low}`, `{conf.high}`

**Categorical:** `{n}`, `{N}`, `{p}`, `{N_obs}`, `{N_nonmiss}`, `{N_miss}`

---

## Applying Themes Within a Pipeline

```r
# Method: wrap table build in withr::with_options for scoped theme
withr::with_options(
  list(gtsummary.theme = list(
    "tbl_summary-str:default_con_type" = "continuous2",
    "tbl_summary-str:continuous2_stats" = c("{median} ({p25}, {p75})", "n = {N_nonmiss}")
  )),
  {
    trial |>
      tbl_summary(by = trt) |>
      add_p() |>
      bold_labels()
  }
)
```

---

## Language Customization

Override specific label strings without changing language:

```r
set_gtsummary_theme(list(
  "pkgwide-str:stat_label"           = "Summary Statistics",
  "tbl_summary-str:overall_col_label" = "All Participants (N = {N})",
  "add_p-str:addp_col_label"         = "P value"
))
```

Supported language codes: `"af"`, `"de"`, `"en"` (default), `"es"`, `"fr"`,
`"gu"`, `"hi"`, `"hy"`, `"ja"`, `"ko"`, `"mr"`, `"nl"`, `"pt"`, `"pt_BR"`,
`"ro"`, `"ru"`, `"sv"`, `"sk"`, `"th"`, `"tr"`, `"uk"`, `"vi"`, `"zh-cn"`,
`"zh-tw"`.
