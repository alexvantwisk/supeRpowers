# CRAN Submission Checklist

Step-by-step guide for submitting an R package to CRAN. Follow this in order.

---

## Phase 1: Pre-Submission Checks

### R CMD check

```r
devtools::check(cran = TRUE)
```

**Required outcome:** 0 errors, 0 warnings, 0 notes (ideal).

CRAN accepts packages with certain NOTEs, but zero is the goal. Fix everything
you can before submitting.

### URL Validation

```r
urlchecker::url_check()
```

Fix broken URLs, redirect chains, and non-HTTPS links. CRAN checks URLs
automatically and will reject packages with broken links.

### Spelling

```r
spelling::spell_check_package()
usethis::use_spell_check()     # Adds to .github/workflows if desired
```

Add false positives to `inst/WORDLIST` (one word per line, sorted).

### Cross-Platform Testing

```r
rhub::check_for_cran()                 # Multiple platforms via R-hub
devtools::check_win_devel()            # Windows R-devel (via win-builder)
devtools::check_mac_release()          # macOS (via mac.r-project.org)
```

Test on at least: Linux, Windows, macOS. Test with both current R release and
R-devel.

### Documentation Completeness

Verify:
- [ ] All exported functions have `@param` for every argument
- [ ] All exported functions have `@returns`
- [ ] All exported functions have `@examples`
- [ ] Examples run without error in `R CMD check`
- [ ] `\dontrun{}` used only when examples truly cannot be run (network, auth)
- [ ] Prefer `\donttest{}` over `\dontrun{}` when examples are just slow

### Package Metadata

Verify `DESCRIPTION`:
- [ ] `Title`: Title case, no period, no "A Package for..."
- [ ] `Description`: At least one complete sentence, ends with period
- [ ] `Authors@R`: Uses `person()` with ORCID if available
- [ ] `License`: Standard license string (e.g., `MIT + file LICENSE`)
- [ ] `URL`: Package website or GitHub repo
- [ ] `BugReports`: Issue tracker URL
- [ ] Version follows semantic versioning (x.y.z for release, x.y.z.9000 for dev)

---

## Phase 2: Acceptable vs Problematic NOTEs

### Usually Acceptable

| NOTE | Reason | Action |
|------|--------|--------|
| "New submission" | First time on CRAN | Mention in cran-comments.md |
| "Days since last update: X" | Frequent updates | Explain why in comments |
| "Installed size is X Mb" | Large data/compiled code | Justify if >5Mb |
| "checking CRAN incoming feasibility" | Automated check | Typically informational |

### Must Fix Before Submission

| NOTE | Fix |
|------|-----|
| "no visible binding for global variable" | Use `.data$col` or add `utils::globalVariables()` |
| "no visible global function definition" | Add `@importFrom` or use `pkg::fun()` |
| "non-standard file/directory found" | Add to `.Rbuildignore` |
| "Undefined global functions or variables" | Fix NSE references with `.data` pronoun |
| "Found the following (possibly) invalid URLs" | Fix or remove broken URLs |
| "Package has a VignetteBuilder field but no vignettes" | Add vignettes or remove field |

---

## Phase 3: NEWS.md

