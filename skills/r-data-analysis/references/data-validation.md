# Data Validation in Pipelines

Use `pointblank` (or `validate`) to encode rules as code, run them at
ingest, and fail loudly when data drifts. Replaces ad-hoc `stopifnot()`
chains. All code uses `|>` and `<-`.

---

## Boundary: Usage vs Skill Generation

This reference covers **using** pointblank/validate inside a data pipeline.
Questions like *"teach Claude about the pointblank package from its
GitHub repository"* are **skill generation** and route to
`r-package-skill-generator` (see `route-024` in the routing matrix).
Do NOT hand off this material when the user wants the package introduced
as a new skill.

---

## pointblank: create_agent() + interrogate()

```r
library(pointblank)

agent <- create_agent(
  tbl = orders,
  tbl_name = "orders",
  label = "Daily order ingest",
  actions = action_levels(warn_at = 0.05, stop_at = 0.10)
) |>
  col_exists(c("order_id", "customer_id", "amount", "order_date")) |>
  col_is_integer(order_id) |>
  col_vals_not_null(c(order_id, customer_id, amount)) |>
  col_vals_gte(amount, value = 0) |>
  col_vals_in_set(status, set = c("open", "shipped", "cancelled")) |>
  rows_distinct(order_id) |>
  interrogate()

# Programmatic access to pass/fail
agent |> all_passed()                # TRUE if every rule passed
agent |> get_agent_x_list()          # detailed results

# Fail the pipeline on warn/stop thresholds
if (!all_passed(agent)) stop_on_fail()(agent)
```

**Rule:** Pipelines that fan out into reports, ML models, or shipped data
products must validate on ingest. A 1% silent NA leak in a key column is
worse than a loud abort.

---

## Common Rule Functions

| Rule | Catches |
|------|---------|
| `col_exists()` | Schema drift (renamed/dropped columns) |
| `col_is_integer()` / `col_is_numeric()` / `col_is_date()` | Type drift |
| `col_vals_not_null()` | NAs in required columns |
| `col_vals_gte()` / `lte()` / `between()` | Out-of-range numerics |
| `col_vals_in_set()` | Unknown category levels |
| `col_vals_regex()` | Malformed strings (emails, IDs) |
| `rows_distinct()` | Duplicate keys |
| `rows_complete()` | Whole-row NAs |
| `col_vals_expr()` | Arbitrary tidy-eval predicate |

```r
# Combine multiple checks — each is a step
agent <- create_agent(tbl = users) |>
  col_vals_regex(email, regex = "^[^@]+@[^@]+\\.[a-z]{2,}$") |>
  col_vals_between(age, left = 0, right = 130) |>
  col_vals_expr(expr = ~ signup_date <= today()) |>
  interrogate()
```

---

## Action Levels

```r
# Three escalation levels per rule
actions <- action_levels(
  notify_at = 0.01,    # log a notification
  warn_at   = 0.05,    # warn (yellow)
  stop_at   = 0.10     # error (red)
)

agent <- create_agent(tbl = df, actions = actions) |>
  col_vals_not_null(amount) |>
  interrogate()
```

Tune thresholds to your tolerance. For regulated pipelines, use
`stop_at = 0` — any failure aborts.

---

## Reporting

```r
# HTML report — embed in Quarto/RMarkdown for review boards
agent |> get_agent_report()

# Email a summary on failure
agent |> email_blast(to = "data-quality@example.com")

# YAML round-trip — version-controlled rules
agent |> yaml_write(filename = "validation-rules.yml")
read_disk_multiagent("validation-rules.yml")
```

Rule sets stored as YAML can live alongside data-loading code in the
package, get reviewed in PRs, and be applied to multiple tables.

---

## validate Package — Lighter Alternative

```r
library(validate)

rules <- validator(
  amount > 0,
  status %in% c("open", "shipped", "cancelled"),
  !is.na(customer_id)
)

result <- confront(orders, rules)
summary(result)
violating(orders, result)         # rows that failed
```

`validate` is a smaller dependency than pointblank — pick it for packages
where pulling in pointblank is too heavy.

---

## When NOT to Use Validation Rules

- One-off interactive exploration — `glimpse()`, `summary()` are enough
- Inside a function that already takes a typed argument (use cli abort
  instead) — see `rules/r-conventions.md` "Error Handling"
- For statistical assumption checks (normality, homoscedasticity) — those
  belong in `r-stats`, not data validation

---

## Gotchas

| Trap | Fix |
|------|-----|
| `stopifnot()` chains scattered through scripts | Centralise as a pointblank agent — readable, reportable |
| Silent type coercion masking schema drift | `col_is_integer()` / `col_is_date()` catch it at ingest |
| Validation rules drift from the actual data | Version-control rules as YAML; review in PRs |
| Failing one row aborts the whole pipeline | Tune `action_levels(stop_at = 0.05)` — abort only on >5% violation |
| `validate` and `pointblank` mixed in one project | Pick one — they have different idioms |
| Forgetting to call `interrogate()` | Without it, the agent has rules but no results |
| Treating validation as a data-cleaning step | Validation reports problems; cleaning fixes them. Do both, in that order. |
