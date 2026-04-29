---
description: Guided data analysis pipeline — import, clean, explore, model, visualize, report
---


# Analysis Pipeline

Guided workflow: import, clean, explore, model, visualize, report.

## Prerequisites

- Data file accessible (CSV, Excel, database, or API)
- Clear research question or analysis goal
- R session with tidyverse installed

## Progress Tracking

Use TaskCreate at the start of this workflow — one task per phase below. Mark each `in_progress` when starting, `completed` when its gate passes.

- "Phase 1: Import data"
- "Phase 2: Clean data"
- "Phase 3: Explore data"
- "Phase 4: Model"
- "Phase 5: Visualize findings"
- "Phase 6: Report"

Surfaces the orchestration shape to the user and prevents skipped phases or premature completion claims.

## Steps

### Step 1: Import
**Skill:** `r-data-analysis`
**Action:** Read data with explicit `col_types`. Inspect with `glimpse()` and `skimr::skim()`. Document dimensions, column types, and any import warnings.
**Gate:** Data loaded successfully. Row count and column types confirmed.

### Step 2: Clean
**Skill:** `r-data-analysis`
**Action:** Handle missing values (diagnose with `across(everything(), \(x) sum(is.na(x)))`). Fix types, rename columns to snake_case, remove duplicates. Document cleaning decisions.
**Gate:** No unexpected NAs in key columns. Types correct. No duplicates in ID columns.

### Step 3: Explore
**Skill:** `r-data-analysis` + `r-visualization`
**Action:** Compute summary statistics (`.by` grouping). Plot distributions, relationships, and potential outliers. Identify key patterns and form hypotheses.
**Gate:** Key patterns identified. Research questions refined.

### Step 4: Model
**Skill:** `r-stats`
**Agent:** `r-statistician` — dispatch for model selection, assumption verification, or interpretation guidance
**Action:** Fit appropriate model(s). Check assumptions (residual plots, normality, homoscedasticity). Interpret coefficients and confidence intervals.
**Gate:** Model assumptions met (or documented violations with justification). Results interpretable.

### Step 5: Visualize
**Skill:** `r-visualization`
**Action:** Create publication-quality plots of key findings using ggplot2. Use `patchwork` for multi-panel layouts. Apply consistent theme.
**Gate:** Plots communicate findings clearly. Axes labeled, legends readable.

### Step 6: Report
**Action:** Summarize findings in plain language. Document limitations, assumptions, and next steps. Structure as: question → method → result → interpretation.
**Gate:** Narrative matches evidence. Limitations acknowledged.

## Abort Conditions

- Data quality too poor to proceed (>50% missing in key variables) — report to user, suggest data collection improvements.
- Model assumptions severely violated with no reasonable alternative — document and present descriptive analysis only.
- Statistical findings contradicted by exploratory analysis — re-examine data and model, do not proceed until resolved.

## Examples

### Example: Exploratory analysis of a CSV dataset

**Prompt:** "Analyze sales_data.csv — what drives revenue by region?"

**Flow:** Import (read_csv with col_types) → Clean (handle NAs in revenue, fix date types) → Explore (revenue distributions by region, correlation with predictors) → Model (linear regression: revenue ~ region + season + marketing_spend) → Visualize (coefficient plot + regional trends) → Report

```r
# Step 1 — Import
sales <- readr::read_csv("sales_data.csv", col_types = cols(
  region = col_character(), date = col_date(),
  revenue = col_double(), marketing_spend = col_double()
))

# Step 3 — Explore
sales |>
  summarise(
    mean_revenue = mean(revenue, na.rm = TRUE),
    n = n(),
    .by = region
  )
```

### Example: Quick EDA on a new dataset

**Prompt:** "I just got this dataset, help me understand what's in it."

**Flow:** Import → Clean (light touch) → Explore (heavy — distributions, missing patterns, relationships) → Skip Model → Visualize (overview plots) → Report (summary of what the data contains and potential questions)
