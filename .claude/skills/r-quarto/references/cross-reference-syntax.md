# Cross-Reference Syntax

Complete reference for Quarto cross-references: figures, tables, equations,
sections, theorems, and custom types.

---

## Figures

**Label rule:** chunk label must start with `fig-`.

````markdown
```{r}
#| label: fig-scatter
#| fig-cap: "Scatter plot of MPG vs weight."
#| fig-alt: "Alt text for accessibility."

library(ggplot2)
mtcars |>
  ggplot(aes(wt, mpg)) +
  geom_point()
```
````

Reference: `@fig-scatter` → "Figure 1"

**Markdown figure** (non-code):
```markdown
![Caption text.](path/to/image.png){#fig-myimage}
```

**Figure shortcaption** (for list of figures):
```r
#| label: fig-scatter
#| fig-cap: "Long detailed caption here."
#| fig-scap: "Short caption for LoF."
```

---

## Tables

**Label rule:** chunk label must start with `tbl-`.

````markdown
```{r}
#| label: tbl-summary
#| tbl-cap: "Descriptive statistics for mtcars."

knitr::kable(summary(mtcars[, 1:4]))
```
````

Reference: `@tbl-summary` → "Table 1"

**Markdown table:**
```markdown
| Col A | Col B |
|-------|-------|
| 1     | 2     |

: Caption for the table. {#tbl-mydata}
```

---

## Equations

Use `{#eq-name}` at the end of a display math block:

```markdown
$$
\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i
$$ {#eq-mean}
```

Reference: `@eq-mean` → "Equation 1"

**Inline math** cannot be cross-referenced — display math only.

---

## Sections

Add `{#sec-name}` to any heading:

```markdown
## Data Preparation {#sec-data-prep}

See @sec-data-prep for details.
```

Reference: `@sec-data-prep` → "Section 2.1" (number depends on position)

Works across chapters in books. `@sec-` prefix is required.

---

## Listings (Code Blocks)

**Label rule:** must start with `lst-`.

````markdown
```{.r}
#| label: lst-model
#| lst-cap: "Linear model fitting code."

fit <- lm(mpg ~ wt + cyl, data = mtcars)
```
````

Reference: `@lst-model` → "Listing 1"

---

## Subfigures

```r
#| label: fig-combo
#| fig-cap: "Combined figure."
#| fig-subcap:
#|   - "Panel A: Distribution."
#|   - "Panel B: Scatter."
#| layout-ncol: 2

hist(mtcars$mpg)
plot(mtcars$wt, mtcars$mpg)
```

Reference parent: `@fig-combo` → "Figure 1"
Reference subfigure: `@fig-combo-1` → "Figure 1a", `@fig-combo-2` → "Figure 1b"

**Markdown subfigures:**
```markdown
::: {#fig-panels layout-ncol=2}
![Panel A](a.png){#fig-panel-a}

![Panel B](b.png){#fig-panel-b}

Combined caption for all panels.
:::
```

---

## Subtables

```r
#| label: tbl-both
#| tbl-cap: "Two tables side by side."
#| tbl-subcap:
#|   - "Left table."
#|   - "Right table."
#| layout-ncol: 2

knitr::kable(head(mtcars[, 1:3]))
knitr::kable(head(mtcars[, 4:6]))
```

Reference: `@tbl-both-1` → "Table 1a", `@tbl-both-2` → "Table 1b"

---

## Theorems and Proofs

Built-in environments: `thm`, `lem`, `cor`, `prp`, `cnj`, `def`, `exm`, `exr`.

```markdown
::: {#thm-clt}
## Central Limit Theorem

As $n \to \infty$, the sample mean converges in distribution to
$\mathcal{N}(\mu, \sigma^2/n)$.
:::

Proof of @thm-clt follows from characteristic functions.

::: {.proof}
Details of proof here.
:::
```

Reference: `@thm-clt` → "Theorem 1"

**Other environments:**
```markdown
::: {#def-variance}
## Variance

The variance of $X$ is $\text{Var}(X) = E[(X - \mu)^2]$.
:::

::: {#lem-helper}
A helpful lemma here.
:::

::: {#exm-usage}
## Example

An example of the concept.
:::
```

---

## Custom Cross-Reference Types

Define custom types in `_quarto.yml`:

```yaml
crossref:
  custom:
    - kind: float
      key: vid
      latex-env: video
      reference-prefix: Video
      space-before-numbering: false
    - kind: float
      key: sup
      latex-env: supplement
      reference-prefix: Supplement
      space-before-numbering: false
```

Usage:
```markdown
::: {#vid-demo}
{{< video demo.mp4 >}}

Video caption.
:::

See @vid-demo for the demonstration.
```

---

## Numbering Configuration

Customize prefixes and numbering in YAML:

```yaml
crossref:
  fig-title: "Fig."          # Prefix in text
  tbl-title: "Tab."
  eq-prefix: "Eq."
  sec-prefix: "Sec."
  fig-labels: arabic         # arabic | roman | Roman | alpha | Alpha
  tbl-labels: arabic
  subref-labels: alpha       # For subfigures: a, b, c
  chapters: true             # Chapter-based numbering (books): Figure 1.1
```

---

## Reference Styles

```markdown
@fig-scatter        → Figure 1
[@fig-scatter]      → (Figure 1)      — parenthetical
-@fig-scatter       → 1               — number only (suppress prefix)
```

Multiple refs:
```markdown
@fig-scatter and @fig-hist
[@fig-scatter; @tbl-summary]
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Label doesn't start with `fig-` or `tbl-` | Add the correct prefix |
| Reference with `\ref{fig:x}` (LaTeX style) | Use `@fig-x` instead |
| Subfigure ref `@fig-combo-a` | Use `@fig-combo-1` (numeric, not letter) |
| Duplicate label across chunks | Labels must be globally unique |
| Missing `fig-cap` or `tbl-cap` | Caption required for cross-reference to render |
| Equation label outside `$$ $$` block | Must be `$$ ... $$ {#eq-name}` |
