---
name: r-cmd-debug
description: >
  Use when starting a systematic debugging session for R code. Orchestrates
  r-debugging and r-tdd skills with the r-code-reviewer agent through a guided
  reproduce-isolate-diagnose-fix-verify workflow. Invoke as /r-cmd-debug.
  Triggers: debug this, find bug, fix error, diagnose issue, start debugging,
  something is wrong, unexpected behavior, wrong result.
  Do NOT use for debugging tool reference — use r-debugging instead.
  Do NOT use for writing tests outside a bug fix — use r-cmd-tdd-cycle instead.
---

# Debug

Guided workflow: reproduce, isolate, diagnose, fix, regression test, verify.

**First question:** Is this interactive script code or package code? The strategy differs — package code has formal test infrastructure and namespacing; scripts need ad-hoc reprex and manual verification.

## Prerequisites

- Observable bug: error message, wrong result, or unexpected behavior
- Access to the code that triggers the bug
- Ability to run the code (R session available)

## Steps

### Step 1: Reproduce
**Skill:** `r-debugging`
**Action:** Create a minimal, self-contained reprex that triggers the bug. Strip to smallest data and code that still fails. Run 3x to confirm deterministic.
**Gate:** Bug reproduced reliably. Reprex is self-contained.

### Step 2: Isolate
**Skill:** `r-debugging`
**Action:** Binary search through the pipeline — comment out the bottom half, check if error persists, recurse. Insert `browser()` at suspect locations to inspect state.
**Gate:** Failure narrowed to a specific function and line.

### Step 3: Diagnose
**Skill:** `r-debugging`
**Action:** Inspect the call stack (`rlang::last_trace()`). Check common gotchas: factor-to-numeric, NSE scoping, vector recycling, NULL propagation, floating point. Identify root cause — not just the symptom.
**Gate:** Root cause identified and documented (one sentence: "X happens because Y").

### Step 4: Fix
**Action:** Apply the minimal change that addresses the root cause. Do not refactor surrounding code. Re-run the exact reprex from Step 1.
**Gate:** Reprex from Step 1 no longer fails. No new warnings.

### Step 5: Regression test
**Skill:** `r-tdd`
**Action:** Write a test that would have caught this bug. For packages: place in `tests/testthat/test-{relevant-file}.R`. For scripts: create a lightweight test or add assertion.
**Gate:** Test passes with the fix. Test fails when fix is reverted.

### Step 6: Verify
**Agent:** `r-code-reviewer` (scope: full)
**Action:** Review the fix for correctness, side effects, and style. Run `devtools::check()` for packages or full script for interactive code.
**Gate:** No CRITICAL findings. Fix is minimal and targeted.

## Abort Conditions

- Cannot reproduce the bug after 3 attempts — ask user for more context (session info, exact input data, environment).
- Root cause is in an external package — file upstream issue, document workaround.
- Fix requires architectural change beyond scope of bug fix — stop and re-plan as a feature.

## Examples

### Example: Function returns wrong result for edge case

**Prompt:** "My `calc_growth()` returns NA for some groups, but I expect a number."

**Flow:** Reproduce (create tibble with single-row group) → Isolate (browser() reveals `lag()` returns NA for first row in group) → Diagnose (root cause: single-row groups have no previous value to lag from) → Fix (guard with `if (n() > 1)`) → Regression test → Verify

```r
# Step 1 — Reproduce
test_data <- tibble::tibble(
  group = c("A", "A", "B"),
  date = as.Date(c("2024-01-01", "2024-02-01", "2024-01-01")),
  value = c(100, 120, 50)
)
calc_growth(test_data)
# Group B has 1 row → lag() returns NA → growth is NA

# Step 4 — Fix
calc_growth <- function(data) {
  data |>
    arrange(group, date) |>
    mutate(
      growth = if (n() > 1) (value - lag(value)) / lag(value) * 100 else NA_real_,
      .by = group
    )
}
```

### Example: Error only in non-interactive mode

**Prompt:** "Script runs fine in RStudio but fails with `Rscript --vanilla`."

**Flow:** Reproduce (run with `Rscript --vanilla script.R`) → Isolate (error at line using `.libPaths()` that differs between interactive/batch) → Diagnose (package installed in user library not on batch R's search path) → Fix (add `renv::activate()` at script top or use explicit library path) → Regression test → Verify
