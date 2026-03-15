# CDISC ADaM & SDTM Guide

Reference for CDISC-compliant dataset structure in R clinical trial analysis.
Use the `admiral`, `metacore`, and `metatools` packages for ADaM creation.

---

## ADaM Dataset Types

| Dataset | Full Name | Purpose |
|---------|-----------|---------|
| **ADSL** | Subject-Level Analysis Dataset | One row per subject. Demographics, treatment assignment, flags. |
| **ADAE** | Adverse Events Analysis Dataset | One row per adverse event. |
| **ADTTE** | Time-to-Event Analysis Dataset | One row per parameter per subject (OS, PFS, DFS). |
| **ADLB** | Laboratory Analysis Dataset | One row per lab test per visit per subject. |
| **ADRS** | Response Analysis Dataset | Tumour response records (CR, PR, SD, PD). |
| **ADEFF** | Efficacy Analysis Dataset | Efficacy endpoints not covered by ADTTE/ADRS. |
| **ADCM** | Concomitant Medications Dataset | One row per concomitant medication record. |
| **ADVS** | Vital Signs Analysis Dataset | One row per vital sign per visit per subject. |

---

## ADaM Variable Naming Conventions

### Universal Variables (all datasets)

| Variable | Type | Description |
|----------|------|-------------|
| `STUDYID` | Char | Study identifier |
| `USUBJID` | Char | Unique subject identifier (STUDYID + SITEID + SUBJID) |
| `SUBJID` | Char | Subject identifier within study |
| `SITEID` | Char | Study site identifier |

### ADSL Key Variables

| Variable | Type | Description |
|----------|------|-------------|
| `TRT01P` | Char | Planned treatment for Period 1 |
| `TRT01A` | Char | Actual treatment for Period 1 |
| `TRT01PN` | Num | Numeric code for `TRT01P` |
| `TRT01AN` | Num | Numeric code for `TRT01A` |
| `RANDFL` | Char | Randomised flag (Y/N) |
| `ITTFL` | Char | Intent-to-treat flag (Y/N) |
| `SAFFL` | Char | Safety population flag (Y/N) |
| `PPROTFL` | Char | Per-protocol flag (Y/N) |
| `TRTSDT` | Num (date) | Date of first exposure to treatment |
| `TRTEDT` | Num (date) | Date of last exposure to treatment |
| `AGE` | Num | Age at randomisation |
| `AGEGR1` | Char | Age group (e.g., "<65", ">=65") |
| `SEX` | Char | Sex (M/F) |
| `RACE` | Char | Race |
| `COUNTRY` | Char | Country |

### BDS (Basic Data Structure) Variables — ADLB, ADVS, ADEFF

| Variable | Type | Description |
|----------|------|-------------|
| `PARAM` | Char | Parameter description (e.g., "Haemoglobin (g/dL)") |
| `PARAMCD` | Char | Parameter code (e.g., "HGB") — max 8 chars, uppercase |
| `PARAMN` | Num | Parameter numeric code |
| `AVAL` | Num | Analysis value |
| `AVALC` | Char | Analysis value (character) — use when AVAL not applicable |
| `BASE` | Num | Baseline value |
| `CHG` | Num | Change from baseline (`AVAL - BASE`) |
| `PCHG` | Num | Percent change from baseline (`100 * CHG / BASE`) |
| `ABLFL` | Char | Baseline record flag (Y = baseline record) |
| `ANL01FL` | Char | Analysis flag 01 (Y = used in primary analysis) |
| `DTYPE` | Char | Derivation type (e.g., "LOCF", "WOCF") |
| `ADT` | Num (date) | Analysis date |
| `ADY` | Num | Analysis day relative to first dose (`ADT - TRTSDT + 1`) |
| `AVISIT` | Char | Analysis visit description |
| `AVISITN` | Num | Analysis visit number |

### ADTTE Key Variables

| Variable | Type | Description |
|----------|------|-------------|
| `PARAM` | Char | Time-to-event parameter (e.g., "Overall Survival") |
| `PARAMCD` | Char | Parameter code (e.g., "OS", "PFS", "DFS") |
| `AVAL` | Num | Analysis value (time in days or months) |
| `AVALU` | Char | Units of AVAL (e.g., "DAYS", "MONTHS") |
| `CNSR` | Num | Censoring indicator: `0` = event, `1` = censored |
| `EVNTDESC` | Char | Event description |
| `SRCDOM` | Char | Source domain for event |
| `SRCVAR` | Char | Source variable for event |

### ADAE Key Variables

| Variable | Type | Description |
|----------|------|-------------|
| `AEBODSYS` | Char | MedDRA System Organ Class |
| `AEDECOD` | Char | MedDRA Preferred Term |
| `AETERM` | Char | Reported term |
| `AESEV` | Char | Severity (MILD/MODERATE/SEVERE) |
| `AESEVN` | Num | Severity numeric |
| `AESER` | Char | Serious AE flag (Y/N) |
| `AEREL` | Char | Relationship to study drug |
| `AESTDTC` | Char | Start date (ISO 8601) |
| `ASTDT` | Num | Analysis start date |
| `TRTEMFL` | Char | Treatment-emergent flag (Y/N) |
| `ATOXGR` | Char | NCI-CTCAE grade at observation |
| `BTOXGR` | Char | Baseline NCI-CTCAE grade |

