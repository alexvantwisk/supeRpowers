# Report Content Structure (Biostatistical Consulting)

> Lazy reference. Use when drafting the *content* of a consulting report — what
> sections to include, how to handle prespecification, multiplicity, missing
> data, uncertainty, and the consultant/client boundary. For *how to render*
> docx files cleanly, see `reference-docx-anatomy.md`,
> `quarto-docx-pitfalls.md`, and `word-figure-table-patterns.md`.

This reference distills evidence-based reporting structure from ICH E9(R1),
CONSORT, STROBE, JAMA SAP guidelines, the ASA Statement on P-Values, the TIER
Protocol for reproducibility, NASEM, and consulting literature (Derr; Boen &
Zahn; Cabrera & McDougall; Chatfield).

---

## When to use this reference

- Drafting the outline of a new consulting report
- Reviewing whether an existing draft has the right sections in the right order
- Deciding what goes in the main text vs an appendix
- Wording prespecification, multiplicity, or missing-data passages
- Communicating uncertainty to non-statistical clients
- Negotiating the consultant-vs-client interpretation boundary

---

## The 12-section spine

| # | Section | Required when | Typical length |
|---|---|---|---|
| 1 | Front matter & administrative info | Always | 1 page |
| 2 | Executive summary | Always (especially industry) | 1–2 pages |
| 3 | Background, scope, research questions | Always | 1–2 pages |
| 4 | Estimand / estimation target | Causal or inferential work | 0.5–1 page |
| 5 | Data sources, provenance, integrity | Always | 1–3 pages |
| 6 | Statistical methods | Always | 2–5 pages |
| 7 | Results | Always | 2–6 pages |
| 8 | Sensitivity analyses & robustness | Whenever assumptions are non-trivial | 1–2 pages |
| 9 | Interpretation, discussion, limitations | Always | 1–3 pages |
| 10 | Recommendations & conclusions | Always | 0.5–1 page |
| 11 | Reproducibility appendix | Always | 1–3 pages |
| 12 | References & supporting appendices | As needed | Variable |

Standalone industry deliverables span ~50–300 pages (full SAR for regulatory
work). Consulting reports for academic or industry clients typically sit at a
1–2 page executive summary + 10–30 page main report + technical appendices.

---

## Industry vs academic emphasis

| Dimension | Industry standalone | Academic collaborative |
|---|---|---|
| Audience | Project managers, regulatory, exec | Domain researcher, manuscript reviewers |
| Tone | Formal, conservative, defensible | Collegial, pedagogical, collaborative |
| Admin section | Heavy (signatures, version block, QC) | Light |
| Executive summary | Mandatory; often read alone | Useful; manuscript readers skip |
| Methods detail | Sufficient for regulatory scrutiny | Sufficient for replication + reviewer defense |
| Code sharing | Constrained by IP | Encouraged; aligns with journal rules |
| Authorship / credit | Acknowledgment, not authorship | ICMJE co-authorship for substantial work |
| Iteration model | "Final" deliverable, Q&A after | Multi-round, evolves with research |

Both share: transparency about all analyses run, prespecified vs exploratory
labeling, full uncertainty quantification, honest limitations, reproducible
methods. (ASA Ethical Guidelines apply to both.)

---

## Section-by-section guidance

### 1. Front matter & administrative information

Title, version, date, consultant credentials, client identifier, version
history table (date / author / change / rationale), conflict of interest
disclosure, signatures where appropriate. Document who performed which
analyses, who decided what, and which recommendations were consultant
suggestions vs client-directed (this is the audit trail that protects you when
clients override methodological advice). (JAMA SAP §1–11; ASA Ethical
Guidelines)

### 2. Executive summary

Bottom-line findings, key effect estimates with uncertainty, main conclusions,
critical limitations, primary recommendations. Standalone; readable by
non-statisticians who may read nothing else. Lead with the most important
finding (BLUF), then significance and context. (Derr; Cabrera & McDougall)

### 3. Background, scope, research questions

