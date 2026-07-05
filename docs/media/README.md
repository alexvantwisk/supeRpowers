# Media assets

## `r-analysis.gif` (pending)

The README's Capabilities section reserves a spot for a demo GIF of the
`/r-analysis` workflow. It is **not yet recorded** — recording requires an
interactive Claude Code session, which cannot be done headlessly.

To produce it (maintainer step):

```bash
# 1. Record a ~30s /r-analysis walkthrough
asciinema rec docs/media/r-analysis.cast
# 2. Render to GIF with agg (asciinema's official renderer)
agg docs/media/r-analysis.cast docs/media/r-analysis.gif
```

Commit both `r-analysis.cast` (re-renderable, reviewable source) and the
rendered `r-analysis.gif`, then embed in `README.md`:

```markdown
![/r-analysis demo](docs/media/r-analysis.gif)
```

Regenerate whenever the `r-analysis` workflow skill's step list changes.
