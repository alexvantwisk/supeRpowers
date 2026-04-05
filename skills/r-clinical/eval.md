# Eval: r-clinical

> Development-only. Not loaded by the plugin.

## Binary Eval Questions

1. When asked to perform a general survival analysis on non-clinical data (e.g., customer churn time-to-event), does the skill defer to r-stats rather than applying clinical trial methodology?
2. When generating a Kaplan-Meier analysis, does the skill check the proportional hazards assumption before fitting a Cox model?
3. When coding censoring flags, does the skill produce correct CDISC-compliant CNSR/CNSRFLG values (0 = event, 1 = censored) rather than the common inversion?
4. When asked for a basic summary table of means and counts with no regulatory context, does the skill defer to r-tables?
5. When handling competing risks in a trial endpoint analysis, does the skill use Fine-Gray or cause-specific hazard approaches rather than naive Kaplan-Meier?
6. When asked to predict biomarker response using a machine learning model, does the skill defer to r-tidymodels for the modeling portion?
7. Does all generated code use `|>` and `<-` exclusively (no `%>%` or `=` for assignment)?

## Test Prompts

### Happy Path

- "Create a Kaplan-Meier survival curve for progression-free survival in an ADaM ADTTE dataset, with treatment arm stratification and a risk table below the plot."
- "Generate a demographics Table 1 for an FDA submission using the ADSL dataset, including age, sex, race, and BMI by treatment arm, with p-values and proper formatting."

### Edge Cases

- "My trial has a composite endpoint where patients can experience progression, death, or withdrawal. How do I handle competing risks properly in the ADTTE derivation?"
- "We're running an adaptive platform trial with interim analyses. How do I set up the analysis datasets to handle patients who cross treatment arms after an interim look?"
- "Validate that my ADaM ADAE dataset conforms to CDISC standards. Check variable names, controlled terminology, and required columns."

### Adversarial Cases

- "Fit a Cox proportional hazards model to predict time until customer churn from a SaaS dataset with columns tenure_days, churned, plan_type." (boundary: non-clinical survival analysis should defer to r-stats)
- "Make a simple summary table showing mean and SD of lab values grouped by visit. No regulatory requirements." (boundary: non-regulatory table should defer to r-tables)
- "Run a t-test comparing hemoglobin levels between two groups in my lab dataset. There's no trial context, just observational data." (boundary: general statistical test should defer to r-stats)

### Boundary Tests

- "Fit a survival model on website session duration data." boundary -> r-stats
- "Create a GT table of summary statistics for a class project." boundary -> r-tables
- "Build a predictive model for treatment response using baseline biomarkers and clinical features." boundary -> r-tidymodels

## Success Criteria

- Happy path KM response MUST use the `survival` and/or `ggsurvfit` packages and MUST include a risk table.
- Happy path demographics table MUST use a regulatory-aware package (e.g., `gtsummary`, `Tplyr`, `rtables`) and produce output suitable for a CSR appendix.
- Competing risks response MUST NOT use naive `survfit()` without addressing the competing event; it MUST reference Fine-Gray (`tidycmprsk`, `cmprsk`) or cause-specific hazard modeling.
- CDISC validation response MUST check for required ADaM variables (STUDYID, USUBJID, PARAMCD, AVAL, etc.) and controlled terminology compliance.
- Censoring code MUST use CNSR = 0 for event and CNSR = 1 for censored (CDISC convention); the response must NOT invert this coding.
- Cox model output MUST include or recommend a proportional hazards diagnostic (e.g., `cox.zph()`, Schoenfeld residuals); it must NOT present Cox results without any assumption check.
- Non-clinical survival prompt MUST be deferred to r-stats; response must NOT apply CDISC or trial-specific methodology.
- Non-regulatory table prompt MUST be deferred to r-tables; response must NOT invoke clinical table packages unnecessarily.
- Response must NOT use `%>%`, `=` for assignment, or single quotes for strings.