---

## SDTM Domains Overview

| Domain | Description | Key Variables |
|--------|-------------|---------------|
| **DM** | Demographics | USUBJID, AGE, SEX, RACE, COUNTRY, RFSTDTC, ARM |
| **AE** | Adverse Events | AETERM, AEDECOD, AEBODSYS, AESEV, AESER, AESTDTC, AEENDTC |
| **LB** | Laboratory Test Results | LBTEST, LBTESTCD, LBORRES, LBSTRESU, VISITNUM, LBDTC |
| **VS** | Vital Signs | VSTESTCD, VSORRES, VSSTRESU, VISITNUM, VSDTC |
| **EX** | Exposure | EXTRT, EXDOSE, EXDOSU, EXROUTE, EXSTDTC, EXENDTC |
| **CM** | Concomitant Medications | CMTRT, CMINDC, CMSTDTC, CMENDTC |
| **MH** | Medical History | MHTERM, MHSTDTC |
| **DS** | Disposition | DSSCAT, DSTERM, DSSTDTC |
| **RS** | Disease Response | RSTEST, RSSTRESC, VISITNUM |
| **TU** | Tumor/Lesion Identification | TULOC, TUMETHOD |
| **TR** | Tumor/Lesion Results | TRTESTCD, TRORRES, VISITNUM |

SDTM variables follow the pattern: two-letter domain prefix + standardised
suffix (e.g., `LBTEST` = lab domain + TEST variable).

---

## R Packages for CDISC

### admiral

`admiral` is the primary package for constructing ADaM datasets from SDTM.

```r
library(admiral)

# Derive ADSL from DM + treatment exposure
adsl <- dm |>
  select(STUDYID, USUBJID, SUBJID, SITEID, AGE, SEX, RACE, COUNTRY) |>
  derive_vars_dt(
    new_vars_prefix = "TRTS",
    dtc = RFSTDTC
  ) |>
  derive_vars_merged(
    dataset_add = ex,
    new_vars = exprs(TRTEDT = EXENDTC),
    by_vars = exprs(STUDYID, USUBJID),
    order = exprs(EXENDTC),
    mode = "last"
  )

# Derive ADTTE for Overall Survival from ADSL + DS
adtte_os <- adsl |>
  derive_param_tte(
    dataset_events = derive_vars_dt(ds, new_vars_prefix = "ADT", dtc = DSSTDTC),
    event_conditions = list(event_source("DS", DSTERM == "DEATH")),
    censor_conditions = list(censor_source("ADSL", DTHFL != "Y")),
    source_datasets = list(ADSL = adsl, DS = ds),
    set_values_to = exprs(PARAMCD = "OS", PARAM = "Overall Survival",
                          AVALU = "DAYS")
  )
```

### metacore & metatools

`metacore` stores metadata (specs) and validates datasets against them.
`metatools` provides helper functions to apply metadata to datasets.

```r
library(metacore)
library(metatools)

# Load specs from Excel spec file
spec <- spec_to_metacore("path/to/specs.xlsx", where_sep_sheet = FALSE)

# Check dataset against spec
check_variables(adsl, spec)    # Flags missing or extra variables
check_type(adsl, spec)         # Flags type mismatches
check_ct_data(adsl, spec)      # Validates controlled terminology values
```

### xportr

Export SAS-compatible XPT files for regulatory submission.

```r
library(xportr)

adsl |>
  xportr_type(spec, domain = "ADSL") |>
  xportr_length(spec, domain = "ADSL") |>
  xportr_label(spec, domain = "ADSL") |>
  xportr_write("path/to/adsl.xpt")
```

---

## Traceability Requirements

Every derived variable must be traceable from source SDTM through ADaM to
the TLF output. Documentation requirements:

1. **Analysis Data Reviewer's Guide (ADRG):** Describes ADaM datasets, key
   derivations, and how to reproduce analyses. Required for NDA/BLA submissions.

2. **Annotated CRF:** Maps CRF fields to SDTM variables.

3. **Variable-level traceability:** For each AVAL derivation, document:
   - Source domain and variable (`SRCDOM`, `SRCVAR` in ADTTE)
   - Derivation algorithm
   - Analysis flag logic (`ANL01FL`)

4. **Population flags:** Always trace `ITTFL`, `SAFFL`, `PPROTFL` back to
   protocol criteria with code comments.

```r
# Example: trace TRTEMFL derivation in ADAE
adae <- adae |>
  mutate(
    # Treatment-emergent: AE onset on or after first dose and
    # on or before last dose + 30 days (per protocol Section 8.2)
    TRTEMFL = dplyr::if_else(
      ASTDT >= adsl_trtsdt & ASTDT <= adsl_trtedt + 30,
      "Y", NA_character_
    )
  )
```

5. **Controlled Terminology:** Use CDISC CT published on
   [NCI EVS](https://evs.nci.nih.gov/ftp1/CDISC/). Never create ad-hoc codes
   for variables that have a CT codelist (e.g., SEX, RACE, AESEV).
