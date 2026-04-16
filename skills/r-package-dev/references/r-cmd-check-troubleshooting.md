# R CMD check Troubleshooting

Every ERROR, WARNING, and NOTE you will see from `devtools::check()`,
grouped by what triggers them and how to fix. Ordered roughly by
frequency.

---

## ERRORs — Block Release

### "no visible global function definition for 'fn'"

```
❯ checking R code for possible problems ... NOTE
  my_fn: no visible global function definition for 'mutate'
```

**Cause:** You use `mutate()` without importing it.

**Fix:**

```r
# Either:
usethis::use_import_from("dplyr", "mutate")

# Or (preferred):
my_fn <- function() {
  data |> dplyr::mutate(x = 1)
}
```

### "no visible binding for global variable '.data'"

**Cause:** You use `.data[[col]]` or `.env$var` without importing from
rlang.

**Fix:**

```r
usethis::use_import_from("rlang", ".data")
devtools::document()
```

### "no visible binding for global variable 'col_name'"

**Cause:** NSE in dplyr/tidyr using bare column names. Check tries to
resolve them as globals.

**Fix:** Two options.

```r
# Option 1 — use .data pronoun (preferred)
my_fn <- function(data) {
  data |> dplyr::filter(.data$col_name > 0)
}

# Option 2 — declare as global (quick, less type-safe)
utils::globalVariables(c("col_name", "other_col"))
```

Put `globalVariables()` call in `R/mypkg-package.R`.

### "Error: object 'fn' is not exported by 'namespace:pkg'"

**Cause:** You reference a function that doesn't exist in the version of
the dependency your check uses.

**Fix:**

```r
# Bump the dependency version constraint:
usethis::use_package("pkg", min_version = "1.2.0")
```

Or change the code to use a function that does exist.

### "could not find function 'fn'"

**Cause:** Missing `library()` equivalent — same as "no visible global
function definition" but at run time (e.g., in examples or tests).

**Fix:** Add `@importFrom` or use `pkg::fn()`.

### "Package required but not available: 'pkg'"

**Cause:** `pkg` listed in Imports but not installed on the check
machine, or you forgot to add it.

**Fix:**

```r
install.packages("pkg")              # Local
usethis::use_package("pkg")          # Ensure it's in DESCRIPTION
```

### "running examples for arch ... failed"

**Cause:** An example in your `@examples` errors.

**Fix:**

```r
# Wrap slow/fragile examples:
#' @examples
#' \donttest{
#' result <- slow_fn()
#' }

# Or replace with lighter demo:
#' @examples
#' small_input <- c(1, 2, 3)
#' my_fn(small_input)
```

### "Error in library(pkg): there is no package called 'pkg'"

**Cause:** You have `library(pkg)` in an R file — package code must
never attach packages.

**Fix:** Replace with `pkg::fn()` or `@importFrom`. Only vignettes and
tests may use `library()`.

---

## WARNINGs — Usually Block Release

### "Undocumented code objects"

```
Undocumented code objects:
  'helper_fn'
```

**Cause:** Exported function has no roxygen block.

**Fix:** Add roxygen documentation with `@param`, `@returns`, `@examples`.

If the function should be internal, remove `@export` and rerun `document()`.

### "Documented arguments not in \usage in documentation object"

**Cause:** `@param some_arg` documented but not an actual function argument.

**Fix:** Remove the stale `@param` or fix the argument name.

### "Argument of ... has different default from \S4method"

**Cause:** S4 method signature drifted from the generic.

**Fix:** Align defaults, or regenerate the generic via `setGeneric()`.

### "Missing or unexported objects imported by ':::' calls"

**Cause:** You use `pkg:::internal_fn` (triple colon).

**Fix:** Don't. Remove the call; use a public alternative.

### "Files in the 'vignettes' directory but no files in 'inst/doc'"

**Cause:** Vignettes exist but haven't been built.

**Fix:**

```r
devtools::build_vignettes()
```

### "'LazyData' is specified without a 'data' directory"

**Cause:** `LazyData: true` in DESCRIPTION but no `data/` folder.

**Fix:** Remove `LazyData: true`.

### "Non-standard file/directory found at top level: 'x'"

**Cause:** A file at package root that isn't part of the standard
package layout.

**Fix:** Add to `.Rbuildignore`:

```r
usethis::use_build_ignore("dev-notes/")
```

### "Problems with news in 'NEWS.md'"

**Cause:** `NEWS.md` doesn't follow the parsing rules.

**Fix:**

- First line must be `# pkgname x.y.z` (H1)
- Use `# pkgname (development version)` for unreleased work
- Subsections use `##` or `###`

See `cran-submission-checklist.md` for template.

---

## NOTEs — Often Acceptable

### "New submission"

Appears on first CRAN submission. Mention in `cran-comments.md`:

