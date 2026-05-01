# brms Model Formulas

`brms` extends the standard R formula syntax. Most non-trivial Bayesian
work in R is built on these forms.

All code uses base pipe `|>`, `<-` for assignment, and `snake_case`.

---

## Standard Regression

```r
# Linear / GLM
y ~ x1 + x2

# Interaction
y ~ x1 * x2                       # x1 + x2 + x1:x2

# Polynomial via poly() — orthogonal by default
y ~ poly(x, 2)

# Suppress intercept
y ~ 0 + x
```

---

## Multilevel / Hierarchical

```r
# Random intercept per group
y ~ x + (1 | group)

# Random intercept + slope per group, correlated
y ~ x + (1 + x | group)

# Random slope only (no random intercept)
y ~ x + (0 + x | group)

# Crossed groupings (e.g. subject x item)
y ~ x + (1 | subject) + (1 | item)

# Nested groupings (school within district)
y ~ x + (1 | district / school)   # equivalent to (1 | district) + (1 | district:school)

# Uncorrelated random intercept and slope
y ~ x + (1 || group)              # double-bar = no correlation
```

`brms` accepts the lme4 syntax verbatim; the multivariate `lkj()` prior on
random-effect correlation kicks in automatically.

---

## Distributional Models

Predict the scale parameter, not just the mean. Use `bf()` to bundle
multiple formulas.

```r
# Heteroscedastic linear model — sigma also depends on group
bf(y ~ x1 + x2, sigma ~ group)

# Negative-binomial with shape parameter modeled
bf(count ~ offset(log(exposure)) + x, shape ~ region)

# Beta regression with phi parameter modeled
bf(prop ~ x, phi ~ x, family = Beta())
```

The auxiliary parameter (`sigma`, `shape`, `phi`, `nu`) becomes a
linear-modeled quantity. Set priors with `class = "b", dpar = "sigma"`.

---

## Nonlinear Models

```r
# Asymptotic exponential — explicit nonlinear formula
bf(y ~ b1 * (1 - exp(-b2 * x)),
   b1 + b2 ~ 1 + (1 | group),
   nl = TRUE)

# Each named coefficient gets its own sub-formula. Priors must be
# specified per coefficient class:
prior(normal(100, 20), nlpar = "b1") +
prior(normal(0.1, 0.05), nlpar = "b2", lb = 0)
```

---

## Smooth Terms (mgcv-style splines)

```r
# Penalized smooth, default thin-plate basis k = 10
y ~ s(x)

# Tensor product smooth (interaction of two smooths)
y ~ te(x1, x2)

# By-factor smooth — separate smooth per group level
y ~ s(x, by = group)
```

`brms` uses `mgcv` machinery. Priors on smooth SD via
`prior(student_t(3, 0, 2.5), class = "sds")`.

---

## Monotonic Predictors

For ordered categorical predictors where you assume a monotonic effect
(e.g. education levels) but don't want to assume linearity:

```r
y ~ mo(education_level)           # education_level must be ordered factor
```

Adds a Dirichlet prior on simplex of step sizes; saner than treating an
ordered factor as numeric.

---

## Mixture Models

```r
mix2 <- mixture(gaussian(), gaussian())
fit  <- brm(bf(y ~ x), data = df, family = mix2,
            prior = c(prior(normal(0, 5), Intercept, dpar = "mu1"),
                      prior(normal(5, 5), Intercept, dpar = "mu2"),
                      prior(dirichlet(c(1, 1)), theta)))
```

For two-component mixtures, label-switching is the most common failure —
constrain ordering with `prior(constant(1), Intercept, dpar = "mu1")`
or post-hoc relabel.

---

## Categorical & Ordinal Outcomes

```r
# Multinomial / categorical
brm(y ~ x, family = categorical())              # y is a factor

# Cumulative ordinal (proportional-odds)
brm(rating ~ x, family = cumulative())

# Adjacent-category, sequential, etc.
brm(rating ~ x, family = acat())
brm(rating ~ x, family = sratio())
```

---

## Survival / Censored Outcomes

```r
# Right-censored survival via cens()
brm(time | cens(censored) ~ x, family = weibull(),
    data = df)                                  # censored is 0/1
```

For full clinical-trial survival modeling, use r-clinical instead.

---

## Multivariate Outcomes

```r
# Two correlated outcomes — residual correlation modeled
mv_fit <- brm(
  bf(y1 ~ x1 + x2) + bf(y2 ~ x1 + x2) + set_rescor(TRUE),
  data = df
)
```

---

## Group-Level (Random) Coefficients in Nonlinear / Distributional Models

The lme4 `(1 + x | group)` syntax works inside any sub-formula:

```r
bf(y ~ b1 + b2 * x,
   b1 ~ 1 + (1 | group),
   b2 ~ 1 + (1 | group),
   nl = TRUE)
```

---

## Inspecting the Generated Stan Code

```r
make_stancode(formula, data = df, family = ...)
make_standata(formula, data = df, family = ...)
```

Useful when debugging strange diagnostics — the Stan model brms generates
is sometimes the answer.
