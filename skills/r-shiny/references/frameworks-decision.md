# Shiny Framework Decision Guide

Pick the framework that matches your app's scale, team, and deployment target.
When in doubt, start with the smallest tool that fits and migrate up. See
[`../SKILL.md`](../SKILL.md) for the picker entry point and deep dives in
[`golem.md`](golem.md), [`rhino.md`](rhino.md), and [`teal.md`](teal.md).

## At-a-glance comparison

| Framework  | File layout                              | Learning curve | Deployment fit                     | Signature feature                        |
|------------|------------------------------------------|----------------|------------------------------------|------------------------------------------|
| base Shiny | `app.R` or `ui.R` + `server.R`           | Low            | shinyapps.io, single-file scripts  | Zero ceremony — paste and run            |
| golem      | R package (`R/app_ui.R`, `R/app_server.R`) | Medium         | Posit Connect, Docker, CRAN-style  | Package discipline + dev/prod lifecycle  |
| rhino      | `app/main/`, `app/view/`, `app/logic/`   | Medium-high    | Enterprise SPA, Docker, Cypress CI | `box::use()` modules + Sass + linting    |
| teal       | `teal::init()` with declarative modules  | High           | Validated pharma / regulated envs  | CDISC-aware filter panel + reproducibility |

## base Shiny (`app.R`, `ui.R`/`server.R`)

**Use when:**
- Prototyping or exploring an idea (<500 lines total).
- Single author, single deployment target (shinyapps.io or local).
- App has one or two logical components and no test suite yet.
- You need to ship a demo today and refactor later.

**Exit signals — migrate up when:**
- You need modules spread across multiple files (`R/mod_*.R`).
- You're adding `testthat` tests or CI.
- You have three or more logical components (data load, model, plotting, reporting).
- Two or more authors are editing the same file.

## golem

**Use when:**
- App will live as a production R package with `DESCRIPTION`, `NAMESPACE`, roxygen.
- Multi-author team needs `R CMD check`, versioned releases, and dependency pinning.
- Deployment target is Posit Connect, ShinyProxy, or a Docker image.
- You want CRAN-style structure with `dev/` scripts (`01_start.R`, `02_dev.R`, `03_deploy.R`).
- You need utilities like `golem::add_module()`, `golem::use_favicon()`, `golem::add_css_file()`.

**Exit signals — migrate up or sideways when:**
- You need first-class `box::use()` imports instead of package-level `NAMESPACE`.
- You want a built-in Sass pipeline and Cypress E2E (rhino territory).
- The app is a single-page enterprise UI where package overhead feels heavy.

## rhino

**Use when:**
- Building Appsilon-style enterprise single-page apps with strong design systems.
- You want `box::use()` module imports (no `library()` calls in app code).
- You need a Sass build pipeline, JS bundling via esbuild, and Cypress E2E in CI.
- Team values opinionated linting (`lintr`, `box.linters`) and a fixed directory shape.
- App will be deployed as a Docker container behind a reverse proxy.

**Exit signals — pick something else when:**
- Team is unfamiliar with `box::use()` and you can't invest in the ramp-up.
- You need a CRAN-publishable artifact (rhino apps are not packages).
- Stakeholders expect golem-style `dev/` scripts or `usethis`-driven tooling.

## teal

**Use when:**
- Dashboards run on CDISC ADaM/SDTM datasets (clinical trials, regulatory submissions).
- You need declarative module pipelines via `teal::init(data, modules)`.
- An integrated filter panel with subject-level / record-level filters is a hard requirement.
- Reproducibility (R code generation per view, snapshot/bookmark) is mandatory.
- Validated environments (GxP, 21 CFR Part 11) are part of the deployment story.

**Exit signals — pick something else when:**
- Data is not CDISC-shaped and you'd be fighting `teal.data::cdisc_data()`.
- You need fully custom UX outside teal's three-pane frame (encodings + filters + output).
- App is exploratory or single-study only — golem or base Shiny is faster.

## Decision tree

```
Is your data CDISC ADaM/SDTM?
  yes -> teal             (see teal.md)
  no  -> Production R package + Posit Connect / Docker?
           yes -> golem   (see golem.md)
           no  -> Enterprise SPA with box modules + Sass + Cypress?
                    yes -> rhino  (see rhino.md)
                    no  -> base Shiny
```

## Migration cheat sheet

### base Shiny -> golem

```r
# 1. Scaffold the package
golem::create_golem(pkg = "myapp")

# 2. Move existing UI/server into the package
# old: ui.R / server.R at project root
# new: R/app_ui.R / R/app_server.R
file.rename("ui.R",     "R/app_ui.R")
file.rename("server.R", "R/app_server.R")

# 3. Wrap each logical block as a module
golem::add_module(name = "data_table")
golem::add_module(name = "summary_plot")

# 4. Run the dev lifecycle
# dev/01_start.R -> dev/02_dev.R -> dev/03_deploy.R
```

### base Shiny -> teal

```r
# 1. Wrap CDISC data with teal.data
adsl_data <- teal.data::cdisc_data(
  ADSL = adsl,
  ADAE = adae
)

# 2. Register modules declaratively
app <- teal::init(
  data = adsl_data,
  modules = teal::modules(
    teal.modules.general::tm_data_table("Listing"),
    teal.modules.clinical::tm_t_summary("Demographics", dataname = "ADSL")
  )
)

# 3. Run as you would any Shiny app
shiny::runApp(app)
```

For a full module catalogue see [`teal.md`](teal.md); for golem dev/deploy
helpers see [`golem.md`](golem.md); for rhino's `box::use()` and Sass setup see
[`rhino.md`](rhino.md).
