# pkgdown Site Configuration

Build and deploy a professional package website with pkgdown. Covers
`_pkgdown.yml` structure, reference organisation, vignette integration,
theming, and GitHub Pages deployment.

---

## Setup

```r
usethis::use_pkgdown()                     # Create _pkgdown.yml skeleton
usethis::use_pkgdown_github_pages()        # Configure GitHub Pages + Actions workflow
pkgdown::build_site()                      # Build locally in docs/
pkgdown::preview_site()                    # Serve locally
```

`use_pkgdown_github_pages()`:
- Creates `.github/workflows/pkgdown.yaml`
- Adds `docs/` to `.Rbuildignore` and `.gitignore`
- Configures GitHub Pages branch (`gh-pages`) and URL
- Sets `URL:` in DESCRIPTION

---

## Minimal `_pkgdown.yml`

```yaml
url: https://user.github.io/mypkg/

template:
  bootstrap: 5
  bootswatch: flatly

development:
  mode: auto      # release/devel shown based on version suffix

home:
  title: mypkg — Tidy Access to Weather APIs

reference:
  - title: "Fetching data"
    desc: >
      Functions that query the underlying APIs.
    contents:
      - fetch_forecast
      - fetch_current
      - fetch_historical

  - title: "Tidying results"
    contents:
      - starts_with("tidy_")

  - title: "Utilities"
    contents:
      - has_concept("utility")
```

---

## Organising the Reference Index

### By explicit function list

```yaml
reference:
  - title: "Data retrieval"
    contents:
      - fetch_forecast
      - fetch_current
```

### By pattern matching

```yaml
reference:
  - title: "Fitters"
    contents:
      - starts_with("fit_")
  - title: "Summarisers"
    contents:
      - ends_with("_summary")
  - title: "All plotters"
    contents:
      - matches("^plot_")
```

### By concept

Tag functions with `@concept` in roxygen2:

```r
#' @concept io
fetch_forecast <- function() ...
```

Then reference them:

```yaml
reference:
  - title: "I/O"
    contents:
      - has_concept("io")
```

### By family

Tag with `@family plotters` in roxygen2:

```yaml
reference:
  - title: "Plotting"
    contents:
      - has_family("plotters")
```

### Internal items

```yaml
reference:
  - title: internal
    contents:
      - has_keyword("internal")
```

---

## Vignettes / Articles

Add vignettes with `usethis::use_vignette()`. They appear under
`Articles` automatically. Group them:

```yaml
articles:
  - title: "Getting started"
    navbar: ~       # Show in navbar
    contents:
      - getting-started
      - installation

  - title: "Advanced usage"
    contents:
      - custom-queries
      - caching
      - performance
```

Articles not intended as CRAN vignettes go in `vignettes/articles/` —
they're built for the site but not shipped with the package.

```r
usethis::use_article("internals")   # Creates vignettes/articles/internals.Rmd
```

---

## Navbar Customisation

```yaml
navbar:
  structure:
    left:  [intro, reference, articles, news]
    right: [search, github]
  components:
    intro:
      text: "Get started"
      href: articles/getting-started.html
    articles:
      text: "Articles"
      menu:
        - text: "Advanced"
        - text: "Custom queries"
          href: articles/custom-queries.html
        - text: "Caching"
          href: articles/caching.html
```

---

## Theming

### Bootstrap 5 (recommended)

```yaml
template:
  bootstrap: 5
  bootswatch: flatly       # Or: cosmo, lumen, materia, minty, pulse, ...
```

Browse options: <https://bootswatch.com/>

### Custom colours

```yaml
template:
  bootstrap: 5
  bslib:
    primary: "#0054AD"
    border-radius: 0.5rem
    btn-border-radius: 0.25rem
    base_font:
      google: "Inter"
    heading_font:
      google: "Lora"
    code_font:
      google: "JetBrains Mono"
```

### Dark mode

```yaml
template:
  bootstrap: 5
  light-switch: true        # Adds light/dark toggle to navbar
```

---

## Home Page

The home page is built from `README.md` by default. Customise with
front-matter-style options:

```yaml
home:
  title: mypkg — One-line tagline
  description: >
    Longer description shown in meta tags and social previews.
  links:
  - text: Browse source
    href: https://github.com/user/mypkg
  - text: Report a bug
    href: https://github.com/user/mypkg/issues
```

---

## Authors Page

pkgdown auto-generates an authors page from `DESCRIPTION`. Enhance with
sidebar blocks:

```yaml
authors:
  Jane Doe:
    href: https://janedoe.dev
  Acme Corp:
    href: https://acme.example.com
    html: <img src="acme.svg" width="72" alt="Acme Corp" />

  sidebar:
    roles: [cre, aut, ctb]
    before: "Thanks to:"
    after: "[Contribute on GitHub](https://github.com/user/mypkg)"
```

---

## Function Reference Enhancement

### `@section` in roxygen2

Appears as a custom heading on the function page:

```r
#' @section Rate limiting:
#' The API enforces 60 requests per minute. This function retries with
#' exponential backoff on HTTP 429 responses.
```

### Usage examples with `@examplesIf`

Conditionally run examples based on setup:

```r
#' @examplesIf interactive()
#' fetch_forecast("London")
```

### Cross-links with `[fn()]`

Auto-link to other functions in the package or listed dependencies:

```r
#' See [summarise_data()] and [stats::lm()] for related tools.
```

---

## News Page

Renders `NEWS.md` as a versioned changelog. Organise with H1 per version
and H2 per category:

```markdown
# mypkg 1.1.0

## New features

* `fetch_historical()` added (#42).

## Bug fixes

* `fetch_forecast()` no longer errors on empty responses (#45).
```

---

## Deployment via GitHub Actions

`usethis::use_github_action("pkgdown")` creates
`.github/workflows/pkgdown.yaml`:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  release:
    types: [published]
  workflow_dispatch:

name: pkgdown

jobs:
  pkgdown:
    runs-on: ubuntu-latest
    env:
      GITHUB_PAT: ${{ secrets.GITHUB_TOKEN }}
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: r-lib/actions/setup-pandoc@v2
      - uses: r-lib/actions/setup-r@v2
      - uses: r-lib/actions/setup-r-dependencies@v2
        with:
          extra-packages: any::pkgdown, local::.
          needs: website
      - name: Build site
        run: pkgdown::build_site_github_pages(new_process = FALSE, install = FALSE)
        shell: Rscript {0}
      - name: Deploy
        if: github.event_name != 'pull_request'
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          clean: false
          branch: gh-pages
          folder: docs
```

After the first successful run, the site is live at the URL in
`_pkgdown.yml`.

---

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| Functions missing from reference index | Add to `reference:` in `_pkgdown.yml`, or ensure `@export` and that `reference:` is not overly restrictive |
| Articles show but don't render | Missing `VignetteEngine` or `knitr` in `Suggests` |
| `@examples` with `\dontrun{}` don't run on site | Replace with `\donttest{}` or `@examplesIf` |
| Broken cross-references `[fn()]` | Check spelling; ensure target is exported or in `Imports` |
| 404 on deploy | Ensure `url:` in `_pkgdown.yml` matches GitHub Pages URL (trailing slash matters) |
| pkgdown version mismatch in CI | Pin `Config/Needs/website: pkgdown` in DESCRIPTION |
| Custom CSS not applied | Put in `pkgdown/extra.css` (auto-loaded) |
