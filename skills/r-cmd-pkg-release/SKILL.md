---
name: r-cmd-pkg-release
description: >
  Use when starting an R package release workflow. Orchestrates r-package-dev
  and r-tdd skills with r-pkg-check, r-dependency-manager, and r-code-reviewer
  agents through a guided check-test-document-build-submit pipeline. Invoke as
  /r-cmd-pkg-release.
  Triggers: release package, CRAN submission, package release, version bump,
  prepare release, submit to CRAN, pre-release check.
  Do NOT use for ongoing package development — use r-package-dev instead.
  Do NOT use for writing new tests — use r-cmd-tdd-cycle instead.
---

# Package Release

Guided release workflow: audit dependencies, test, document, check, bump, review, submit.

## Prerequisites

- R package with `DESCRIPTION`, `NAMESPACE`, and `R/` directory
- testthat 3e configured with existing test suite
- renv initialized (`renv.lock` present)
- All current work committed to version control

## Progress Tracking

Use TaskCreate at the start of this workflow — one task per phase below. Mark each `in_progress` when starting, `completed` when its gate passes.

- "Phase 1: Dependency audit"
- "Phase 2: Run tests"
- "Phase 3: Document"
- "Phase 4: R CMD check"
- "Phase 5: Version bump"
- "Phase 6: Final review"
- "Phase 7: Submit (CRAN only — skip for internal releases)"

CRAN submission is high-stakes; visible checkpoint state prevents skipping a gate after a failed retry.

## Steps

### Step 1: Dependency audit
**Agent:** `r-dependency-manager`
**Action:** Run `renv::status()`, check for version conflicts, unused dependencies, and heavy packages with lighter alternatives. Verify R version compatibility.
**Gate:** No CRITICAL dependency issues. Lock file is in sync.

### Step 2: Run tests
**Skill:** `r-tdd`
**Action:** Run `devtools::test()`. Check coverage with `covr::package_coverage()`.
**Gate:** All tests pass. Coverage >= 80%.

### Step 3: Document
**Skill:** `r-package-dev`
**Action:** Run `devtools::document()`. Verify all exported functions have complete roxygen2 docs (`@param`, `@returns`, `@examples`). Update `NEWS.md` with changes since last release.
**Gate:** No undocumented exports. `NEWS.md` is current.

### Step 4: R CMD check
**Agent:** `r-pkg-check` → escalate to `r-dependency-manager` on version conflicts → escalate to `r-code-reviewer` on code quality findings
**Action:** Run `devtools::check()`. Resolve all ERRORs and WARNINGs. Review NOTEs.
**Gate:** 0 errors, 0 warnings. NOTEs reviewed and either fixed or documented as acceptable.

### Step 5: Version bump
**Skill:** `r-package-dev`
**Action:** Run `usethis::use_version()` (patch/minor/major as appropriate). Verify `DESCRIPTION` version and `NEWS.md` heading match.
**Gate:** Version incremented. NEWS heading matches new version.

### Step 6: Final review
**Agent:** `r-code-reviewer` (scope: full)
**Action:** Review all changed files since last release tag. Check for leftover TODOs, debug code, or commented-out blocks.
**Gate:** No CRITICAL or HIGH findings.

### Step 7: Submit (CRAN only)
**Skill:** `r-package-dev`
**Action:** Run `devtools::submit_cran()` or follow manual submission at https://cran.r-project.org/submit.html. Verify `cran-comments.md` is complete.
**Gate:** Package submitted. Confirmation email received.

## Abort Conditions

- Failing tests that indicate broken functionality — fix before proceeding.
- R CMD check ERRORs requiring architectural changes — stop and re-plan.
- Dependency conflicts requiring upstream package updates — file issue, defer release.
- Coverage below 80% — add tests before release.

## Examples

### Example: Preparing a patch release for CRAN

**Prompt:** "Prepare mypackage v0.2.1 for CRAN — we fixed two bugs since 0.2.0."

**Flow:** Dependency audit → Tests (all pass) → Document (update NEWS.md with bug fixes) → R CMD check (0/0/1 NOTE about package size — acceptable) → Version bump to 0.2.1 → Final review → Submit

### Example: First CRAN submission

**Prompt:** "Submit mypackage to CRAN for the first time."

**Flow:** Dependency audit (extra scrutiny on deps list) → Tests → Document (ensure all vignettes build) → R CMD check (fix all NOTEs for first submission) → Version bump to 1.0.0 → Final review → Create `cran-comments.md` with `usethis::use_cran_comments()` → Submit