Scientific motivation, specific research questions or hypotheses, engagement
objectives, scope boundaries (what is and is not covered), how this work fits
the broader research program. If initial consultation revealed the question
differed from the client's first articulation, document that here. (CONSORT,
STROBE; Chatfield's problem-formulation phase)

### 4. Estimand / estimation target

For intervention or causal questions, specify the ICH E9(R1) five attributes:

1. **Population** of interest
2. **Intervention/exposure** strategies being compared
3. **Endpoint** (variable for each participant)
4. **Population-level summary measure** (mean difference, risk ratio, hazard ratio, ...)
5. **Approach to intercurrent events** (treatment policy / composite / hypothetical / while-on-treatment / principal stratum)

For observational work, state the causal contrast of interest vs descriptive
association explicitly. For prediction modeling, follow TRIPOD: state whether
the goal is explanation or prediction and to what population predictions apply.
This section may be brief or omitted for purely descriptive analyses with no
inferential intent. (ICH E9(R1); TRIPOD)

### 5. Data sources, provenance, integrity

Source URLs/DOIs, dates obtained, who collected the data and how, data use
agreements, eligibility criteria, sampling, completeness assessment by variable
and group, quality issues identified, inclusion/exclusion decisions with
counts and reasons, final analysis sample. Include a CONSORT-style flow
diagram for trials, equivalent participant flow for observational work.
(TIER Protocol; CONSORT; STROBE; NASEM)

When data is client-provided, document who is responsible for data quality.
Per the ASA guidelines, if quality issues exist, document them honestly with
assessed impact.

### 6. Statistical methods

Sufficient detail for replication. Include:

- Methods used, with citations for non-standard approaches
- Software and version (see Reproducibility appendix)
- Assumptions and how they were assessed
- Missing-data handling — see "Missing data" critical issue below
- Multiplicity considerations — see "Multiplicity" critical issue below
- All planned analyses (primary, secondary, sensitivity, subgroup)
- **Explicit distinction between prespecified and exploratory analyses**

For mixed audiences, layer: conceptual description in main text, technical
detail in an appendix. Always document software version because
implementations differ. (JAMA SAP §17; SAMPL; ASA Statement on P-Values)

### 7. Results

Organized by research question. For every comparison report:

- Point estimate **and** confidence/credible interval (not just a p-value)
- Both relative and absolute effects for comparative work
- Exact p-values when used (not "p < 0.05")
- **Results for ALL prespecified outcomes, including null findings**
- Clear primary / secondary / exploratory labels

Tables for precise values, figures for patterns. Every table and figure must
be referenced and interpreted in text. (NEJM; JAMA; The Lancet; BMJ; ASA
Statement)

### 8. Sensitivity analyses & robustness

Results under alternative assumptions: alternative missing-data mechanisms,
alternative methods, with/without outliers, model-specification variations,
key assumption checks. State whether conclusions are robust or sensitive to
particular choices. When results prove sensitive, honest acknowledgment
strengthens credibility. (ICH E9 §5; JAMA SAP §17)

### 9. Interpretation, discussion, limitations

Findings in context of prior evidence; comparison with literature;
**statistical vs clinical/practical significance distinguished explicitly**;
biological/theoretical plausibility; limitations covering bias, precision,
generalizability, assumption violations and their likely impact. Strengths
too.

This section delineates the consultant/client boundary — see "Consultant vs
client" critical issue below. (CONSORT; STROBE; ASA Statement; Gelman on
embracing uncertainty)

### 10. Recommendations & conclusions

Clear, prioritized, actionable recommendations tied directly to findings, with
implementation feasibility considered. Suggestions for follow-up analyses or
studies if appropriate. Statistical guidance only — do not make substantive
domain decisions for the client.

Good: "A larger sample (n ≈ 240) would provide 80% power to detect a 10%
difference."
Out of scope: "You should proceed with the intervention." (ASA Ethical
Guidelines; Derr)

### 11. Reproducibility appendix

The TIER Protocol's four standards — sufficiency, soup-to-nuts, portability,
one-click reproducibility — operationalized for R:

