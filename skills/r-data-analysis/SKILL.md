---
name: r-data-analysis
description: >
  Use when working with data wrangling, cleaning, transformation, or pipelines
  in R using dplyr, tidyr, readr, lubridate, stringr, or forcats. Provides
  expert guidance on tidy data principles, column manipulation, reshaping,
  joins, type conversion, string and date processing, and factor handling.
  Triggers: data wrangling, data cleaning, data transformation, dplyr, tidyr,
  readr, mutate, filter, pivot, join, reshape, stringr, forcats, lubridate, pipe.
  Do NOT use for statistical modeling or hypothesis testing — use r-stats instead.
  Do NOT use for performance optimization of large datasets — use r-performance instead.
---

# R Data Analysis

Tidyverse-first data wrangling, cleaning, and transformation in R.
All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/dplyr-patterns.md` for advanced across()/pick()/window function recipes
- Read `references/join-guide.md` for complex join strategies and decision trees

**Agent dispatch:** When analysis crosses into statistical modeling (regression,
hypothesis testing, mixed models), hand off to the **r-statistician** agent.
If the r-statistician agent is not yet available, provide basic modeling
guidance inline.

---

## Data Import with readr

```r
df <- read_csv("data/sales.csv")                  # basic import
df <- read_tsv("data/results.tsv")                 # tab-delimited

# Explicit column types (always do this in production)
df <- read_csv("data/sales.csv", col_types = cols(
  id = col_integer(), date = col_date(format = "%Y-%m-%d"),
  amount = col_double(), category = col_character()
))

spec(read_csv("data/sales.csv", n_max = 0))        # inspect spec first

# Messy files
df <- read_csv("data/messy.csv",
  na = c("", "NA", "N/A", "null", "-"), skip = 2,
  locale = locale(encoding = "latin1")
)
```

Always specify `col_types` for production code — silent type guessing causes
subtle bugs downstream.

---

## dplyr Core Verbs

```r
result <- sales |>
  filter(year >= 2023, !is.na(revenue)) |>
  select(region, product, revenue, quantity) |>
  mutate(unit_price = revenue / quantity) |>
  summarise(total_revenue = sum(revenue), .by = c(region, product))

# Top 3 products per region
sales |>
  summarise(total = sum(revenue), .by = c(region, product)) |>
  arrange(region, desc(total)) |>
  slice_head(n = 3, by = region)
```

### across, pick, reframe

```r
# Multiple functions across numeric columns
df |> summarise(
  across(where(is.numeric), list(mean = mean, sd = sd), na.rm = TRUE),
  .by = group
)

# Rename output with .names glue syntax
df |> mutate(across(c(x, y, z), \(col) col / max(col), .names = "{.col}_scaled"))

# Multi-row summaries with reframe
df |> reframe(
  quantile = c(0.25, 0.5, 0.75),
  value = quantile(score, c(0.25, 0.5, 0.75)),
  .by = group
)
```

---

## tidyr Reshaping

```r
# Wide to long
long_df <- wide_df |>
  pivot_longer(cols = starts_with("q"), names_to = "quarter",
               values_to = "sales", names_prefix = "q")

# Long to wide
wide_df <- long_df |>
  pivot_wider(names_from = quarter, values_from = sales, values_fill = 0)

# Split delimited columns
df |> separate_wider_delim(full_name, delim = " ", names = c("first", "last"))

# Nest / unnest for group-level operations
nested <- df |>
  nest(.by = group) |>
  mutate(model = map(data, \(d) lm(y ~ x, data = d)))
nested |> unnest(data)

# Fill missing values downward / replace NAs
df |> fill(category, .direction = "down")
df |> replace_na(list(score = 0, label = "unknown"))
```

---

## Joins

Use `join_by()` for all joins — supports equality and inequality conditions.

```r
orders |> left_join(customers, join_by(customer_id))
sales |> inner_join(targets, join_by(region, year))

# Filtering joins — no columns added
orders |> semi_join(active_customers, join_by(customer_id))   # keep matches
orders |> anti_join(active_customers, join_by(customer_id))   # keep orphans
```

Use `left_join()` to preserve all left-side rows (most common),
`inner_join()` when both sides must match, `anti_join()` to find orphans.
Read `references/join-guide.md` for inequality joins and complex strategies.

---

## String Manipulation with stringr

```r
df |>
  mutate(
    clean_name = str_to_lower(name) |> str_trim() |> str_squish(),
    has_email = str_detect(contact, "@"),
    domain = str_extract(email, "(?<=@)[^.]+"),
    parts = str_split(tags, ",\\s*")
  ) |>
  filter(str_starts(code, "PRD"))
