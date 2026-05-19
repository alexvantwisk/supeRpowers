# mcp-repl Setup (Persistent R Sessions for Claude)

[posit-dev/mcp-repl](https://github.com/posit-dev/mcp-repl) is an MCP server
written in Rust, maintained by Posit, that exposes a **persistent R (or
Python) subprocess** as two MCP tools: `repl` and `repl_reset`. Variables,
loaded packages, fitted models, and open graphics devices survive across
tool calls within an agent session — Claude Code owns the R process for
the duration.

Use this path when you want Claude to do **agent-driven analysis without
attaching to an IDE**. For pairing with a running RStudio / Positron
console, use btw + mcptools instead (see `SKILL.md` Path B).

License: Apache-2.0.

---

## Install

### Option 1 — Prebuilt binary (recommended for reproducibility)

Releases ship binaries for macOS arm64, Linux x86_64, and Windows x86_64
on the [GitHub releases page](https://github.com/posit-dev/mcp-repl/releases).

```bash
# macOS arm64 example
curl -L -o mcp-repl https://github.com/posit-dev/mcp-repl/releases/latest/download/mcp-repl-aarch64-apple-darwin
chmod +x mcp-repl
mv mcp-repl /usr/local/bin/      # or ~/.local/bin if you prefer user-local
```

Verify:

```bash
mcp-repl --help
```

### Option 2 — Build from source via cargo

Requires the Rust toolchain ([rustup.rs](https://rustup.rs)).

```bash
cargo install --git https://github.com/posit-dev/mcp-repl --locked
```

Binary lands in `~/.cargo/bin/mcp-repl`. Ensure `~/.cargo/bin` is on `PATH`.

Caveat: `cargo install --git` cannot pin a specific version without
`--rev`. Prefer prebuilt binaries when reproducibility matters.

### Windows aarch64

No prebuilt binary. Install Rust via rustup, then `cargo install --git ...`
as above. If that's not available, fall back to btw + mcptools only.

---

## Register with Claude Code

Project-scoped registration with sandbox on by default:

```bash
claude mcp add -s "project" mcp-repl -- mcp-repl --sandbox
```

User-scoped (available across all projects):

```bash
claude mcp add -s "user" mcp-repl -- mcp-repl --sandbox
```

Verify:

```bash
claude mcp list
```

Expect `mcp-repl` with status `connected`.

---

## Sandbox flag

`--sandbox` disables network access and restricts filesystem writes inside
the agent's R process. Recommended posture:

- **Start sandboxed.** Most analysis work doesn't need network.
- **Install packages from your normal R session** (RStudio terminal, system
  shell, etc.) — the agent only consumes packages that are already
  installed in the user library it can see.
- **One-off agent-driven installs** require re-registering without
  `--sandbox`. Drop sandbox only for that session, then put it back.

If you see `cannot open URL` or `install.packages` hanging, the sandbox is
the cause. See `mcp-troubleshooting.md`.

---

## `--oversized-output`

By default, very large tool replies are truncated to keep the protocol
responsive. For workflows where Claude needs to see the full output of
`summary()` on a wide model or a wide `head(df, 100)`, pass
`--oversized-output`:

```bash
claude mcp add -s "project" mcp-repl -- mcp-repl --sandbox --oversized-output
```

Restart Claude Code to reconnect.

---

## The two tools

### `repl(code, timeout?)`

Execute arbitrary R code in the persistent subprocess. State that persists
between calls:

- Bound variables in `.GlobalEnv`
- Loaded packages (`library()`, `require()`)
- Fitted models and complex objects
- Open graphics devices (`dev.cur()`)
- Random seed state
- Working directory changes

`timeout` is an integer in seconds. Long-running jobs (large MCMC fits,
heavy `caret`/`tidymodels` tuning) need an explicit timeout; the default
is conservative.

Signal handling: Claude can interrupt a running `repl` call with SIGINT —
equivalent to pressing Esc / Ctrl-C in a console.

### `repl_reset()`

Drop the current R subprocess and start a fresh one. Use when:

- Switching to an unrelated task and you want a clean slate
- Memory has bloated from large intermediate objects
- A package state is corrupted (e.g. `data.table` warnings persisting)
- You want to test that a script runs from scratch

Faster than restarting Claude Code; equivalent to `Restart R` in RStudio.

---

## Comparison vs btw + mcptools

| Dimension | mcp-repl | btw + mcptools |
|---|---|---|
| Process ownership | Claude Code owns the R subprocess | User owns it (RStudio/Positron) |
| IDE awareness | None (headless) | Inspects the running IDE's session via `mcptools::mcp_session()` |
| Persistence | Yes, across calls within an agent session | Yes, as long as the IDE console stays alive |
| Survives IDE restart | N/A (no IDE involved) | No — must re-run `mcp_session()` |
| Sandbox option | Built-in (`--sandbox`) | None |
| Install effort | Single binary | R packages + `.Rprofile` step |
| Best for | Headless agent work, autonomous analysis | Pairing with you while you work in RStudio/Positron |
| Tool surface | `repl`, `repl_reset` | Six tool groups (docs, pkg, env, run, search, session) |
| Introspection helpers | None (just execute) | `btw_tool_env_describe_data_frame`, structured help/news/vignettes |

The two are **complementary, not competing**. They can be registered
simultaneously — tool names don't collide.

---

## Concurrent Claude Code sessions

Each Claude Code session that connects to mcp-repl spawns its **own**
R subprocess with **separate state**. If you open the project in two
windows, you get two independent R sessions. This is usually what you
want (parallel exploration), but be aware that variables in one don't
appear in the other.

---

## Removing the registration

```bash
claude mcp remove mcp-repl
```

The binary stays installed; only the Claude Code registration is dropped.
