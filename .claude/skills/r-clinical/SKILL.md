---
name: r-clinical
description: >
  Use when performing clinical trial analysis, biostatistics, regulatory
  submissions, or biomedical research in R. Covers trial design, CDISC,
  survival endpoints, biomarkers, meta-analysis, and MCP integration.
---

# R Clinical Trials & Biostatistics

Biostatistics and clinical trial analysis in R: trial design, CDISC
standards, TLF generation, survival analysis, biomarkers, and meta-analysis.

All code uses base pipe `|>`, `<-` for assignment, and tidyverse style.

**Lazy references:**
- Read `references/cdisc-adam-guide.md` for ADaM/SDTM dataset structure,
  naming conventions, and `admiral` package patterns
- Read `references/tlf-templates.md` for ready-to-use TLF code patterns
  (demographics, AE, KM curves, forest plots, waterfall plots)

**Agent dispatch:** For statistical methodology questions (mixed models,
Bayesian approaches, multiplicity adjustments), dispatch to **r-statistician**.

---

## Trial Design & Power Analysis

```r
library(pwr)
library(gsDesign)

# Two-sample t-test: detect delta=0.5 with 80% power, alpha=0.05
pwr.t.test(d = 0.5, sig.level = 0.05, power = 0.80, type = "two.sample")

# Proportion test (e.g. ORR comparison)
pwr.2p.test(h = ES.h(p1 = 0.40, p2 = 0.25), sig.level = 0.05, power = 0.80)

# Group sequential design (interim analysis)
gs <- gsDesign(k = 2, test.type = 1, alpha = 0.025, beta = 0.20,
               sfu = sfO'Brien-Fleming)
gs$n.I   # sample sizes at each look
gs$upper$bound  # efficacy boundaries
```

Key packages: `pwr`, `gsDesign`, `rpact` (adaptive designs), `PowerTOST`
(bioequivalence). Follow ICH E9(R1) for estimand framework.

---

## Survival Endpoints (OS, PFS, DFS)

```r
library(survival)
library(survminer)

# Fit Kaplan-Meier
km_fit <- survfit(Surv(AVAL, CNSR == 0) ~ TRT01P, data = adtte)

# Log-rank test
survdiff(Surv(AVAL, CNSR == 0) ~ TRT01P, data = adtte)

# Cox proportional hazards
cox_fit <- coxph(Surv(AVAL, CNSR == 0) ~ TRT01P + AGE + SEX, data = adtte)
summary(cox_fit)   # HR, 95% CI, p-value

# Competing risks (e.g. death before progression)
library(cmprsk)
cr_fit <- cuminc(
  ftime = adtte$AVAL, fstatus = adtte$EVNTDESC,
  group = adtte$TRT01P
)
```

Censoring rules: follow CDISC ADTTE conventions — `CNSR = 1` for censored,
`CNSR = 0` for event. Landmark analysis: `survfit(..., start.time = t)`.

---

## Biomarkers: ROC & Cutpoints

```r
library(pROC)
library(cutpointr)

# ROC curve with 95% CI
roc_obj <- roc(response ~ biomarker, data = bm_df, ci = TRUE)
auc(roc_obj)       # AUC with 95% CI
plot(roc_obj, print.auc = TRUE)

# Optimal cutpoint (maximise Youden index)
cp <- cutpointr(data = bm_df, x = biomarker, class = response,
                method = maximize_metric, metric = youden)
summary(cp)

# Subgroup analysis scaffold
subgroups <- c("SEX", "AGEGR1", "RACE", "BMICAT")
subgroup_results <- purrr::map(subgroups, \(sg) {
  coxph(Surv(AVAL, CNSR == 0) ~ TRT01P,
        data = adtte |> dplyr::filter(.data[[sg]] == level))
})
```

---

## Meta-Analysis

```r
library(meta)
library(metafor)

# Fixed/random effects meta-analysis of log HRs
ma <- metagen(
  TE = log_hr, seTE = se_log_hr, studlab = study,
  data = meta_df, sm = "HR", method.tau = "REML",
  hakn = TRUE   # Hartung-Knapp correction
)
summary(ma)        # I², Q-test, pooled HR
forest(ma, sortvar = TE)

# Publication bias
funnel(ma)
metabias(ma, method.bias = "linreg")  # Egger's test
```