```

Key functions: `str_detect()`, `str_extract()`, `str_replace()`,
`str_remove()`, `str_split()`, `str_c()`, `str_glue()`, `str_pad()`.

---

## Factor Handling with forcats

```r
df |>
  mutate(
    category = fct_reorder(category, revenue, .fun = median),       # by variable
    category = fct_lump_n(category, n = 5, other_level = "Other"),  # lump rare
    priority = fct_relevel(priority, "high", "medium", "low"),      # manual order
    status = fct_recode(status, Active = "A", Inactive = "I")       # recode
  )
```

---

## Date/Time with lubridate

```r
df |>
  mutate(
    date = ymd(date_string),
    datetime = ymd_hms(timestamp),
    year = year(date), month = month(date, label = TRUE),
    weekday = wday(date, label = TRUE), quarter = quarter(date),
    days_ago = as.integer(today() - date),
    next_month = date + months(1),
    interval_days = interval(start_date, end_date) / days(1)
  )
```

Use `floor_date()` / `ceiling_date()` for rounding to periods.

---

## Missing Data Strategies

```r
# Diagnose
df |> summarise(across(everything(), \(x) sum(is.na(x))))

# Remove rows with any NA in key columns
df |> drop_na(revenue, date)

# Replace NAs — coalesce takes first non-NA across columns
df |> mutate(
  score = replace_na(score, 0),
  label = coalesce(label, backup_label, "unknown")
)

# Fill within groups (time series)
df |>
  arrange(group, date) |>
  mutate(value = fill(value, .direction = "down"), .by = group)
```

---

## When to Use data.table

Consider `data.table` when: dataset >1M rows, memory-constrained, or
performance-critical inner loops. `fread()`/`fwrite()` are significantly
faster for file I/O.

```r
library(data.table)
dt <- fread("large_data.csv")
result <- dt[year >= 2023, .(total = sum(revenue)), by = .(region, product)]
```

For most analysis under 1M rows, dplyr is clearer and preferred.

---

## Gotchas

| Trap | Why It Fails | Fix |
|------|-------------|-----|
| `%>%` instead of `|>` | Convention violation; base pipe is project standard | Always use `|>` — never `%>%` |
| Omitting `col_types` in `read_csv()` | Silent type guessing causes subtle downstream bugs | Always specify `col_types` explicitly in production code |
| `=` for assignment | Convention violation; `<-` is project standard | Use `<-` for assignment, `=` only in function arguments |
| Joining without checking duplicates | Silent row multiplication when join keys are not unique | Run `count()` on join keys first; assert no duplicates |
| `.` placeholder with `|>` | Base pipe does not support `.` placeholder like magrittr | Use anonymous function: `x |> (\(d) lm(y ~ x, data = d))()` |
| Forgetting `ungroup()` | Grouped data frame silently changes downstream `mutate()`/`summarise()` behavior | Use `.by` argument instead, or call `ungroup()` explicitly |
| `gather()`/`spread()` | Deprecated; superseded by `pivot_longer()`/`pivot_wider()` | Use `pivot_longer()` and `pivot_wider()` exclusively |
| Scope creep | Claude rewrites entire pipeline when asked to fix one step | Fix only the identified issue; show minimal diff |

---

## Examples

### 1. Clean and summarise survey data
**Prompt:** "Compute average satisfaction by department, excluding incomplete."

```r
survey <- read_csv("data/survey_results.csv", col_types = cols(
  employee_id = col_integer(), department = col_character(),
  satisfaction = col_double(), completed = col_logical()
))

survey |>
  filter(completed) |>
  drop_na(satisfaction) |>
  summarise(avg = mean(satisfaction), n = n(), .by = department) |>
  arrange(desc(avg))
```

### 2. Reshape wide time-series data
**Prompt:** "Monthly columns (jan-dec) need to be long for plotting."

```r
wide_data |>
  pivot_longer(cols = jan:dec, names_to = "month", values_to = "value") |>
  mutate(month = fct_relevel(month, month.abb |> str_to_lower()))
```

### 3. Find customers who never purchased
**Prompt:** "Which customers have zero orders?"

```r
customers |> anti_join(orders, join_by(customer_id))
```

### 4. Standardize numeric columns by group
**Prompt:** "Z-score all numeric columns within each group."

```r
df |> mutate(
  across(where(is.numeric), \(x) (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)),
  .by = group
)
```

### 5. Date filtering with string cleanup
**Prompt:** "Last 90 days, clean names, weekly totals by region."

```r
sales |>
  filter(date >= today() - days(90)) |>
  mutate(name = str_to_title(name) |> str_squish(), week = floor_date(date, "week")) |>
  summarise(weekly_total = sum(amount, na.rm = TRUE), .by = c(region, week)) |>
  arrange(region, week)
```