- `sessionInfo()` output (or `sessioninfo::session_info()` for richer detail)
- `renv.lock` snapshot or pinned package list
- Operating system, R version
- Random seeds for any stochastic step
- Data dictionary (variable, type, units, missing-data code, valid range)
- Code location with persistent identifier (Zenodo DOI, OSF, GitHub release tag)
- Step-by-step reproduction README with expected outputs

Standard R chunk for the appendix:

```r
#| label: session-info
#| echo: false
sessioninfo::session_info(pkgs = "attached")
```

For stochastic methods:

```r
set.seed(20260430)  # frozen at analysis lock; document in methods
```

(TIER Protocol; NASEM; AMSTAT reproducibility initiative; JASA repro program)

### 12. References & supporting appendices

Comprehensive references for academic work; key methodological + regulatory
citations for industry. Distinguish references cited for background from
methods you actually implemented. Appendices: extended tables, complete
statistical output, derivation details, protocol amendments, sensitivity
results not in main text. Number consecutively (Appendix A, B, ...) with
descriptive titles; tables become Table A1, Figure B2, etc.

---

## Critical technical issues

### Prespecification in non-registered consulting

Most consulting projects lack formal preregistration. Best practice: write a
brief analysis-plan memo with research questions, planned analyses, and
rationale **before looking at results**, email it to the client with a date
stamp, and reference it in the methods section.

Use standardized labels in the report:

- **Prespecified** / **Protocol-specified** — locked before data examination
- **Exploratory** — additional analyses planned but not confirmatory
- **Post-hoc** / **Data-driven** — suggested by observed patterns, hypothesis-generating

The ethical issue is misrepresentation, not conducting exploratory work.
Exploratory analyses are valuable when labeled as such. (ASA Statement;
Simmons, Nelson & Simonsohn 2011; Ioannidis 2005)

### Multiplicity: the PICOTA framework

Evaluate need for adjustment along five axes:

| Axis | Adjust when |
|---|---|
| **P**opulation subgroups | Prespecified, confirmatory, biologically plausible |
| **I**ntervention comparisons | Multiple related comparisons feed one conclusion |
| **C**omparators / **O**utcomes | Multiple primary outcomes (secondary outcomes typically don't) |
| **T**imepoints | Interim analyses (use group-sequential methods) |
| **A**nalyses | Sensitivity analyses don't require adjustment — they're supportive |

State explicitly: "The following approach was taken for multiplicity: ___"
with method (Bonferroni, Holm, Hochberg, hierarchical testing, graphical
methods) and rationale, **or** state why no adjustment was performed.
Reporting unadjusted alongside adjusted p-values lets readers judge. (Li et
al.; NEJM guidance)

### Missing data: MCAR / MAR / MNAR with sensitivity

Every method makes an assumption:

| Method | Assumption | Notes |
|---|---|---|
| Complete-case | MCAR | Usually implausible in observational work |
| Multiple imputation | MAR | Untestable but often defensible |
| Likelihood-based (mixed models) | MAR | Same |
| Pattern-mixture / selection models | MNAR | Sensitivity analysis only — no unique solution |

Required reporting:

- Missing-data table by variable and group
- Mechanism assumption with justification
- Primary method with implementation detail (e.g., "Multiple imputation via
  `mice` 5.2.0, m = 20, predictive mean matching, auxiliary variables age,
  sex, baseline_score")
- Number of imputed values reported in the participant flow
- At least one sensitivity analysis examining MNAR scenarios

Avoid LOCF — it appears convenient but induces bias. (ICH E9(R1); TARMOS;
CONSORT participant flow)

### Software documentation (R-flavored)

Minimum:

```r
sessioninfo::session_info(pkgs = "attached")
# OR for tighter scope:
sessionInfo()
```

Pin via `renv::snapshot()` (creates `renv.lock`) or document key package
versions inline. Set seeds before any stochastic operation:

```r
set.seed(20260430)
boot_results <- boot::boot(data = df, statistic = my_stat, R = 1000L)
```

Archive code with a persistent identifier (Zenodo DOI, OSF). Use relative
paths (`here::here()`) so scripts run on any machine. The TIER Protocol's
"one-click reproducibility" standard requires a master script that runs the
entire pipeline. (TIER; NASEM; renv documentation)

### Communicating uncertainty to non-statisticians

Avoid jargon. Replace:

| Don't say | Say |
|---|---|
| "Statistically significant" | What the data show; effect estimate with CI |
| "Failed to reject the null" | "Found insufficient evidence that A differs from B" |
| "p < 0.05" | The exact p-value, alongside effect estimate and CI |
| "OR = 1.8 [1.2, 2.7]" (alone) | "The intervention approximately doubled the odds of success; the true effect is likely between 1.2 and 2.7 times the baseline odds" |

Use figures over tables (Cleveland's perception ranking: position on common
scale > length > angle > area). Forest plots with CIs communicate uncertainty
visually. Distinguish statistical from clinical significance every time.
(ASA Statement; Harrell; Gelman)

**Operator-aware p-value insertion in prose.** When p-values are spliced into
running text via Quarto inline ``` `r ...` ``` chunks, the comparison operator
(`=`, `≤`, `<`) must travel inside the helper, not stay loose in the prose.
Otherwise authors end up writing "p `r fmt_p(x)` or smaller" or "p
`r fmt_p(x)`" — both read awkwardly and the second is grammatically broken.
The pattern (full source in the `/r-report` template's setup chunk):

```r
# Bare value — for tables and parenthesised lists where the operator is implied
fmt_p <- function(p, d = 3) { ... }            # "0.042" or "<0.001"

# Operator + value — for running prose
fmt_p_inline <- function(p, op = "=", d = 3) { ... }
# returns "= 0.042", "≤ 0.002", or "< 0.001"
```

The critical invariant: when `p < 10^(-d)`, `fmt_p_inline()` collapses the
operator to `<`, so "p `r fmt_p_inline(p, op = "≤")`" renders as "p < 0.001"
rather than the malformed "p ≤ < 0.001". Pass `op = "≤"` when reporting the
maximum across a corrected family of tests ("all seven items had Holm-corrected
p ≤ 0.002"); pass the default `op = "="` for a single test. This keeps
prose-level p-values consistent with the ASA recommendation to report exact
values, without forcing authors to hand-write inequalities case by case.

### Consultant vs client responsibility boundary

| Consultant provides | Client provides |
|---|---|
| Statistical inference | Substantive interpretation |
| Methodology selection | Domain expertise |
| Honest reporting of limitations | Research questions |
| Clear communication of findings | Implementation decisions |
| Confidentiality | Complete data and context |

When the client overrides a methodological recommendation, document in the
report:

> "The consultant recommended [method X] based on [rationale]. The client
> requested [method Y] for [stated reason]. Results using the client's
> preferred approach are reported here; the consultant's methodological
> concerns are noted in §Limitations."

Authorship follows ICMJE: substantial contribution to design / analysis /
interpretation, drafting or critical revision, approval of final version, and
accountability — all four. (ASA Ethical Guidelines; ICMJE; Derr)

---

## Common failures and template defenses

| Failure | What goes wrong | Template defense |
|---|---|---|
| **Selective outcome reporting** | Only significant findings reported; primary outcomes switched silently | Outcomes section listing every prespecified outcome with results, even null; protocol-compliance subsection documenting any deviations with timing and rationale |
| **P-hacking / HARKing** | Multiple analyses tried; only "winners" reported; post-hoc hypotheses framed as a priori | Separate prespecified-analyses section from exploratory section; decision-log appendix recording analytic choices with dates |
| **Inadequate uncertainty** | Point estimates without CIs; p < 0.05 thresholding; binary "significant/not" framing | Result-table template forcing point estimate + CI for every effect; remove "significant"/"non-significant" language from boilerplate |
| **Opaque missing data** | Amount/pattern undocumented; assumption unstated; LOCF used silently | Mandatory missing-data subsection: amount-by-group / mechanism / justification / primary method / sensitivity analyses |
| **Multiplicity ignored or over-adjusted** | Multiple primary outcomes treated as independent; or, all comparisons Bonferroni'd including separate research questions | PICOTA checklist in methods; explicit confirmatory-vs-exploratory designation per comparison |
| **Irreproducible analyses** | Software versions undocumented; Excel-clicking; hard-coded paths; no random seeds | Reproducibility appendix checklist: sessionInfo / random seeds / data dictionary / code DOI / master script / README |

---

## Formatting conventions

**Tables vs figures.** Tables when precise numeric values matter or readers
will use the report as a reference. Figures when showing trends, patterns, or
distributions, or for non-statistical audiences. Combine: key results
graphically in main text, complete numerical tables in appendices.

**Tables.** Self-explanatory titles; column units stated; row labels left,
numbers right (or decimal-aligned); footnotes explain abbreviations and
tests; consistent decimals appropriate to measurement precision; SD or CI
alongside every point estimate; minimal lines and borders.

**Figures.** Maximize data-ink ratio (Tufte): no chartjunk, no 3D, light
gridlines. Direct labels over legends when possible. Colorblind-safe palettes
(viridis, ColorBrewer); 3–5 colors max; never rely on color alone — add
shapes or patterns. Banking line graphs to ~45° for slope perception.

**Length norms.** Industry SAR: 50–300 pages. Consulting report: 1–2 page
executive summary + 10–30 page main + appendices. Manuscript: 3,000–5,000
words main text, 6–8 tables/figures.

**Versioning.** File names like `Statistical_Report_v2.1_2026-04-30.docx` —
never `final_final.docx`. Version-history table inside the document. Git for
code with meaningful commit messages and tags matching report versions.
Time-stamp analysis plans before data examination.

(Tufte; Cleveland; Wickham/ggplot2; Gelman on document structure)

---

## Pre-submission checklist

- [ ] Version, date, and version-history table on the title page
- [ ] Executive summary readable standalone by a non-statistician
- [ ] Estimand or estimation target stated explicitly
- [ ] All prespecified outcomes reported (including nulls)
- [ ] Prespecified vs exploratory analyses clearly labeled
- [ ] Multiplicity approach stated (PICOTA), with rationale
- [ ] Missing-data mechanism stated; primary method + ≥1 sensitivity analysis
- [ ] Every effect reports point estimate + CI, not just p-value
- [ ] Statistical vs clinical/practical significance distinguished
- [ ] Limitations cover bias, precision, generalizability
- [ ] Recommendations are actionable and within consultant scope
- [ ] `sessionInfo()` and seeds in the reproducibility appendix
- [ ] `renv.lock` or equivalent pinning included or referenced
- [ ] Code archived with a persistent identifier
- [ ] Data dictionary in the appendix
- [ ] All tables and figures referenced and interpreted in text

---

## Forward links

A future editorial-template skill (CONSORT/STROBE/TRIPOD-aware Quarto
scaffolds with section-by-section prompt text) is on the deferred-scope list
in `docs/superpowers/specs/2026-04-30-r-reporting-design.md`. This reference
is the precursor: it defines *what goes in*; that skill would generate *the
literal text scaffold*.

---

## Sources

- ICH E9(R1) — *Statistical Principles for Clinical Trials: Addendum on Estimands and Sensitivity Analyses*
- CONSORT 2010 — *Reporting parallel-group randomised trials*
- STROBE — *Reporting observational studies in epidemiology*
- TRIPOD — *Reporting prediction model studies*
- JAMA SAP guidelines — *Statistical Analysis Plan content (17 items)*
- SAMPL — *Statistical Analyses and Methods in the Published Literature*
- ASA Statement on P-Values (Wasserstein & Lazar, 2016) and "Moving to a World Beyond p < 0.05" (2019)
- ASA Ethical Guidelines for Statistical Practice
- TIER Protocol — Project TIER reproducibility standards
- NASEM — *Reproducibility and Replicability in Science* (2019)
- Simmons, Nelson & Simonsohn (2011) — *False-Positive Psychology*
- Ioannidis (2005) — *Why Most Published Research Findings Are False*
- ICMJE — Authorship criteria
- Tufte — *The Visual Display of Quantitative Information*
- Cleveland — *Visualizing Data*
- Derr — *Statistical Consulting: A Guide to Effective Communication*
- Boen & Zahn — *The Human Side of Statistical Consulting*
