
# Assignment 1
# Data Provenance and Measurement Validity Assessment of Published Geothermobarometric Datasets

## 1. Introduction

This report documents the provenance assessment, structural validation,
measurement-quality evaluation, and reproducibility checks performed on
four supplementary geothermobarometric datasets (S1-S4) associated with
the published study Rabbani & Wu (2026).

The objective of this assessment was to establish a transparent and
reproducible foundation before applying statistical modelling or machine
learning approaches. The analysis focused on identifying data structure
issues, separating analytical observations from non-analytical records,
evaluating missingness and duplication, checking mineral-chemical
plausibility, and preventing target leakage.

---

## 2. Dataset Overview

Four supplementary datasets were evaluated.

| Dataset | Description | Observations retained |
|---|---|---:|
| S1 | Experimental garnet-hornblende dataset | 39 |
| S2 | Experimental hornblende-plagioclase dataset | 90 |
| S3 | Natural-rock GASP-GBPQ comparison dataset | 2084 |
| S4 | Natural-rock multi-thermobarometer dataset | 88 |

All datasets were preserved in their original provenance context.
Raw files were retained separately from processed analytical products.

---

## 3. Data Provenance Assessment

### S1

S1 contained 39 experimental observations with complete analytical
fields. No missing required fields, duplicate identifiers, or exact
duplicate analytical rows were detected.

### S2

The original structured S2 file contained 113 rows. Provenance auditing
identified:

- 90 experimental observations
- 23 appended reference/bibliographic rows

The 23 reference rows were separated from the analytical dataset while
being preserved independently.

The final analytical S2 dataset contains 90 experimental runs with
complete pressure-temperature information.

### S3

S3 contains 2084 published natural-rock observations.

Repeated Source + Sample identifiers were retained because they may
represent independent analytical measurements.

Eight exact duplicate rows were detected. A sensitivity dataset was
generated after removing four redundant exact copies, resulting in
2080 observations.

The primary published dataset was not altered.

### S4

S4 contains 88 natural-rock samples.

Hierarchical Excel header reconstruction was performed to preserve
original column provenance. The audit confirmed that iterative
thermobarometric outputs terminate before the raw mineral chemistry
blocks.

Raw chemistry variables were therefore separated correctly from
calculated thermobarometric outputs.

---

## 4. Missingness and Duplicate Analysis

### Missingness

No completely missing columns were detected in S1-S4.

Observed missingness reflected dataset design:

- S2: incomplete plagioclase oxide analyses in 25 samples
- S3: missing opaque mineral information in some observations
- S4: partial availability of oxide datasets

Missing values were retained as provenance information rather than
artificially imputed.

### Duplicate assessment

No problematic duplicate analytical rows were detected in S1, S2, or S4.

S3 duplicate handling was explicitly documented through a primary
published dataset and a deduplicated sensitivity dataset.

---

## 5. Mineral Chemistry Integrity Assessment

Chemical plausibility checks were performed on mineral chemistry data.

### S1

Results:

- Negative garnet cations: 0
- Negative hornblende cations: 0
- Non-numeric entries: 0

Cation sums were consistent with expected mineral structural ranges.

### S2

Results:

- Negative oxide values: 0
- Non-numeric oxide entries: 0

Complete analyses were distinguished from incomplete plagioclase oxide
records.

### S3

Results:

- Biotite negative values: 0
- Plagioclase negative values: 0
- Garnet negative values: 0

All chemistry fields were numeric.

### S4

Results:

- Negative mineral chemistry values: 0
- Non-numeric chemistry entries: 0

Raw mineral chemistry groups were successfully separated into:

- biotite cations
- plagioclase cations
- garnet cations
- hornblende cations
- plagioclase oxides
- hornblende oxides

---

## 6. Thermobarometer Reproducibility Assessment

### S3 GASP-GBPQ Agreement

The GASP-GBPQ comparison was independently reproduced.

Using full precision values:

- 2028 / 2084 observations were within ±1 kbar
- Agreement = 97.31%

A rounding sensitivity analysis demonstrated that the manuscript-level
agreement depends on numerical precision.

Using GBPQ values rounded to two decimal places reproduced:

- 2027 / 2084 observations within ±1 kbar

This confirms that the reported agreement is reproducible and that the
difference is due to rounding convention rather than data manipulation.

---

## 7. Thermobarometer Inventory Validation

The corrected thermobarometer inventory contains:

- 8 geobarometers
- 12 geothermometers
- 20 total methods

Calibration-domain classification identified:

- 14 methods with explicit pressure-temperature ranges
- 5 methods with unspecified ranges
- 1 method with mixed/unclear metadata

Unspecified calibration ranges were not inferred.

---

## 8. Machine Learning Readiness and Leakage Prevention

A predictor-role audit was performed before modelling.

The following categories were excluded as predictors:

- experimental/reference target values
- calculated thermobarometer outputs
- model-derived benchmark values

The final leakage audit confirmed:

- prohibited predictor variables: 0 remaining unresolved cases
- manual role review variables: 0

This ensures that future modelling will evaluate genuine predictive
relationships rather than reproduce already calculated thermobarometric
outputs.

---

## 9. Data Redistribution and Reproducibility

The repository preserves:

- raw supplementary datasets
- processed analytical datasets
- audit outputs
- metadata
- scripts
- reproducibility documentation

The repository avoids redistribution of publisher-formatted article
files while preserving citation and DOI information.

---

## 10. Conclusions

The provenance and validity assessment demonstrates that the S1-S4
datasets are suitable for subsequent computational analysis.

Key outcomes:

1. Analytical observations were separated from non-analytical records.
2. Dataset structure and provenance were preserved.
3. Duplicate handling decisions were documented.
4. Mineral chemistry integrity was verified.
5. Thermobarometric calculations were independently reproduced.
6. Data leakage risks were eliminated before modelling.

The resulting repository provides a reproducible foundation for
subsequent statistical and machine-learning investigations of
geothermobarometric relationships.
