# teal Deep Dive — Clinical-Trial Dashboards on CDISC Data

## What teal is

`teal` is a Shiny-based exploratory analysis framework built by Roche/Genentech as part of the [NEST](https://insightsengineering.github.io/) initiative. It is the de facto pharma standard for clinical-trial dashboards over CDISC ADaM/SDTM-shaped data.

A teal app is **declarative**: instead of writing UI/server pairs by hand, you describe (a) the dataset bundle and join keys, (b) an ordered list of analysis modules, and (c) a pre-set filter state. teal renders the filter panel, navigation tabs, and inter-module reactivity for you. Each module is itself a Shiny module wrapped in `teal::module()` so that filters propagate, the reproducibility log captures interactions, and variable selectors stay consistent across tabs.

teal is not a general-purpose Shiny framework. It assumes your inputs are tidy data frames with stable join keys (typically `STUDYID`, `USUBJID`) and that your analyses are recognisable patterns from clinical reporting (summary tables, AE listings, KM curves, MMRM, ANCOVA, shift tables).

For *what* the underlying data domains contain, defer to `r-clinical`. This reference covers the *app-construction* layer.

## Package ecosystem

| Package | Role | Key entry points |
|---|---|---|
| `teal` | Core framework | `teal::init()`, `teal::module()`, `teal::modules()` |
| `teal.data` | Dataset bundle, join keys | `teal.data::cdisc_data()`, `teal.data::cdisc_dataset()` |
| `teal.slice` | Filter panel UI | `teal.slice::teal_slices()`, `teal.slice::teal_slice()` |
| `teal.transform` | Variable selectors, extract specs | `teal.transform::choices_selected()`, `teal.transform::data_extract_spec()` |
| `teal.modules.general` | Standard non-clinical modules | `tm_data_table`, `tm_g_scatterplot`, `tm_a_regression` |
| `teal.modules.clinical` | Clinical-specific modules | `tm_a_patient_profile`, `tm_t_summary`, `tm_g_km`, `tm_a_mmrm`, ... |
| `teal.code` | Reproducible R code log | Captures every interaction; users download the script |
| `teal.logger` | Structured logging | Wraps `logger` for app-level events |

Install the clinical stack from the NEST CRAN-like repo (or from CRAN where mirrored):

```r
install.packages(
  c("teal", "teal.data", "teal.slice", "teal.transform",
    "teal.modules.general", "teal.modules.clinical"),
  repos = c("https://insightsengineering.r-universe.dev", getOption("repos"))
)
```

## Defining datasets — `teal.data::cdisc_data()`

Every teal app starts with a `cdisc_data` bundle. Each dataset is wrapped via `cdisc_dataset()` so teal knows the dataset name (`ADSL`, `ADAE`, `ADTTE`) and the **join keys** that wire cross-module filtering.

```r
library(teal)
library(teal.data)
library(teal.modules.clinical)

adsl <- random.cdisc.data::cadsl
adae <- random.cdisc.data::cadae
adtte <- random.cdisc.data::cadtte

teal_data <- teal.data::cdisc_data(
  adsl = teal.data::cdisc_dataset(
    dataname = "ADSL",
    x = adsl,
    keys = c("STUDYID", "USUBJID")
  ),
  adae = teal.data::cdisc_dataset(
    dataname = "ADAE",
    x = adae,
    keys = c("STUDYID", "USUBJID", "AETERM", "AESTDTC")
  ),
  adtte = teal.data::cdisc_dataset(
    dataname = "ADTTE",
    x = adtte,
    keys = c("STUDYID", "USUBJID", "PARAMCD")
  ),
  code = "
    adsl  <- random.cdisc.data::cadsl
    adae  <- random.cdisc.data::cadae
    adtte <- random.cdisc.data::cadtte
  "
)
```

**Why join keys matter:** when a user filters `ADSL` to `SAFFL == \"Y\"`, teal propagates the filter to `ADAE` and `ADTTE` by their shared `STUDYID`/`USUBJID`. Without keys, modules see un-filtered data and cross-tab consistency breaks. The `code` argument is the seed of the reproducibility log — it records how the data were loaded.

## Initialising the app — `teal::init()`

`teal::init()` glues data, modules, and filters into an `app` list with `ui` and `server` components. You hand those to `shiny::shinyApp()`.

```r
app <- teal::init(
  data = teal_data,
  modules = teal::modules(
    teal.modules.general::tm_data_table("Data"),
    teal.modules.clinical::tm_t_summary(
      label = "Summary",
      dataname = "ADSL",
      arm_var = teal.transform::choices_selected(c("ARM", "ACTARM"), "ARM"),
      summarize_vars = teal.transform::choices_selected(
        c("AGE", "SEX", "RACE", "BMRKR1"),
        c("AGE", "SEX")
      )
    ),
    teal.modules.clinical::tm_g_km(
      label = "Kaplan-Meier",
      dataname = "ADTTE",
      arm_var = teal.transform::choices_selected(c("ARM", "ACTARM"), "ARM"),
      paramcd = teal.transform::choices_selected("PARAMCD", "PARAMCD"),
      time_var = teal.transform::choices_selected("AVAL", "AVAL"),
      cnsr_var = teal.transform::choices_selected("CNSR", "CNSR")
    )
  ),
  filter = teal.slice::teal_slices(
    teal.slice::teal_slice(
      dataname = "ADSL",
      varname = "AGE",
      selected = c(18, 100)
    )
  )
)

shiny::shinyApp(app$ui, app$server)
```

This is a complete `app.R` — paste it into a file with the dataset block above and `shiny::runApp()` it. teal handles the navigation tabs, filter panel on the left, and inter-module reactivity.

## Standard `teal.modules.clinical` modules

Each module ships with its own variable selectors exposed via constructor `args()`. Common modules:

- `tm_a_patient_profile` — per-subject patient-level dossier across multiple ADaM domains.
- `tm_t_summary` — descriptive summary table over arbitrary `summarize_vars`, stratified by `arm_var`.
- `tm_t_ae` — adverse-event count tables with `SOC`/`PT` hierarchy.
- `tm_g_km` — Kaplan-Meier survival curves over an `ADTTE` parameter, stratified by arm.
- `tm_a_mmrm` — mixed-model repeated measures with auto-rendered diagnostics.
- `tm_a_ancova` — ANCOVA for change-from-baseline endpoints.
- `tm_t_logistic` — logistic-regression tables for binary endpoints.
- `tm_t_shift_by_grade` — lab shift tables for safety reporting.

Browse `teal.modules.clinical::` in RStudio for the full list and signatures.

## `teal.transform::choices_selected()`

A `choices_selected()` object describes a variable selector input: the set of valid choices and the default selection. It powers nearly every dropdown in teal.

```r
arm_var <- teal.transform::choices_selected(
  choices = c("ARM", "ACTARM", "TRT01P"),
  selected = "ARM"
)
```

For lazy or cross-dataset references — e.g., letting users pick an `ADAE` variable while the module is anchored to `ADSL` — wrap inside a `data_extract_spec()`:

```r
ae_extract <- teal.transform::data_extract_spec(
  dataname = "ADAE",
  filter = teal.transform::filter_spec(
    vars = "AESEV",
    choices = c("MILD", "MODERATE", "SEVERE"),
    selected = "MODERATE"
  ),
  select = teal.transform::select_spec(
    choices = teal.transform::variable_choices("ADAE", c("AETERM", "AEDECOD")),
    selected = "AEDECOD"
  )
)
```

Modules consume the spec and render the filter + selector UI automatically.

## `teal.slice::teal_slices()`

`teal_slices()` is the pre-set filter state passed to `teal::init(filter = ...)`. Each `teal_slice()` targets one dataset/variable.

```r
filters <- teal.slice::teal_slices(
  # Single numeric range
  teal.slice::teal_slice(
    dataname = "ADSL",
    varname = "AGE",
    selected = c(18, 75)
  ),
  # Multi-select categorical
  teal.slice::teal_slice(
    dataname = "ADSL",
    varname = "SEX",
    selected = c("F", "M")
  ),
  # Locked filter (user cannot remove)
  teal.slice::teal_slice(
    dataname = "ADSL",
    varname = "SAFFL",
    selected = "Y",
    fixed = TRUE
  )
)
```

`fixed = TRUE` is critical for safety populations — lock `SAFFL == "Y"` so a user cannot accidentally render an AE table over the full enrolled set.

## Custom module authoring — `teal::module()`

When standard modules don't cover your analysis, write your own. The required signature wraps a Shiny module in `teal::module()` so it integrates with the filter panel, reactive data, and reproducibility log.

```r
tm_my_custom <- function(label = "My module",
                        dataname = "ADSL",
                        arm_var = teal.transform::choices_selected("ARM", "ARM")) {
  teal::module(
    label = label,
    server = function(id, data) {
      shiny::moduleServer(id, function(input, output, session) {
        # data is a reactive returning the filtered dataset bundle.
        # Access ADSL with data()[["ADSL"]].
        output$summary <- shiny::renderPrint({
          adsl <- data()[[dataname]]
          arm <- input$arm
          adsl |>
            dplyr::group_by(.data[[arm]]) |>
            dplyr::summarise(n = dplyr::n(), mean_age = mean(AGE, na.rm = TRUE))
        })
      })
    },
    ui = function(id, ...) {
      ns <- shiny::NS(id)
      shiny::tagList(
        teal.transform::data_extract_ui(
          id = ns("arm"),
          label = "Arm variable",
          data_extract_spec = arm_var
        ),
        shiny::verbatimTextOutput(ns("summary"))
      )
    },
    datanames = dataname
  )
}
```

**Never construct teal modules with raw `shiny::moduleServer` at the top level** — always wrap in `teal::module()`. A bare `moduleServer` will not receive the filtered reactive `data()`, will not appear in the filter panel's data-name routing, and will not contribute to the reproducibility log. The wrapper is what makes a module a *teal* module.

The `datanames` argument tells teal which datasets this module needs; the filter panel scopes its UI accordingly.

## Reproducibility log (`teal.code`)

Every reactive event in a teal app emits the equivalent R code. Users click the "Show R code" button (or "Download R script") and get a self-contained script that recreates the exact analysis they see on screen — including filter state, selector values, and the model call.

This is the single most important teal feature for regulated environments:

- **GxP/Part-11**: the displayed analysis is auditable; reviewers receive deterministic R code, not screenshots.
- **Statistician handoff**: an exploratory finding turns into a TLF (table/listing/figure) by lifting the captured code into a production script.
- **Reproducibility**: combined with `renv` lockfiles and pinned NEST versions, the captured code reproduces the analysis on a clean machine.

Custom modules contribute to the log automatically *if and only if* they use `teal`-aware reactives. Plain `shiny::reactive()` outputs render but do not appear in the script. Use `teal.code::eval_code()` and `teal_reactive()` patterns from the NEST docs to capture custom analyses.

## Validation reports

NEST packages release on a CRAN-like cadence via `r-universe.dev` and (for tagged versions) CRAN itself. FDA/EMA-aware validation is not a property of teal itself — it is a property of *your sponsor's* validation process applied to a pinned version of the framework on a controlled deployment.

The conventional pharma path:

1. Pin NEST package versions in an `renv.lock`.
2. Run sponsor validation against that lockfile (URS/FRS/IQ/OQ/PQ traceability).
3. Deploy to **Posit Connect** (preferred) or Posit Workbench with the same lockfile.
4. Tag the app version, dataset bundle version, and lockfile hash in the reproducibility log header.

See `deployment.md` for the deploy-time pieces.

## Bridge to `r-clinical`

This reference deliberately stops at app structure. For:

- the meaning and derivation of `USUBJID`, `STUDYID`, `SAFFL`, `ITTFL`, `ARM` vs `ACTARM` vs `TRT01P`,
- ADaM variable conventions (`AVAL` vs `AVALC`, `AVISIT`/`AVISITN`, `PARAMCD`/`PARAM`, `CNSR`, `CHG`/`PCHG`),
- ADaMIG class rules (`ADSL` is one row per subject; `BDS` datasets are one row per parameter-visit; `OCCDS` are one row per occurrence),
- SDTM domain definitions (`DM`, `AE`, `LB`, `VS`, `EX`, ...) and the SDTM-to-ADaM mapping,

defer to the `r-clinical` skill at `../../r-clinical/SKILL.md`. teal handles the *app structure*; r-clinical handles the *domain*. A teal app built on data the analyst doesn't understand at the domain level will produce slick-looking but invalid analyses.

## Common gotchas

| Trap | Why it fails | Fix |
|---|---|---|
| `"no datasets defined"` error at startup | Forgot to wrap data in `cdisc_dataset()` or omitted `keys` | Use `cdisc_data(adsl = cdisc_dataset("ADSL", ADSL, keys = c("STUDYID", "USUBJID")))` |
| Module shows empty selectors | `choices_selected()` references a variable not in `dataname` | Verify the variable exists in that domain; pass the correct `dataname` |
| Filter panel ignores my pre-set | Mismatched `dataname` in `teal_slice()` (e.g., `"adsl"` vs `"ADSL"`) | Match `dataname` exactly to the name registered in `cdisc_data()` |
| Custom-module reactivity broken | Wrote raw `shiny::moduleServer` instead of `teal::module()` | Wrap in `teal::module()` so filtered `data()` and the log are wired |
| Cross-module filter not propagating | Missing or inconsistent join keys in `cdisc_data()` | Define `keys` on every dataset; teal joins on shared keys |
| Reproducibility log empty for custom output | Used plain `renderPlot`/`renderTable` directly | Use teal-aware reactives (`teal.code::eval_code`, `teal_reactive`) so the code is captured |
| `tm_g_km` errors on `ADTTE` | `time_var`/`cnsr_var` selectors point at variables not in the actual `ADTTE` | Confirm `AVAL` and `CNSR` exist; otherwise pass the correct names |
| Filter panel cluttered with irrelevant vars | Did not scope `datanames` on a custom module | Set `datanames = "ADSL"` (or the actual list) on `teal::module()` |

## When NOT to use teal

- **Non-CDISC data shapes.** teal assumes ADaM/SDTM conventions: stable join keys, BDS-style long format, parameter codes. For arbitrary tidy data, the cost of conforming is higher than just writing Shiny modules. See `frameworks-decision.md`.
- **Fully custom UX.** teal's paradigm is a left-hand filter panel and tabbed analysis modules. If your stakeholders want a guided wizard, a single-page kiosk, or a non-tabular dashboard, base Shiny (or `golem`/`rhino`) is more flexible.
- **Small prototypes.** A two-day exploration doesn't need NEST's package surface. Start with base Shiny; promote to teal when you commit to clinical reporting at scale.
- **Non-pharma domains.** teal's conventions, modules, and naming are all clinical-trial-specific. Use it for what it's for.

## Cross-links

- `frameworks-decision.md` — when to choose teal versus base Shiny, `golem`, or `rhino`.
- `testing.md` — testing strategies for teal apps (module tests, snapshot of reproducibility-log output, end-to-end with `shinytest2`).
- `deployment.md` — Posit Connect deployment with `renv` lockfiles and pinned NEST versions.
- `../../r-clinical/SKILL.md` — ADaM/SDTM domain semantics, ADaMIG variable rules, SDTM domain definitions.
