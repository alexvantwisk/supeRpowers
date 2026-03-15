# Scaffold Templates

Reusable template file contents for R project scaffolding.

---

## .lintr Template

```
linters: linters_with_defaults(
    line_length_linter(120),
    object_name_linter(styles = "snake_case")
  )
encoding: "UTF-8"
```

---

## .gitignore Template (R Projects)

```gitignore
# R artifacts
.Rhistory
.RData
.Rproj.user/
*.Rproj.user

# renv
renv/library/
renv/staging/
renv/sandbox/
renv/cellar/

# targets
_targets/

# Quarto
.quarto/
_site/
_book/
*_files/

# Data (raw data should not be committed — too large or sensitive)
# data/raw/

# OS files
.DS_Store
Thumbs.db

# IDE
.Rproj.user/
.vscode/
.idea/
```

---

## .Rprofile Template

```r
if (file.exists("renv/activate.R")) {
  source("renv/activate.R")
}
```

---

## .Rproj Template

```
Version: 1.0

RestoreWorkspace: No
SaveWorkspace: No
AlwaysSaveHistory: Default

EnableCodeIndexing: Yes
UseSpacesForTab: Yes
NumSpacesForTab: 2
Encoding: UTF-8

RnwWeave: knitr
LaTeX: pdfLaTeX

AutoAppendNewline: Yes
StripTrailingWhitespace: Yes

BuildType: Package
PackageUseDevtools: Yes
PackageInstallArgs: --no-multiarch --with-keep.source
```

---

## Basic Shiny app.R Template

```r
library(shiny)
library(bslib)

ui <- page_sidebar(
  title = "My App",
  sidebar = sidebar(
    selectInput(
      "dataset",
      "Choose a dataset:",
      choices = c("mtcars", "iris", "pressure")
    ),
    numericInput(
      "obs",
      "Number of observations:",
      value = 10,
      min = 1,
      max = 100
    )
  ),
  card(
    card_header("Data Preview"),
    tableOutput("table")
  )
)

server <- function(input, output, session) {
  dataset <- reactive({
    get(input$dataset, "package:datasets")
  })

  output$table <- renderTable({
    dataset() |> head(input$obs)
  })
}

shinyApp(ui, server)
```

---

## Quarto _quarto.yml Templates

### Document

```yaml
project:
  type: default

format:
  html:
    toc: true
    code-fold: true
    theme: cosmo
  pdf:
    documentclass: article
    geometry: margin=1in
  docx:
    toc: true

execute:
  echo: true
  warning: false

bibliography: references.bib
```

### Presentation (revealjs)

```yaml
project:
  type: default

format:
  revealjs:
    theme: simple
    slide-number: true
    transition: slide
    incremental: true
    footer: "Presentation Title"

execute:
  echo: true
  warning: false
```

### Website

```yaml
project:
  type: website

website:
  title: "My Site"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - href: about.qmd
        text: About

format:
  html:
    theme: cosmo
    toc: true

execute:
  echo: true
  warning: false
```

### Book

```yaml
project:
  type: book

book:
  title: "My Book"
  author: "Author Name"
  date: today
  chapters:
    - index.qmd
    - 01-intro.qmd
    - 02-methods.qmd

format:
  html:
    theme: cosmo
  pdf:
    documentclass: book

bibliography: references.bib

execute:
  echo: true
  warning: false
```
