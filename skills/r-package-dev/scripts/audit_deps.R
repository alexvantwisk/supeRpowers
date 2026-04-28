#!/usr/bin/env Rscript
# audit_deps.R — Audit a package's declared dependencies.
#
# Usage:  Rscript audit_deps.R [path/to/package]
#
# Reports:
#   1. Imports that are not actually used in R/ (candidates for removal)
#   2. Packages used in R/ but not listed in Imports/Depends (missing deps)
#   3. Suggests that are not guarded by requireNamespace() (potential bugs)
#   4. Version constraints (>= x.y.z) — lists them for review
#   5. Summary of dep counts

args <- commandArgs(trailingOnly = TRUE)
pkg_path <- if (length(args) >= 1) args[1] else "."

if (!dir.exists(pkg_path)) stop(sprintf("Directory not found: %s", pkg_path))
desc_file <- file.path(pkg_path, "DESCRIPTION")
if (!file.exists(desc_file)) {
  stop(sprintf("No DESCRIPTION in %s.", pkg_path))
}
if (!requireNamespace("desc", quietly = TRUE)) {
  stop("Package 'desc' required. install.packages(\"desc\").")
}

desc_obj <- desc::desc(file = desc_file)
deps <- desc_obj$get_deps()

imports_pkgs <- deps$package[deps$type %in% c("Imports", "Depends")]
imports_pkgs <- setdiff(imports_pkgs, "R")
suggests_pkgs <- deps$package[deps$type == "Suggests"]

# Scan R/ files for pkg::fun and @importFrom references
r_files <- list.files(file.path(pkg_path, "R"), pattern = "\\.[RrSsQq]$",
                      full.names = TRUE, recursive = TRUE)

collect_used <- function(files) {
  if (length(files) == 0L) return(character())
  lines <- unlist(lapply(files, readLines, warn = FALSE))
  # Match pkg::fn or pkg:::fn
  ns_refs <- regmatches(
    lines,
    gregexpr("([a-zA-Z][a-zA-Z0-9._]+)(?=:::?)", lines, perl = TRUE)
  )
  # Match #' @importFrom pkg ...
  import_refs <- regmatches(
    lines,
    regexec("@importFrom\\s+([A-Za-z][A-Za-z0-9._]+)", lines)
  )
  import_refs <- vapply(
    import_refs,
    function(x) if (length(x) >= 2L) x[[2L]] else NA_character_,
    character(1)
  )
  # Match @import pkg
  full_imports <- regmatches(
    lines,
    regexec("^#'\\s*@import\\s+([A-Za-z][A-Za-z0-9._]+)", lines)
  )
  full_imports <- vapply(
    full_imports,
    function(x) if (length(x) >= 2L) x[[2L]] else NA_character_,
    character(1)
  )
  unique(c(
    unlist(ns_refs),
    stats::na.omit(import_refs),
    stats::na.omit(full_imports)
  ))
}

used_in_r <- collect_used(r_files)

# Scan tests/ and vignettes/ for packages used there
test_files <- list.files(file.path(pkg_path, "tests"),
                         pattern = "\\.[RrSsQq]$", full.names = TRUE,
                         recursive = TRUE)
vignette_files <- list.files(
  c(file.path(pkg_path, "vignettes"),
    file.path(pkg_path, "vignettes", "articles")),
  pattern = "\\.(Rmd|qmd)$", full.names = TRUE, recursive = TRUE
)
used_in_tests <- collect_used(test_files)
used_in_vignettes <- collect_used(vignette_files)

cat("=== Dependency audit ===\n")
cat(sprintf("Package: %s (%s)\n",
            desc_obj$get("Package"), desc_obj$get_version()))
cat(sprintf("R files scanned: %d\n", length(r_files)))
cat(sprintf("Test files scanned: %d\n", length(test_files)))
cat(sprintf("Vignette files scanned: %d\n\n", length(vignette_files)))

