# MCP Troubleshooting

Common issues and fixes for MCP server setup with btw and mcptools.

## 1. MCP Server Won't Start

**Symptom:** `claude mcp list` shows the server, but no tools appear.

**Diagnose:** Run the server manually:

```bash
Rscript -e "btw::btw_mcp_server()"
```

**Fix — missing packages:**

```r
install.packages(c("mcptools", "btw"))
```

**Fix — renv project:**

```r
renv::install("btw")
renv::install("mcptools")
renv::snapshot()
```

## 2. Windows Path Issues

**Symptom:** `Rscript` not found when the MCP server starts.

**Fix:** Use the full path to `Rscript.exe` in registration:

```bash
claude mcp add -s "project" r-btw -- \
  "C:/Program Files/R/R-4.x.x/bin/Rscript.exe" \
  -e "btw::btw_mcp_server()"
```

Replace `R-4.x.x` with your installed version (e.g., `R-4.4.1`).

**Alternative:** Add R's `bin/` to the PATH before launching Claude Code.

## 3. renv Conflicts

**Symptom:** MCP server can't find packages even though they are installed.

**Cause:** The MCP server inherits renv, but `btw`/`mcptools` aren't in the
renv library.

**Fix:**

```r
renv::install("btw")
renv::install("mcptools")
renv::snapshot()
```

## 4. Positron Session Not Discoverable

**Symptom:** `env_*` tools return empty; `run_r` executes in a fresh process
instead of the interactive Positron session.

**Fix:** In the Positron R console, run:

```r
mcptools::mcp_session()
```

**Tip:** Add to `.Rprofile` so it runs automatically:

```r
if (interactive()) mcptools::mcp_session()
```

Edit `.Rprofile` with `usethis::edit_r_profile()`.

## 5. Multiple R Sessions / Wrong Session

**Symptom:** Tools respond but operate on the wrong workspace.

**Cause:** Multiple Positron instances each running `mcp_session()`.

**Fix:** Stop `mcp_session()` in sessions you don't want Claude to touch.
Keep only one registered at a time, then reconnect Claude Code.

## 6. Permission Denied on `claude mcp add`

**Symptom:** Command fails with a permissions error.

**Alternative:** Add the server manually to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "r-btw": {
      "command": "Rscript",
      "args": ["-e", "btw::btw_mcp_server()"],
      "scope": "project"
    }
  }
}
```

Restart Claude Code after editing.
