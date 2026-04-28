#!/usr/bin/env Rscript
# preflight.R -- Fast pre-check pipeline for an R package.
#
# Usage:  Rscript preflight.R [path/to/package]
#
# Runs, in order, the fast checks that should pass on every commit:
#   1. roxygen2::roxygenize()        -- regenerates man/ + NAMESPACE
#   2. lintr::lint_package()         -- style and bug-prone patterns
#   3. spelling::spell_check_package -- typos
#   4. urlchecker::url_check         -- URL validity
#
# Skips the slow R CMD check. Use scripts/check_package.R for that.
# Exits 0 on success, 1 on any failure.

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."

pkg_path <- normalizePath(pkg_path, mustWork = FALSE)
if (!dir.exists(pkg_path)) {
  stop(sprintf("Directory not found: %s", pkg_path))
}
desc_file <- file.path(pkg_path, "DESCRIPTION")
if (!file.exists(desc_file)) {
  stop(sprintf("No DESCRIPTION in %s -- not an R package.", pkg_path))
}

need <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf(
      "Package '%s' required. Install with install.packages(\"%s\").",
      pkg, pkg
    ))
  }
}

results <- list()
record <- function(name, ok, details = "") {
  results[[name]] <<- list(ok = ok, details = details)
  status <- if (ok) "PASS" else "FAIL"
  cat(sprintf("[%s] %s%s\n", status, name,
              if (nzchar(details)) paste0(" -- ", details) else ""))
}

cat(sprintf("\n=== Preflight: %s ===\n\n", pkg_path))

# ---- 1. roxygen2::roxygenize() ----
cat(">> Regenerating man/ and NAMESPACE...\n")
need("roxygen2")
rox_result <- tryCatch(
  roxygen2::roxygenize(pkg_path),
  error = function(e) e
)
if (inherits(rox_result, "error")) {
  record("roxygenize", FALSE, conditionMessage(rox_result))
} else {
  record("roxygenize", TRUE, "man/ + NAMESPACE up to date")
}

# ---- 2. lintr::lint_package() ----
if (requireNamespace("lintr", quietly = TRUE)) {
  cat("\n>> Linting...\n")
  lints <- tryCatch(
    lintr::lint_package(pkg_path),
    error = function(e) e
  )
  if (inherits(lints, "error")) {
    record("lintr", FALSE, conditionMessage(lints))
  } else {
    n <- length(lints)
    record("lintr", n == 0L,
           if (n > 0L) sprintf("%d lint(s); see lintr::lint_package() output", n)
           else "")
  }
} else {
  record("lintr", FALSE, "lintr not installed -- skipping")
}

# ---- 3. spelling::spell_check_package() ----
if (requireNamespace("spelling", quietly = TRUE)) {
  cat("\n>> Spell-checking...\n")
  typos <- tryCatch(
    spelling::spell_check_package(pkg_path),
    error = function(e) e
  )
  if (inherits(typos, "error")) {
    record("spelling", FALSE, conditionMessage(typos))
  } else {
    n <- nrow(typos)
    record("spelling", is.null(n) || n == 0L,
           if (!is.null(n) && n > 0L)
             sprintf("%d potential typos -- review inst/WORDLIST", n)
           else "")
  }
} else {
  record("spelling", FALSE, "spelling not installed -- skipping")
}

# ---- 4. urlchecker::url_check() ----
if (requireNamespace("urlchecker", quietly = TRUE)) {
  cat("\n>> Checking URLs...\n")
  urls <- tryCatch(
    urlchecker::url_check(pkg_path),
    error = function(e) e
  )
  if (inherits(urls, "error")) {
    record("url_check", FALSE, conditionMessage(urls))
  } else {
    n <- nrow(urls)
    record("url_check", is.null(n) || n == 0L,
           if (!is.null(n) && n > 0L) sprintf("%d problematic URLs", n)
           else "")
  }
} else {
  record("url_check", FALSE, "urlchecker not installed -- skipping")
}

# ---- Summary ----
cat("\n=== Summary ===\n")
n_pass <- sum(vapply(results, function(r) isTRUE(r$ok), logical(1)))
n_fail <- length(results) - n_pass
cat(sprintf("%d passed, %d failed of %d checks.\n",
            n_pass, n_fail, length(results)))

if (n_fail > 0L) {
  cat("\nFailures:\n")
  for (name in names(results)) {
    if (!isTRUE(results[[name]]$ok)) {
      cat(sprintf("  * %s: %s\n", name, results[[name]]$details))
    }
  }
  cat("\nResult: PREFLIGHT FAILED.\n")
  quit(status = 1L)
}

cat("\nResult: preflight clean. Run devtools::check() before push.\n")
quit(status = 0L)