Use [Keep a Changelog](https://keepachangelog.com/) style:

```markdown
# mypkg (development version)

# mypkg 1.0.0

## New Features

* `fetch_forecast()` retrieves weather data from the API (#12).
* `plot_trend()` adds a smoothed trend line to time series plots (#15).

## Bug Fixes

* `parse_date()` no longer fails on ISO 8601 dates with timezone offsets (#23).
* Fixed NULL propagation in `validate_input()` when column is missing (#27).

## Breaking Changes

* `summarise_data()` argument `group` renamed to `group_col` for consistency.
* Minimum R version bumped to 4.1.0 (base pipe support).

# mypkg 0.9.0

* Initial release.
```

**Rules:**
- Reference GitHub issue/PR numbers with `#N`
- Group by: New Features, Bug Fixes, Breaking Changes, Deprecated
- Most recent version at top
- Use `usethis::use_version()` to bump version and update NEWS.md header

---

## Phase 4: cran-comments.md

Create at package root (not in `inst/`). Template:

```markdown
## Test environments

* local macOS (aarch64), R 4.4.1
* GitHub Actions: ubuntu-latest (R release, R devel), windows-latest (R release), macOS-latest (R release)
* R-hub: ubuntu-22.04 (R devel), windows-latest (R devel)
* win-builder: R devel

## R CMD check results

0 errors | 0 warnings | 1 note

* This is a new submission.

## Downstream dependencies

There are currently no downstream dependencies for this package.
```

**For updates** (not first submission):

```markdown
## Downstream dependencies

Checked N reverse dependencies using `revdepcheck::revdep_check()`.
0 packages had issues.

Summary: https://github.com/user/mypkg/tree/main/revdep
```

Run reverse dependency checks:

```r
usethis::use_revdep()
revdepcheck::revdep_check(num_workers = 4)
revdepcheck::revdep_summary()
```

---

## Phase 5: Submit

```r
devtools::submit_cran()
```

Or upload the tarball manually at <https://cran.r-project.org/submit.html>.

After submission:
1. You receive a confirmation email -- click the link to confirm
2. CRAN reviews within 1-10 business days (typically 2-5)
3. You receive an email with accept/reject/request-changes

---

## Resubmission Protocol

If CRAN requests changes:

1. **Fix all issues** mentioned in the reviewer's email
2. **Bump patch version** (e.g., 1.0.0 -> 1.0.1)
3. **Update cran-comments.md** with:
   ```markdown
   ## Resubmission

   This is a resubmission. In this version I have:

   * Replaced \dontrun{} with \donttest{} in examples (per reviewer request).
   * Added single quotes around package names in DESCRIPTION.
   ```
4. **Resubmit** via `devtools::submit_cran()` or web form
5. **Reply to the original CRAN email** with a brief, polite note

**Etiquette:**
- Be concise and professional
- Address every point raised
- Do not argue with policies -- just fix the issues
- Thank the reviewer
- Do not resubmit more than once per day

---

## Common Rejection Reasons

### Documentation Issues

| Problem | Fix |
|---------|-----|
| Missing `\value` in Rd files | Add `@returns` to every function |
| `\dontrun{}` without justification | Use `\donttest{}` for slow examples, remove `\dontrun{}` unless truly impossible |
| Package name not quoted in DESCRIPTION | Use single quotes: `'dplyr'` |
| Vague `Description` field | Write complete sentences explaining what the package does |

### Examples and Tests

| Problem | Fix |
|---------|-----|
| Examples fail on CRAN machines | Wrap network/auth examples in `\donttest{}` |
| Tests take >10 minutes | Skip slow tests on CRAN with `skip_on_cran()` |
| Tests modify user state | Use `withr::local_*()` for all side effects |
| Tests rely on internet | Mock HTTP calls or `skip_if_offline()` |

### Policy Violations

| Problem | Fix |
|---------|-----|
| Writing to user home/working directory | Use `tempdir()` for all file I/O in examples/tests |
| Downloading files in examples | Use `\donttest{}` or mock the download |
| Setting `options()` without resetting | Use `withr::local_options()` |
| Modifying the global environment | Use `withr::local_envvar()` |
| Calling `installed.packages()` | Use `find.package()` or `requireNamespace()` instead |
| Using `cat()`/`print()` in functions | Use `message()` or `cli::cli_inform()` (suppressible) |
| Hard-coded paths | Use `system.file()` or `tempdir()` |

### NAMESPACE Issues

| Problem | Fix |
|---------|-----|
| `@import` entire package | Use `@importFrom pkg fun` selectively |
| Unused imports | Remove from roxygen tags and re-run `devtools::document()` |
| Missing package in `Imports` | `usethis::use_package("pkg")` |

---

## Final Checklist Before Clicking Submit

- [ ] `devtools::check(cran = TRUE)` passes with 0 errors, 0 warnings
- [ ] All NOTEs are explained in `cran-comments.md`
- [ ] `urlchecker::url_check()` is clean
- [ ] `spelling::spell_check_package()` false positives in `inst/WORDLIST`
- [ ] `NEWS.md` is updated for this version
- [ ] `cran-comments.md` is current
- [ ] Version number is release-ready (no `.9000` suffix)
- [ ] Reverse dependencies checked (for updates)
- [ ] `README.md` is up to date (`devtools::build_readme()` if using `.Rmd`)
- [ ] Package builds from clean state: `devtools::build()` succeeds
