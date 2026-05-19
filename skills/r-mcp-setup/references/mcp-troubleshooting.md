# MCP Troubleshooting

Common issues and fixes for MCP server setup with mcp-repl, btw, and
mcptools.

## mcp-repl issues

### M1. `mcp-repl: command not found`

**Symptom:** `mcp-repl --help` fails with "command not found" or
`claude mcp list` shows the server as disconnected.

**Cause:** Binary not on `PATH`. Two common cases:

1. **Built via `cargo install`** — binary is in `~/.cargo/bin`, which may
   not be on `PATH`. Add to your shell rc:

   ```bash
   # ~/.zshrc or ~/.bashrc
   export PATH="$HOME/.cargo/bin:$PATH"
   ```

2. **Prebuilt binary downloaded** — needs `chmod +x` and to live somewhere
   on `PATH`:

   ```bash
   chmod +x mcp-repl
   mv mcp-repl /usr/local/bin/        # macOS / Linux system-wide
   # or
   mkdir -p ~/.local/bin && mv mcp-repl ~/.local/bin/   # user-local
   ```

Verify with `which mcp-repl`.

### M2. `claude mcp list` shows mcp-repl as `disconnected`

**Symptom:** Server is registered but Claude Code can't connect.

**Cause (usually):** mcp-repl can't find R. It calls `R RHOME` at startup.

**Diagnose:**

```bash
R --version       # should print version
R RHOME           # should print the R install root
```

If either fails, R isn't on `PATH` or `RHOME` is overridden by an env var.
Fix the shell environment, then restart Claude Code.

### M3. `install.packages()` fails with "cannot open URL"

**Symptom:** `repl` returns a network error when you ask Claude to install
a package.

**Cause:** mcp-repl is running with `--sandbox`, which blocks network
access.

**Fixes (in order of preference):**

1. **Install from your normal R session.** Open a terminal or RStudio and
   run `install.packages("...")` there. mcp-repl shares the user library,
   so the agent will see the package on the next call.
2. **Re-register without `--sandbox`** for a one-off install, then put
   sandbox back:

   ```bash
   claude mcp remove mcp-repl
   claude mcp add -s "project" mcp-repl -- mcp-repl
   # ... install package via Claude ...
   claude mcp remove mcp-repl
   claude mcp add -s "project" mcp-repl -- mcp-repl --sandbox
   ```

### M4. `repl` returns truncated output

**Symptom:** A `summary()` on a wide model or `head(df, 100)` cuts off.

**Fix:** Add `--oversized-output` to the registration:

```bash
claude mcp remove mcp-repl
claude mcp add -s "project" mcp-repl -- mcp-repl --sandbox --oversized-output
```

Restart Claude Code so the connection re-establishes.

---

## btw / mcptools issues

### 1. MCP Server Won't Start

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

## 7. `cc_env()` shows an empty workspace via Claude

**Symptom:** You have objects in your Positron R session, but when Claude calls
`cc_env()` through `r-btw`, it returns `(empty)`.

**Cause:** `btw_tool_run_r()` is hitting a fresh R subprocess, not the Positron
session bridged by `mcptools::mcp_session()`.

**Fix:**

1. Confirm `mcptools::mcp_session()` is running in the Positron console (check
   the startup message — declaring it in `.Rprofile` is not enough if the
   session was launched before the line was added)
2. Confirm `.mcp.json` registers `mcptools::mcp_server()` for stateful tools
   (not a bare `Rscript -e "btw::btw_mcp_server(...)"` which spawns its own
   process)
3. Restart Claude Code so the MCP connection re-establishes against the
   running session
