# Alternative UI Frameworks

bslib (Bootstrap 5) is the default. The alternatives below exist for
narrow use cases where a hard requirement forces a different stack. See
`frameworks-decision.md` for the broader decision matrix.

## bs4Dash

Bootstrap 4 dashboard look-alike based on AdminLTE 3. Useful when you want
the classic shinydashboard sidebar/header layout but on Bootstrap 4
without redesigning around bslib.

```r
install.packages("bs4Dash")

ui <- bs4Dash::dashboardPage(
  header  = bs4Dash::dashboardHeader(title = "demo"),
  sidebar = bs4Dash::dashboardSidebar(),
  body    = bs4Dash::dashboardBody("hello")
)
server <- function(input, output, session) {}
shiny::shinyApp(ui, server)
```

When to pick: shinydashboard refugees who want AdminLTE 3 without bslib.
Gotcha: it is Bootstrap 4, not 5, so it cannot be mixed with bslib's
`page_navbar()` or Bootstrap 5 themes.

## shinyMobile

Framework7-based UI optimised for phones and tablets. Useful for
field-data-capture apps and mobile-first deployments.

```r
install.packages("shinyMobile")

ui <- shinyMobile::f7Page(
  title = "demo",
  shinyMobile::f7SingleLayout(navbar = shinyMobile::f7Navbar(title = "demo"),
                              "hello")
)
server <- function(input, output, session) {}
shiny::shinyApp(ui, server)
```

When to pick: mobile-first apps where touch ergonomics matter more than
desktop dashboards. Gotcha: heavy JS bundle and not designed for rich
multi-panel dashboards; performance suffers on data-dense layouts.

## shiny.semantic

Wraps Semantic UI / Fomantic UI components. Useful when a design team is
already committed to the Semantic UI design language.

```r
install.packages("shiny.semantic")

ui <- shiny.semantic::semanticPage(
  title = "demo",
  "hello"
)
server <- function(input, output, session) {}
shiny::shinyApp(ui, server)
```

When to pick: org-wide design system standardised on Semantic UI.
Gotcha: smaller component ecosystem than bslib, and several bslib idioms
(cards, value boxes, sidebar layouts) do not translate cleanly.

## argonDash

Creative Tim Argon design adapted for Shiny. Useful for marketing-style
landing dashboards with a polished consumer aesthetic.

```r
install.packages("argonDash")

ui <- argonDash::argonDashPage(
  header = argonDash::argonDashHeader(),
  sidebar = argonDash::argonDashSidebar(),
  body = argonDash::argonDashBody("hello")
)
server <- function(input, output, session) {}
shiny::shinyApp(ui, server)
```

When to pick: marketing-style dashboards prioritising visual polish.
Gotcha: low maintenance velocity; verify last release date before adopting.

Default remains bslib (Bootstrap 5). Pick an alternative only if a hard requirement forces it.
