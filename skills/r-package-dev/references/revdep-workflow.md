# Reverse Dependency Check Workflow

Required before any CRAN update that could break downstream packages.
Uses `revdepcheck` to install and check every CRAN/Bioconductor/GitHub
package that depends on yours against both the CRAN release and your
proposed update.

---

## When to Run revdep Checks

- Any time you update an already-published CRAN package
- Before changing exported function signatures
- Before deprecating or removing any exported function
- Before bumping a minimum dependency version
- Before any release, regardless of whether you think it's breaking

Skipping this is the single most common cause of a rejected CRAN update.

---

## Setup

```r
install.packages("revdepcheck",
                 repos = c("https://r-lib.r-universe.dev",
                           "https://cloud.r-project.org"))

usethis::use_revdep()
```

`use_revdep()`:
- Adds `revdep/` to `.Rbuildignore` and `.gitignore`
- Creates `revdep/.gitignore`
- Creates `revdep/` directory for artifacts

---

## Running the Check

```r
revdepcheck::revdep_check(num_workers = 4)
```

**Time:** 30 minutes to many hours depending on reverse-dep count and
machine. For packages with > 50 reverse deps, run overnight.

**Output:** `revdep/README.md` with summary, plus per-package reports in
`revdep/checks/<pkg>/`.

### Resuming an interrupted check

```r
revdepcheck::revdep_check(num_workers = 4)   # Resumes by default
```

`revdepcheck` caches completed package checks. Rerunning continues from
where it stopped.

### Starting over

```r
revdepcheck::revdep_reset()        # Clean slate
```

---

## Interpreting Results

### `revdep/README.md` summary

Auto-generated file with three sections:

```markdown
## Revdeps

### Failed to check (2)
| package | version | error | warning | note |
| :---    | :---    | :---  | :---    | :--- |
| pkgA    | 1.2.0   | 1     |         |      |
| pkgB    | 0.3.1   | 1     |         |      |

### New problems (0)
(No new problems.)

### Broken (0)
```

**What matters:**

| Category | Meaning | Action |
|----------|---------|--------|
| **New problems** | Package passed CRAN but fails your update | MUST fix before release |
| **Broken** | Subset of "new problems" marking regressions | MUST fix |
| **Failed to check** | Timeouts, install failures, environment issues | Investigate; usually not your fault |
| **Unchanged issues** | Pre-existing problems in the reverse dep | Ignore — not yours to fix |

### Per-package reports

`revdep/checks/<pkg>/` contains:
- `old/` — R CMD check result against CRAN version of your package
- `new/` — R CMD check result against your development version
- The diff between them is what matters

```r
revdepcheck::revdep_details(".", "pkgA")   # Print full diff for one package
```

---

## Handling New Problems

### Step 1: Confirm the failure is caused by your changes

Run locally against just that reverse dep:

```r
revdepcheck::revdep_check_package("pkgA", new_repo = ".",
                                  old_repo = "cran")
```

### Step 2: Classify the issue

| Type | Example | Action |
|------|---------|--------|
| Behaviour change | Your fn now returns tibble instead of data.frame | Add back data.frame compat or negotiate with downstream |
| Argument rename | `group` → `group_col` | Provide deprecated alias with `lifecycle` |
| Removed function | Cleanup of internal-looking API | Add back with deprecation warning |
| Stricter validation | Rejects inputs previously accepted | Decide: fix downstream or relax validation |
| Broken example | Downstream's example calls your API incorrectly | Not your problem if they're using undocumented behaviour |

### Step 3: File issues or PRs with downstream maintainers

For breaking changes you intend to keep, notify downstream early:

1. Open a GitHub issue on each affected package
2. Reference your PR / release notes
3. Offer to send a PR fixing their usage
4. Give them 2+ weeks before submitting to CRAN

### Step 4: Add deprecation shims where possible

Use `lifecycle` package:

```r
#' @param group `r lifecycle::badge("deprecated")` Use `group_col` instead.
#' @param group_col Column to group by.
summarise_data <- function(data, group_col, group = lifecycle::deprecated()) {
  if (lifecycle::is_present(group)) {
    lifecycle::deprecate_warn(
      "1.2.0", "summarise_data(group = )", "summarise_data(group_col = )"
    )
    group_col <- group
  }
  # ... use group_col
}
```

---

## Reporting in `cran-comments.md`

After revdep checks pass, update `cran-comments.md`:

```markdown
## revdepcheck results

We checked 47 reverse dependencies, comparing R CMD check results
across CRAN and dev versions of this package.

 * We saw 0 new problems
 * We failed to check 2 packages

Issues with CRAN packages are summarised below.

### Failed to check

* pkgA (NA). System requirement libxyz-dev not available on test runner.
* pkgB (NA). Timed out during install.
```

Both lines are expected patterns; CRAN reviewers accept them if you
verify the failures are environment-related, not caused by your package.

---

## Tips for Large Reverse Dependency Counts

### Parallelism

```r
revdepcheck::revdep_check(num_workers = 8)
```

Rule of thumb: `num_workers = floor(cores / 2)` to leave headroom.

### Docker for reproducibility

```r
revdepcheck::revdep_check(num_workers = 4, bioc = TRUE)
```

For packages with Bioconductor reverse deps, pass `bioc = TRUE`.

### Running on a spare machine

```r
revdepcheck::revdep_check(
  num_workers = 4,
  timeout = as.difftime(60, units = "mins"),  # Per-package timeout
  quiet = FALSE
)
```

### Cloud runners

- GitHub Actions runners time out at 6 hours — insufficient for many
  packages
- Use a dedicated VM or `revdepcheck::revdep_cloud()` helpers (if
  available in your setup)

---

## Targeting Specific Reverse Deps

For incremental development:

```r
# Check just a few packages
revdepcheck::revdep_check(num_workers = 2,
                          packages = c("pkgA", "pkgB"))

# Check only packages using a specific function
rdeps <- revdepcheck::revdep_deps(".", "fetch_forecast")
revdepcheck::revdep_check(packages = rdeps)
```

---

## Common Failure Modes and Fixes

| Failure | Likely cause | Fix |
|---------|-------------|-----|
| "installation of package failed" | Missing system lib on runner | Not your problem; note in cran-comments.md |
| "there is no package called 'x'" | Missing Suggests dep | Install manually; rerun |
| Consistent timeouts | Package is genuinely slow | Skip with `revdep_skip()` |
| Different errors across runs | Flaky tests | Not your problem; document in comments |
| Examples fail where they passed before | Actual regression in your package | Fix the regression |
| Stale cache after your code change | `revdepcheck` using old build | `revdep_reset()`; rerun |

---

## Commit Artifacts?

**Commit:**
- `revdep/README.md`
- `revdep/cran.md`
- `revdep/problems.md`
- `revdep/failures.md`

**Gitignore:**
- `revdep/checks/` (large, regenerable)
- `revdep/library/`
- `revdep/data.sqlite`

`use_revdep()` configures `revdep/.gitignore` correctly.

---

## Fast Path for Small Packages

For packages with 0-5 reverse deps, the full workflow is overkill:

```r
# One-shot check
revdepcheck::revdep_check(num_workers = 1)

# Or skip automation — just install each revdep manually and run their tests
```

Still note the result in `cran-comments.md`:

```markdown
## Downstream dependencies

There are currently no downstream dependencies for this package.
```

or

```markdown
## Downstream dependencies

Checked 3 reverse dependencies. 0 packages had issues.
```