Heterogeneity: I² < 25% low, 25–75% moderate, > 75% high. Report I² and
τ² alongside pooled estimate. Use `metafor::rma()` for meta-regression.

---

## Genomics Bridge (Bioconductor)

```r
# Differential expression
library(DESeq2)
dds <- DESeqDataSetFromMatrix(count_matrix, col_data, design = ~ condition)
dds <- DESeq(dds)
results(dds, contrast = c("condition", "treated", "control"))

# Limma/voom for microarray or normalised RNA-seq
library(limma)
fit <- lmFit(expr_matrix, design_matrix) |> eBayes()
topTable(fit, coef = 2, adjust.method = "BH", n = Inf)

# Enrichment
library(clusterProfiler)
enrichGO(gene = sig_genes, OrgDb = "org.Hs.eg.db", ont = "BP")
```

For full Bioconductor workflows, use `BiocManager::install()` for packages
and consult Bioconductor workflows vignettes.

---

## Regulatory Context

- **ICH E9(R1):** Define estimand (population, treatment, endpoint, intercurrent
  events, summary measure) before analysis
- **ICH E6(R2):** GCP — traceability and reproducibility requirements
- **CONSORT:** Report randomisation, allocation concealment, and flow diagram
- **TLFs:** Every regulatory table/listing/figure must be traceable to ADaM

CONSORT flow diagram scaffold:

```r
library(ggplot2)
# Use DiagrammeR or a custom ggplot approach for CONSORT boxes
library(DiagrammeR)
grViz("
  digraph consort {
    Assessed [label='Assessed for eligibility\\n(n=500)']
    Excluded [label='Excluded (n=120)\\n- Not meeting criteria (n=80)\\n- Declined (n=40)']
    Randomised [label='Randomised (n=380)']
    ArmA [label='Arm A (n=190)']
    ArmB [label='Arm B (n=190)']
    Assessed -> Excluded; Assessed -> Randomised
    Randomised -> ArmA; Randomised -> ArmB
  }
")
```

---

## MCP Integration (Optional)

All MCP features below are **optional** — the skill works fully without them.
Use when connected MCP servers are available.

### Clinical Trials MCP

```
search_trials          — find trials by condition, phase, status
get_trial_details      — full protocol details for a specific NCT ID
analyze_endpoints      — summarise primary/secondary endpoint patterns
search_by_sponsor      — find trials by sponsor organisation
search_investigators   — look up principal investigators
search_by_eligibility  — filter trials by inclusion/exclusion criteria
```

Example: "Find Phase 3 trials for NSCLC comparing immunotherapy vs chemo"
→ `search_trials(condition="NSCLC", phase="3")` then
  `get_trial_details(nct_id="NCT...")` to pull endpoint definitions.

### bioRxiv MCP

```
search_preprints           — keyword search across bioRxiv/medRxiv
get_preprint               — fetch full preprint metadata + abstract
search_published_preprints — find preprints that became journal articles
search_by_funder           — filter by funding source
```

---

## Examples

### 1. Power calculation for a Phase 2 trial
**Prompt:** "How many patients do I need to detect an ORR improvement from 20% to 40%?"

```r
pwr.2p.test(h = ES.h(0.40, 0.20), sig.level = 0.05, power = 0.80)
```

### 2. Kaplan-Meier plot with risk table from ADTTE
**Prompt:** "Plot OS by treatment arm with risk table."

See `references/tlf-templates.md` → KM figure section.

### 3. Demographic Table 1
**Prompt:** "Create a demographics table comparing arms."

See `references/tlf-templates.md` → Table 1 section.

### 4. Meta-analysis of published HR estimates
**Prompt:** "Pool hazard ratios from 5 studies."

Use `metagen()` with `sm = "HR"` as shown above; report I², τ², forest plot.

### 5. Search for comparable trials via MCP
**Prompt:** "What Phase 3 NSCLC trials used PFS as primary endpoint?"

Use `search_trials` MCP tool, then `analyze_endpoints` on retrieved NCT IDs.