# 1. Unused imports
unused <- setdiff(imports_pkgs, used_in_r)
# Exclude re-exports that only appear in NAMESPACE (e.g., magrittr)
# by including tests / vignettes references too
unused <- setdiff(unused, c(used_in_tests, used_in_vignettes))

cat("## 1. Potentially unused Imports/Depends\n")
if (length(unused) == 0L) {
  cat("  (none — all imports appear used)\n\n")
} else {
  for (p in sort(unused)) {
    cat(sprintf("  * %s — not referenced in R/. Verify or drop.\n", p))
  }
  cat("\n")
}

# 2. Missing deps — used in R/ but not in Imports/Depends
base_pkgs <- c("base", "stats", "utils", "methods", "graphics",
               "grDevices", "datasets", "tools", "parallel")
missing_in_desc <- setdiff(used_in_r, c(imports_pkgs, base_pkgs))

cat("## 2. Packages used in R/ but not declared\n")
if (length(missing_in_desc) == 0L) {
  cat("  (none — every referenced package is declared)\n\n")
} else {
  for (p in sort(missing_in_desc)) {
    cat(sprintf("  * %s — run usethis::use_package(\"%s\")\n", p, p))
  }
  cat("\n")
}

# 3. Unguarded Suggests
cat("## 3. Suggests usage\n")
check_guards <- function(files, suggested) {
  results <- list()
  if (length(suggested) == 0L || length(files) == 0L) return(results)
  for (p in suggested) {
    locations <- list()
    guarded <- FALSE
    for (f in files) {
      lines <- readLines(f, warn = FALSE)
      use_idx <- grep(paste0("\\b", p, "::"), lines)
      guard_idx <- grep(
        paste0("requireNamespace\\(\\s*[\"']", p, "[\"']"),
        lines
      )
      if (length(guard_idx) > 0L) guarded <- TRUE
      if (length(use_idx) > 0L) {
        for (i in use_idx) {
          locations[[length(locations) + 1L]] <- list(
            file = f, line = i, text = trimws(lines[i])
          )
        }
      }
    }
    results[[p]] <- list(
      uses = length(locations) > 0L,
      guarded = guarded,
      locations = locations
    )
  }
  results
}

r_guard <- check_guards(r_files, suggests_pkgs)
any_issue <- FALSE
for (p in names(r_guard)) {
  info <- r_guard[[p]]
  if (isTRUE(info$uses) && !isTRUE(info$guarded)) {
    cat(sprintf("  * %s -- used in R/ but NOT guarded by requireNamespace():\n",
                p))
    for (loc in info$locations) {
      rel_file <- sub(paste0("^", pkg_path, "/"), "",
                      normalizePath(loc$file, mustWork = FALSE))
      cat(sprintf("      %s:%d  %s\n",
                  rel_file, loc$line, loc$text))
    }
    cat(sprintf(
      "    Fix: wrap with `if (!requireNamespace(\"%s\", quietly = TRUE))`\n",
      p
    ))
    any_issue <- TRUE
  }
}
if (!any_issue) cat("  (all Suggests used in R/ appear guarded)\n")
cat("\n")

# 4. Version constraints
cat("## 4. Version constraints\n")
with_version <- deps[nzchar(trimws(deps$version)), ]
if (nrow(with_version) == 0L) {
  cat("  (no version constraints)\n")
} else {
  for (i in seq_len(nrow(with_version))) {
    cat(sprintf("  * %s %s (%s)\n",
                with_version$package[i],
                with_version$version[i],
                with_version$type[i]))
  }
  cat("\n  Review: remove constraints unless you use a version-specific feature.\n")
}
cat("\n")

# 5. Summary counts
cat("## 5. Summary\n")
cat(sprintf("  Depends:  %d\n", sum(deps$type == "Depends")))
cat(sprintf("  Imports:  %d\n", sum(deps$type == "Imports")))
cat(sprintf("  Suggests: %d\n", sum(deps$type == "Suggests")))
cat(sprintf("  LinkingTo: %d\n", sum(deps$type == "LinkingTo")))
cat("\n")

cat("Done.\n")