```markdown
## R CMD check results

0 errors | 0 warnings | 1 note

* This is a new submission.
```

### "Days since last update: N"

Appears when submitting < 30 days since last release. Explain why:

```markdown
* Submitting 8 days after previous release to fix a critical bug
  (#42) reported by downstream maintainers.
```

### "Installed size is X Mb"

NOTE if install > 5 Mb. Justify if large:

```markdown
* Installed size is 12.3 Mb; this is due to precompiled Stan models
  in inst/stan/ (6.1 Mb) and embedded fonts (4.2 Mb) required for
  PDF output.
```

Reduce by:
- Moving large data to a companion data package
- Precompiling Stan models with `rstantools::rstan_config()`
- Removing unused fixture files

### "Found the following (possibly) invalid URLs"

**Cause:** Broken link or one that returns an unexpected status code.

**Fix:**

```r
urlchecker::url_check()           # Scan all URLs
urlchecker::url_update()          # Auto-fix redirects
```

For transient failures (e.g., rate-limited hosts), mention in
`cran-comments.md`.

### "checking dependencies in R code ... NOTE: Namespace in Imports field not imported from"

**Cause:** A package is in `DESCRIPTION` Imports but no function or
`@importFrom` references it.

**Fix:**

```r
# Either use the package or remove it:
usethis::use_package("unused_pkg", type = "Suggests")
# Or remove entirely from DESCRIPTION.
```

### "Found the following (non-portable) file names"

**Cause:** Filenames contain characters that break on Windows or older
filesystems (e.g., colons, >127 chars, trailing periods).

**Fix:** Rename to ASCII, short, no special chars.

### "Examples with CPU or elapsed time > 5s"

**Cause:** `@examples` take too long.

**Fix:**

```r
#' @examples
#' \donttest{
#' slow_fn(large_input)
#' }
```

### "checking compiled code ... NOTE"

**Cause:** Unregistered native routines or calls to `strcpy`, `printf`,
etc. in Rcpp code.

**Fix:**

```r
# Add to R/mypkg-package.R:
#' @useDynLib mypkg, .registration = TRUE
#' @importFrom Rcpp sourceCpp
NULL

devtools::document()
```

### "checking for unstated dependencies in 'tests' ... NOTE: 'pkg'"

**Cause:** A test uses `pkg::fn()` but `pkg` isn't in Suggests.

**Fix:**

```r
usethis::use_package("pkg", type = "Suggests")
```

---

## Special Checks (CRAN-only)

Turn on with `devtools::check(cran = TRUE)`.

### "checking CRAN incoming feasibility"

Informational. Lists detected issues — check and address each:

- Possible misspellings in DESCRIPTION
- Author format issues
- License issues
- Missing/broken URLs

### "Unknown, possibly misspelled, fields in DESCRIPTION"

**Cause:** Typo in a field name or unsupported field.

**Fix:** Check against the list in `?utils::read.dcf`; remove or fix.

### "The Title field should be in title case"

**Cause:** Lowercase Title.

**Fix:** Capitalise words other than articles/conjunctions/prepositions.

### "The Date field is over a month old"

**Cause:** Stale `Date:` field.

**Fix:** Remove the `Date:` field — CRAN uses DESCRIPTION timestamp on
upload. It's never needed manually.

---

## Environment and Platform Checks

### Checking on multiple platforms

```r
rhub::check_for_cran()                # Three typical CRAN platforms
devtools::check_win_devel()           # Windows R-devel (via win-builder)
devtools::check_mac_release()         # macOS (via mac.r-project.org)
```

Results arrive by email in ~1 hour.

### Debugging an R-hub-only failure

```r
# Get interactive shell on the failing platform:
rhub::local_check_linux(image = "rhub/ubuntu-release")
```

Or inspect the tarball CRAN uploaded to its check farm:
<https://cran.r-project.org/web/checks/check_results_mypkg.html>

---

## Quick-Triage Workflow

When `devtools::check()` fails:

1. Read the last error/warning from the top — most are cascading
2. Classify: code, docs, examples, tests, namespace, or metadata
3. Fix the cause, not the symptom
4. Rerun `devtools::document()` if NAMESPACE or Rd may be stale
5. Rerun `devtools::check()` on a clean install

```r
devtools::clean_dll()                 # Clear compiled artifacts
devtools::document()
devtools::check(cran = TRUE)
```

---

## Suppressing vs Fixing

Resist the urge to suppress. Legitimate uses of `utils::globalVariables()`:

- NSE in data-masking dplyr code where `.data` doesn't apply
- R6 `self` and `private` (add these in R6-heavy packages)
- ggplot2 `aes()` variables that are genuinely column names

Put them all in one place for easy audit:

```r
# R/mypkg-package.R
utils::globalVariables(c(".", "self", "private", "x", "y"))
```

Flag with a comment so future-you knows it's intentional.
