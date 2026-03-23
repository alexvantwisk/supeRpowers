#!/usr/bin/env Rscript
# check_assumptions.R — Run assumption checks on a fitted lm object
#
# Usage:  Rscript check_assumptions.R path/to/model.rds
#
# Tests: Shapiro-Wilk (normality), Breusch-Pagan (heteroscedasticity),
# VIF (multicollinearity). Prints PASS/WARN per check (alpha = 0.05).

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  cat("Usage: Rscript check_assumptions.R path/to/model.rds\n")
  quit(status = 1)
}

model_path <- args[1]
if (!file.exists(model_path)) stop(sprintf("File not found: %s", model_path))

model <- tryCatch(readRDS(model_path),
  error = function(e) stop(sprintf("Could not read RDS: %s", e$message)))
if (!inherits(model, "lm")) stop("Object is not a fitted lm model.")

alpha <- 0.05
cat(sprintf("Assumption checks for: %s (alpha = %.2f)\n\n", model_path, alpha))

# 1. Shapiro-Wilk normality
resids <- residuals(model)
n <- length(resids)
if (n >= 3 && n <= 5000) {
  sw <- shapiro.test(resids)
  cat(sprintf("  [%s] Shapiro-Wilk normality (p = %.4f)\n",
    if (sw$p.value >= alpha) "PASS" else "WARN", sw$p.value))
} else {
  cat("  [SKIP] Shapiro-Wilk — requires 3-5000 observations\n")
}

# 2. Breusch-Pagan heteroscedasticity
if (requireNamespace("lmtest", quietly = TRUE)) {
  bp <- lmtest::bptest(model)
  cat(sprintf("  [%s] Breusch-Pagan heteroscedasticity (p = %.4f)\n",
    if (bp$p.value >= alpha) "PASS" else "WARN", bp$p.value))
} else {
  cat("  [SKIP] Breusch-Pagan — install lmtest package\n")
}

# 3. VIF multicollinearity
n_pred <- length(attr(terms(model), "term.labels"))
if (n_pred < 2) {
  cat("  [SKIP] VIF — requires 2+ predictors\n")
} else if (requireNamespace("car", quietly = TRUE)) {
  vif_vals <- tryCatch(car::vif(model), error = function(e) NULL)
  if (!is.null(vif_vals)) {
    cat(sprintf("  [%s] VIF multicollinearity (max = %.2f)\n",
      if (max(vif_vals) < 5) "PASS" else "WARN", max(vif_vals)))
  } else {
    cat("  [SKIP] VIF — could not compute (aliased coefficients?)\n")
  }
} else {
  cat("  [SKIP] VIF — install car package\n")
}
cat("\nDone.\n")
