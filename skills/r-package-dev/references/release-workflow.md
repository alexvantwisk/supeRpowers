# Release Workflow

The `usethis::use_release_issue()`-driven workflow for shipping a CRAN release.
Complements `cran-submission-checklist.md` (which covers the check gauntlet);
this file covers the lifecycle around it.

**Sources:**
- R Packages 2e ch. 22 "Releasing to CRAN" — <https://r-pkgs.org/release.html>
- usethis release helpers — <https://usethis.r-lib.org/reference/use_release_issue.html>
- Keep a Changelog — <https://keepachangelog.com/>
- Semantic Versioning — <https://semver.org/>

---

## Lifecycle Overview

```
Dev (0.4.0.9000) -> Pre-release PR -> use_release_issue() -> Submit -> Tag -> Post-release bump
```

A package in active development carries a `.9000` dev suffix on its version
(e.g. `0.4.0.9000`). The release process strips the suffix, tests, submits,
and post-release bumps to the next `.9000`.

---

## Phase 1: Pre-release PR

Open a single PR that contains all release-prep changes:

```r
usethis::use_version("minor")          # 0.4.0.9000 -> 0.5.0
usethis::use_news_md()                 # if not already present
```

Update `NEWS.md`:

- New top-level header: `# mypkg 0.5.0`
- Subsections: `## New features`, `## Bug fixes`, `## Breaking changes`,
  `## Deprecations`
- One bullet per user-facing change. Reference issue/PR numbers.
- Move all bullets from the previous `# mypkg (development version)`
  header into the new release header.

Update `README.Rmd` (or `README.md`) if needed for new features. Re-knit:

```r
devtools::build_readme()
```

Update vignettes if API changed.

## Phase 2: Open the release issue

```r
usethis::use_release_issue()
```

This opens a GitHub issue with a checklist tailored to your package
(devtools/usethis introspect your CI status, whether it has revdeps, etc.).

The issue typically contains, in order:

1. Update `NEWS.md` ✓ (done in Phase 1)
2. Run `devtools::check()` and `urlchecker::url_check()`
3. Run `devtools::check_win_devel()` and `devtools::check_mac_release()`
4. Run `revdepcheck::revdep_check()` (only if revdeps exist)
5. Update `cran-comments.md`
6. `devtools::submit_cran()`
7. Approve email (CRAN sends a confirmation)
8. (After acceptance) tag the release
9. Post-release: `usethis::use_dev_version()`

Tick each item as you complete it. The issue is your audit trail.

## Phase 3: Pre-submission checks

Run the full gauntlet (this skill ships `scripts/release_checklist.R` for it):

```bash
Rscript skills/r-package-dev/scripts/release_checklist.R .
# or for revdeps:
Rscript skills/r-package-dev/scripts/release_checklist.R . --with-revdep
```

Required outcome: 0 errors, 0 warnings, 0 notes — across all platforms.

`cran-comments.md` minimum content:

```markdown
## R CMD check results

0 errors | 0 warnings | 0 notes

## Test environments

* local R 4.4.0, macOS 14.5
* win-builder R-devel
* mac-builder R-release
* GitHub Actions: ubuntu-latest, windows-latest, macos-latest, R-release

## Reverse dependencies

We checked 12 reverse dependencies. No new problems were detected.
```

## Phase 4: Submit

```r
devtools::submit_cran()
```

Approve the confirmation email CRAN sends to the maintainer address.

## Phase 5: Post-acceptance

After CRAN accepts (typically 1–7 days):

```r
usethis::use_github_release()    # tag + GitHub release with NEWS body
usethis::use_dev_version()       # bump 0.5.0 -> 0.5.0.9000
```

Commit the dev-version bump on `main` directly (not via PR).

Open a fresh `# mypkg (development version)` block at the top of `NEWS.md`.

## Rejection Protocol

If CRAN rejects:

1. Read the rejection email carefully — quote each issue in `cran-comments.md`.
2. Fix every flagged issue. Do not push back unless you genuinely disagree.
3. Add a "Resubmission" section to the top of `cran-comments.md`:

```markdown
## Resubmission

This is a resubmission. Compared to the previous submission:

* Fixed `\dontrun{}` examples flagged by Uwe — now use `\donttest{}`
  with `if (interactive())` guards (responses to comments dated YYYY-MM-DD).
* Added missing `\value{}` documentation for `internal_helper()`.
```

4. Re-run the gauntlet and resubmit with `devtools::submit_cran()`.

Most rejections are policy-related (description text, examples, file
modifications outside `tempdir()`), not code-correctness.

## Versioning

Follow Semantic Versioning:

| Change | Bump |
|---|---|
| Breaking API change | major (`0.4.0` -> `1.0.0`) |
| New feature, backward-compatible | minor (`0.4.0` -> `0.5.0`) |
| Bug fix only | patch (`0.4.0` -> `0.4.1`) |
| Active development | `.9000` suffix on the next planned version |

Pre-1.0 packages may break API freely between minor versions, but state this
in NEWS.md.
