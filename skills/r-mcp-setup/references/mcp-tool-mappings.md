# MCP Tool Mappings — btw Groups and mcp-repl to Skills

Central reference for skill/agent MCP tool selection and Bash fallback commands.

---

## How Skills Detect MCP Availability

The session-start hook injects `"MCP: available"` into context when btw tools
or mcp-repl are registered. Skills check for this substring to choose
execution path:

```
if context contains "MCP: available"
  → use mcp-repl `repl` (persistent state) or btw_tool_* (structured result)
else
  → use Bash Rscript fallback (parse text output)
```

---

## Persistent Execution (mcp-repl)

Orthogonal to the btw introspection groups — `repl` is full agent-owned
execution where state persists across calls.

**Tools:**
- `repl` — execute arbitrary R code in a long-lived Claude-owned subprocess
- `repl_reset` — drop the subprocess and start a fresh R session

**Benefits:** r-data-analysis, r-stats, r-tidymodels, r-bayesian, r-targets,
r-debugging, r-performance — any skill that benefits from carrying objects
across multiple tool calls (e.g. fit a model, then inspect coefficients,
then run diagnostics — all without re-loading data).

| Capability | mcp-repl | btw equivalent | Bash fallback |
|---|---|---|---|
| Execute R, state persists across calls | `repl(code)` | `btw_tool_run_r` (no persistence between calls in agent context) | `Rscript -e` (no persistence) |
| Reset session state | `repl_reset()` | n/a (restart server) | n/a |
| Sandbox network/FS | `--sandbox` flag | n/a | n/a |

**Combine with btw** when both are registered: use `repl` to fit a model,
then `btw_tool_env_describe_data_frame` to inspect a data frame that lives
in the user's IDE session (different process, separate state).

**Bash fallback:**
```bash
Rscript -e 'fit <- lm(mpg ~ wt, mtcars); summary(fit)'
```
Note: Bash spawns a fresh R process every call — no persistence.

---

## Tool Group Reference (btw)

### docs — Package Documentation

**Tools:**
- `btw_tool_docs_help_page` — fetch a single help page
- `btw_tool_docs_package_help_topics` — list all topics in a package
- `btw_tool_docs_vignette` — fetch a named vignette
- `btw_tool_docs_available_vignettes` — list all vignettes in a package
- `btw_tool_docs_package_news` — fetch package NEWS / changelog

**Benefits:** All skills. Documentation lookup is universal.

**MCP usage:**
```
btw_tool_docs_help_page(package = "dplyr", topic = "mutate")
btw_tool_docs_vignette(package = "ggplot2", topic = "ggplot2-specs")
```

**Bash fallback:**
```bash
Rscript -e 'utils::help("mutate", package = "dplyr")'
```

---

### pkg — Package Development Tools

**Tools:**
- `btw_tool_pkg_test` — run testthat tests with optional filter
- `btw_tool_pkg_check` — run R CMD CHECK
- `btw_tool_pkg_document` — run roxygen2 documentation generation
- `btw_tool_pkg_coverage` — measure test coverage via covr

**Benefits:** r-tdd, r-package-dev, r-debugging

**MCP usage:**
```
btw_tool_pkg_test(filter = "validate")
btw_tool_pkg_check()
```

**Bash fallback:**
```bash
Rscript -e 'devtools::test(filter = "validate")'
Rscript -e 'devtools::check()'
```

---

### env — Live Session Environment

**Tools:**
- `btw_tool_env_describe_data_frame` — schema + summary of a data frame object
- `btw_tool_env_describe_environment` — list all objects in an R environment

**Benefits:** r-data-analysis, r-debugging, r-stats, r-clinical, r-performance, r-targets

**Requirement:** User must run `mcptools::mcp_session()` in their live R session.
Without it, tools see only the MCP server's own empty R process.

**MCP usage:**
```
btw_tool_env_describe_data_frame(name = "my_df")
btw_tool_env_describe_environment()
```

**Bash fallback:** No direct equivalent for live session objects. For static files:
```bash
Rscript -e 'str(readRDS("data.rds"))'
Rscript -e 'dplyr::glimpse(readr::read_csv("data.csv"))'
```
When MCP is unavailable, ask the user to paste `str()` or `glimpse()` output.

---

### run — Execute R Code

**Tools:**
- `btw_tool_run_r` — execute arbitrary R code in the connected R session

**Benefits:** r-data-analysis, r-debugging, r-stats, r-performance, r-tidymodels, r-targets

**MCP usage:**
```
btw_tool_run_r(code = "summary(mtcars)")
```

Best combined with `btw_tool_env_describe_data_frame` to inspect results.

**Bash fallback:**
```bash
Rscript -e 'summary(mtcars)'
```
Note: Bash runs in a fresh R process — cannot access live session objects.

---

### search — CRAN Package Discovery

**Tools:**
- `btw_tool_search_packages` — search CRAN by keyword
- `btw_tool_search_package_info` — fetch metadata for a specific package

**Benefits:** r-package-dev, r-project-setup, r-dependency-manager agent

**MCP usage:**
```
btw_tool_search_packages(query = "spatial data")
btw_tool_search_package_info(package = "sf")
```

**Bash fallback:**
```bash
Rscript -e 'available.packages()[grep("spatial", available.packages()[,"Package"]),]'
```
Web search is also effective for discovery.

---

### session — R Session Information

**Tools:**
- `btw_tool_session_check_package_installed` — check if a package is installed
- `btw_tool_session_package_info` — version and load path for an installed package
- `btw_tool_session_platform_info` — R version, OS, locale, loaded packages

**Benefits:** r-project-setup, r-dependency-manager agent

**MCP usage:**
```
btw_tool_session_platform_info()
btw_tool_session_check_package_installed(package = "targets")
```

**Bash fallback:**
```bash
Rscript -e 'sessionInfo()'
Rscript -e 'requireNamespace("targets", quietly = TRUE)'
```

---

## Quick Lookup: Skill → Recommended Tool Groups

| Skill | Primary MCP Groups |
|-------|--------------------|
| r-data-analysis | run, env, docs |
| r-visualization | docs, run |
| r-stats | run, env, docs |
| r-clinical | run, env, docs |
| r-tdd | pkg, docs |
| r-package-dev | pkg, search, docs |
| r-debugging | run, env, pkg |
| r-performance | run, env, docs |
| r-shiny | run, docs |
| r-tidymodels | run, env, docs |
| r-targets | run, env, docs |
| r-project-setup | session, search |
| r-quarto | run, docs |
| r-tables | run, docs |
| r-mcp-setup | session, pkg, repl |
