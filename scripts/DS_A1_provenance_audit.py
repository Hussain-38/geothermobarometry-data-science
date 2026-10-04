# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 14:43:51 2026

@author: hussa
"""

# %% ============================================================
# DS-A1 | DATA PROVENANCE AND MEASUREMENT AUDIT
# Geothermobarometry Data Science Project
# ================================================================
#
# Project objective:
# Audit the provenance, structure, measurement integrity, ranges,
# missingness, duplicates, anomalies, and leakage risks of the
# experimental and natural-rock geothermobarometry datasets.
#
# IMPORTANT:
# - Raw files are never modified.
# - All outputs are written to results/, figures/, metadata/, etc.
# - This script is designed for Spyder and can be run cell-by-cell.
# ================================================================


# %% ============================================================
# 1. IMPORT LIBRARIES
# ================================================================

from pathlib import Path
import hashlib
import json
import platform
import sys
import re
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("default")

SEED = 42
np.random.seed(SEED)

print("Python:", sys.version)
print("Platform:", platform.platform())
print("NumPy:", np.__version__)
print("Pandas:", pd.__version__)
print("Random seed:", SEED)


# %% ============================================================
# 2. DEFINE PROJECT DIRECTORIES
# ================================================================

PROJECT_DIR = Path(r"D:\Data Science Assignment")

RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
SCRIPTS_DIR = PROJECT_DIR / "scripts"
RESULTS_DIR = PROJECT_DIR / "results"
FIGURES_DIR = PROJECT_DIR / "figures"
METADATA_DIR = PROJECT_DIR / "metadata"
REPORTS_DIR = PROJECT_DIR / "reports"

for directory in [
    RAW_DIR,
    PROCESSED_DIR,
    SCRIPTS_DIR,
    RESULTS_DIR,
    FIGURES_DIR,
    METADATA_DIR,
    REPORTS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)

print("\nProject directory:")
print(PROJECT_DIR)

print("\nRaw data directory:")
print(RAW_DIR)


# %% ============================================================
# 3. DEFINE INPUT FILES
# ================================================================

FILES = {
    "S1": RAW_DIR / "1-s2.0-S1367912026001495-mmc1.xls",
    "S2": RAW_DIR / "1-s2.0-S1367912026001495-mmc2.xls",
    "S3": RAW_DIR / "1-s2.0-S1367912026001495-mmc3.xls",
    "S4": RAW_DIR / "1-s2.0-S1367912026001495-mmc4.xls",
    "inventory": RAW_DIR / "Geobarometers and geothermometers need to be investigated.xlsx"
}

print("\nFILE CHECK")
print("=" * 80)

all_files_found = True

for name, path in FILES.items():

    exists = path.exists()

    print(
        f"{name:12s}",
        "FOUND" if exists else "MISSING",
        "->",
        path
    )

    if not exists:
        all_files_found = False

if not all_files_found:

    raise FileNotFoundError(
        "\nOne or more required input files are missing.\n"
        "Check the filenames inside:\n"
        f"{RAW_DIR}"
    )


# %% ============================================================
# 4. CALCULATE SHA-256 HASHES
# ================================================================

def calculate_sha256(file_path):

    sha = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            block = file.read(1024 * 1024)

            if not block:
                break

            sha.update(block)

    return sha.hexdigest()


manifest_rows = []

for dataset_name, file_path in FILES.items():

    stat = file_path.stat()

    manifest_rows.append(
        {
            "dataset": dataset_name,
            "file_name": file_path.name,
            "file_size_bytes": stat.st_size,
            "sha256": calculate_sha256(file_path),
            "audit_date": datetime.now().isoformat(
                timespec="seconds"
            )
        }
    )

manifest = pd.DataFrame(manifest_rows)

print("\nDATASET MANIFEST")
print("=" * 80)
print(manifest.to_string(index=False))

manifest.to_csv(
    METADATA_DIR / "data_manifest_sha256.csv",
    index=False
)


# %% ============================================================
# 5. SAVE SOFTWARE ENVIRONMENT INFORMATION
# ================================================================

environment = {
    "python": sys.version,
    "platform": platform.platform(),
    "numpy": np.__version__,
    "pandas": pd.__version__,
    "random_seed": SEED,
    "audit_time": datetime.now().isoformat(
        timespec="seconds"
    )
}

with open(
    METADATA_DIR / "environment.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        environment,
        file,
        indent=4
    )

print("\nEnvironment information saved.")


# %% ============================================================
# 6. READ GEOTHERMOBAROMETER INVENTORY
# ================================================================

inventory_raw = pd.read_excel(
    FILES["inventory"],
    header=None,
    engine="openpyxl"
)

print("\nRAW GEOTHERMOBAROMETER INVENTORY")
print("=" * 80)
print(inventory_raw.to_string())

inventory_raw.to_csv(
    RESULTS_DIR / "inventory_raw_snapshot.csv",
    index=False,
    header=False
)


# %% ============================================================
# 7. EXTRACT MODEL INVENTORY SECTIONS
# ================================================================

# The uploaded workbook contains separate geobarometer
# and geothermometer sections.
#
# We preserve the original content first and only perform
# minimal cleaning.

barometers = inventory_raw.iloc[
    1:10,
    0:5
].copy()

barometers.columns = [
    "name",
    "symbol",
    "source",
    "calibration_method",
    "pt_range"
]

thermometers = inventory_raw.iloc[
    14:27,
    0:5
].copy()

thermometers.columns = [
    "name",
    "symbol",
    "source",
    "calibration_method",
    "pt_range"
]

barometers["model_type"] = "geobarometer"
thermometers["model_type"] = "geothermometer"

model_inventory = pd.concat(
    [
        barometers,
        thermometers
    ],
    ignore_index=True
)

print("\nEXTRACTED MODEL INVENTORY")
print("=" * 80)
print(model_inventory.to_string(index=False))


# %% ============================================================
# 8. PRESERVE RAW METADATA VALUES
# ================================================================

for column in [
    "name",
    "symbol",
    "source",
    "calibration_method",
    "pt_range"
]:

    model_inventory[
        column + "_raw"
    ] = model_inventory[column]


# %% ============================================================
# 9. MINIMAL TEXT NORMALIZATION
# ================================================================

def normalize_text(value):

    if pd.isna(value):
        return np.nan

    value = str(value)

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


text_columns = [
    "name",
    "symbol",
    "source",
    "calibration_method",
    "pt_range"
]

for column in text_columns:

    model_inventory[column] = (
        model_inventory[column]
        .apply(normalize_text)
    )


# %% ============================================================
# 10. STANDARDIZE CALIBRATION METHOD LABELS
# ================================================================

def standardize_calibration(value):

    if pd.isna(value):
        return np.nan

    value_lower = str(value).lower()

    if "empir" in value_lower:
        return "Empirical"

    if "experiment" in value_lower:
        return "Experimental"

    if "mix" in value_lower:
        return "Mixed"

    return "Unclassified"


model_inventory[
    "calibration_method_standardized"
] = (
    model_inventory[
        "calibration_method"
    ]
    .apply(
        standardize_calibration
    )
)


# %% ============================================================
# 11. INVENTORY METADATA QUALITY FLAGS
# ================================================================

model_inventory[
    "flag_missing_symbol"
] = model_inventory[
    "symbol"
].isna()

model_inventory[
    "flag_missing_source"
] = model_inventory[
    "source"
].isna()

model_inventory[
    "flag_unclassified_calibration"
] = (
    model_inventory[
        "calibration_method_standardized"
    ]
    == "Unclassified"
)

model_inventory[
    "flag_unspecified_range"
] = (
    model_inventory[
        "pt_range"
    ]
    .astype(str)
    .str.lower()
    .str.contains(
        "unspecified",
        na=False
    )
)


# %% ============================================================
# 12. CLASSIFY P-T RANGE FIELD
# ================================================================

def classify_pt_range(value):

    if pd.isna(value):
        return "missing"

    text = str(value).lower()

    if "unspecified" in text:
        return "unspecified"

    has_number = bool(
        re.search(
            r"\d",
            text
        )
    )

    has_unit = (
        ("kbar" in text)
        or
        ("ºc" in text)
        or
        ("°c" in text)
        or
        ("c" in text)
    )

    if has_number and has_unit:
        return "structured_range"

    return "review_required"


model_inventory[
    "pt_range_status"
] = (
    model_inventory[
        "pt_range"
    ]
    .apply(
        classify_pt_range
    )
)

print("\nP-T RANGE AUDIT")
print("=" * 80)

print(
    model_inventory[
        [
            "symbol",
            "pt_range",
            "pt_range_status"
        ]
    ]
    .to_string(index=False)
)


# %% ============================================================
# 13. CHECK MODEL SYMBOL DUPLICATES
# ================================================================

model_inventory[
    "flag_duplicate_symbol"
] = (
    model_inventory[
        "symbol"
    ]
    .duplicated(
        keep=False
    )
)

print("\nDUPLICATE SYMBOL CHECK")
print("=" * 80)

print(
    model_inventory[
        [
            "symbol",
            "model_type",
            "flag_duplicate_symbol"
        ]
    ]
    .to_string(index=False)
)


# %% ============================================================
# 14. EXPORT MODEL INVENTORY AUDIT
# ================================================================

model_inventory.to_csv(
    RESULTS_DIR /
    "geothermobarometer_inventory_audit.csv",
    index=False
)

print(
    "\nSaved:",
    RESULTS_DIR /
    "geothermobarometer_inventory_audit.csv"
)


# %% ============================================================
# 15. LOAD ALL FOUR SCIENTIFIC TABLES AS RAW DATA
# ================================================================

raw_tables = {}

for dataset_name in [
    "S1",
    "S2",
    "S3",
    "S4"
]:

    raw_tables[
        dataset_name
    ] = pd.read_excel(
        FILES[dataset_name],
        header=None,
        engine="xlrd"
    )

    print("\n")
    print("=" * 80)
    print(dataset_name)
    print("=" * 80)

    print(
        "Raw shape:",
        raw_tables[
            dataset_name
        ].shape
    )

    print(
        raw_tables[
            dataset_name
        ]
        .head(15)
        .to_string()
    )


# %% ============================================================
# 16. AUTOMATIC LIKELY HEADER-ROW DETECTION
# ================================================================

HEADER_TERMS = [
    "reference",
    "source",
    "run",
    "sample",
    "rock",
    "pressure",
    "temperature",
    "exp",
    "sio2",
    "tio2",
    "al2o3",
    "feo",
    "mgo",
    "cao",
    "na2o",
    "k2o",
    "fe",
    "mg",
    "ca",
    "al"
]


def header_score(row):

    score = 0

    for value in row:

        if pd.isna(value):
            continue

        text = str(value).lower()

        for term in HEADER_TERMS:

            if term in text:
                score += 1

    return score


header_candidates = []

for dataset_name, df in raw_tables.items():

    scores = df.apply(
        header_score,
        axis=1
    )

    candidate = int(
        scores.idxmax()
    )

    score_value = int(
        scores.loc[candidate]
    )

    header_candidates.append(
        {
            "dataset":
                dataset_name,

            "candidate_header_row_zero_based":
                candidate,

            "candidate_header_row_excel_based":
                candidate + 1,

            "header_score":
                score_value
        }
    )

    print("\n")
    print("=" * 80)
    print(
        dataset_name,
        "LIKELY HEADER ROW"
    )
    print("=" * 80)

    print(
        "Python row index:",
        candidate
    )

    print(
        "Excel-style row number:",
        candidate + 1
    )

    print(
        "Header score:",
        score_value
    )

    print("\nRows around candidate:")

    print(
        df.iloc[
            max(0, candidate - 2):
            candidate + 3
        ]
        .to_string()
    )


header_candidates_df = pd.DataFrame(
    header_candidates
)

header_candidates_df.to_csv(
    RESULTS_DIR /
    "candidate_header_rows.csv",
    index=False
)


# %% ============================================================
# 17. RAW STRUCTURAL AUDIT
# ================================================================

structural_summary = []

for dataset_name, df in raw_tables.items():

    structural_summary.append(
        {
            "dataset":
                dataset_name,

            "rows_raw":
                df.shape[0],

            "columns_raw":
                df.shape[1],

            "completely_empty_rows":
                int(
                    df.isna()
                    .all(axis=1)
                    .sum()
                ),

            "completely_empty_columns":
                int(
                    df.isna()
                    .all(axis=0)
                    .sum()
                ),

            "exact_duplicate_rows":
                int(
                    df.duplicated()
                    .sum()
                ),

            "total_missing_cells":
                int(
                    df.isna()
                    .sum()
                    .sum()
                )
        }
    )


structural_summary = pd.DataFrame(
    structural_summary
)

print("\nRAW STRUCTURAL AUDIT")
print("=" * 80)

print(
    structural_summary
    .to_string(index=False)
)

structural_summary.to_csv(
    RESULTS_DIR /
    "raw_structural_audit.csv",
    index=False
)


# %% ============================================================
# 18. PUBLISHED EXPECTED SAMPLE COUNTS
# ================================================================

published_expectations = pd.DataFrame(
    {
        "dataset": [
            "S1",
            "S2",
            "S3",
            "S4"
        ],

        "expected_n": [
            39,
            90,
            2084,
            88
        ],

        "scientific_role": [
            "GH experimental precision evaluation",
            "PH/Hbl experimental precision evaluation",
            "Natural metapelite GASP-GBPQ consistency evaluation",
            "Natural-rock thermobarometer accuracy/applicability evaluation"
        ]
    }
)

print("\nPUBLISHED DATASET EXPECTATIONS")
print("=" * 80)

print(
    published_expectations
    .to_string(index=False)
)

published_expectations.to_csv(
    METADATA_DIR /
    "published_dataset_expectations.csv",
    index=False
)


# %% ============================================================
# 19. PUBLISHED EXPERIMENTAL P-T DOMAINS
# ================================================================

published_domains = pd.DataFrame(
    {
        "dataset": [
            "S1",
            "S2"
        ],

        "P_min_kbar": [
            8,
            1
        ],

        "P_max_kbar": [
            15,
            15
        ],

        "T_min_C": [
            700,
            650
        ],

        "T_max_C": [
            1025,
            1050
        ]
    }
)

print("\nPUBLISHED EXPERIMENTAL DOMAINS")
print("=" * 80)

print(
    published_domains
    .to_string(index=False)
)

published_domains.to_csv(
    METADATA_DIR /
    "published_PT_domains.csv",
    index=False
)


# %% ============================================================
# 20. GENERIC COLUMN-NAME CLEANING FUNCTION
# ================================================================

def clean_column_name(name):

    if pd.isna(name):
        return "unnamed"

    name = str(name).strip()

    name = re.sub(
        r"\s+",
        "_",
        name
    )

    name = name.replace(
        "/",
        "_"
    )

    name = name.replace(
        "(",
        ""
    )

    name = name.replace(
        ")",
        ""
    )

    name = name.replace(
        "%",
        "pct"
    )

    name = name.replace(
        "°",
        ""
    )

    return name


# %% ============================================================
# 21. GENERIC SCHEMA AUDIT FUNCTION
# ================================================================

def schema_audit(
    df,
    dataset_name
):

    output = []

    for column in df.columns:

        series = df[column]

        row = {
            "dataset":
                dataset_name,

            "variable":
                column,

            "dtype":
                str(series.dtype),

            "n_rows":
                len(series),

            "n_missing":
                int(
                    series.isna()
                    .sum()
                ),

            "missing_pct":
                float(
                    100
                    * series.isna()
                    .mean()
                ),

            "n_unique":
                int(
                    series.nunique(
                        dropna=True
                    )
                )
        }

        if pd.api.types.is_numeric_dtype(
            series
        ):

            row["min"] = (
                series.min(
                    skipna=True
                )
            )

            row["max"] = (
                series.max(
                    skipna=True
                )
            )

            row["mean"] = (
                series.mean(
                    skipna=True
                )
            )

            row["median"] = (
                series.median(
                    skipna=True
                )
            )

        else:

            row["min"] = np.nan
            row["max"] = np.nan
            row["mean"] = np.nan
            row["median"] = np.nan

        output.append(row)

    return pd.DataFrame(
        output
    )


# %% ============================================================
# 22. GENERIC MISSINGNESS AUDIT FUNCTION
# ================================================================

def missingness_audit(df):

    result = pd.DataFrame(
        {
            "variable":
                df.columns,

            "missing_n":
                df.isna()
                .sum()
                .values,

            "missing_pct":
                (
                    100
                    * df.isna()
                    .mean()
                )
                .values
        }
    )

    return result.sort_values(
        "missing_pct",
        ascending=False
    )


# %% ============================================================
# 23. BLANK-STRING AUDIT FUNCTION
# ================================================================

def blank_string_audit(df):

    results = []

    for column in df.columns:

        if df[column].dtype == "object":

            blank_mask = (
                df[column]
                .fillna("")
                .astype(str)
                .str.strip()
                .eq("")
            )

            results.append(
                {
                    "variable":
                        column,

                    "blank_strings":
                        int(
                            blank_mask.sum()
                        )
                }
            )

    return pd.DataFrame(
        results
    )


# %% ============================================================
# 24. EXACT DUPLICATE AUDIT FUNCTION
# ================================================================

def duplicate_audit(df):

    duplicated = (
        df.duplicated(
            keep=False
        )
    )

    return df.loc[
        duplicated
    ].copy()


# %% ============================================================
# 25. ROBUST Z-SCORE FUNCTION FOR ANOMALY SCREENING
# ================================================================

def robust_zscore(series):

    x = pd.to_numeric(
        series,
        errors="coerce"
    )

    median = x.median()

    mad = (
        x - median
    ).abs().median()

    if (
        pd.isna(mad)
        or
        mad == 0
    ):

        return pd.Series(
            np.nan,
            index=series.index
        )

    z = (
        0.6745
        * (x - median)
        / mad
    )

    return z


def robust_anomaly_table(
    df,
    threshold=3.5
):

    results = []

    numeric_columns = (
        df.select_dtypes(
            include=np.number
        )
        .columns
    )

    for column in numeric_columns:

        z = robust_zscore(
            df[column]
        )

        mask = (
            z.abs()
            > threshold
        )

        for index in df.index[
            mask.fillna(False)
        ]:

            results.append(
                {
                    "row_index":
                        index,

                    "variable":
                        column,

                    "value":
                        df.loc[
                            index,
                            column
                        ],

                    "robust_z":
                        z.loc[index]
                }
            )

    return pd.DataFrame(
        results
    )


# %% ============================================================
# 26. RANGE-FLAGGING FUNCTION
# ================================================================

def range_flag(
    series,
    minimum,
    maximum
):

    x = pd.to_numeric(
        series,
        errors="coerce"
    )

    return (
        (x < minimum)
        |
        (x > maximum)
    )


# %% ============================================================
# 27. GENERIC MINERAL-TOTAL CHECK FUNCTION
# ================================================================

def check_total(
    series,
    minimum=None,
    maximum=None
):

    x = pd.to_numeric(
        series,
        errors="coerce"
    )

    flag = pd.Series(
        False,
        index=x.index
    )

    if minimum is not None:

        flag |= (
            x < minimum
        )

    if maximum is not None:

        flag |= (
            x > maximum
        )

    return flag


# %% ============================================================
# 28. LEAKAGE / VARIABLE-ROLE CLASSIFICATION FUNCTION
# ================================================================

def classify_variable_role(column):

    c = (
        str(column)
        .lower()
        .replace(" ", "")
        .replace("_", "")
    )

    if any(
        term in c
        for term in [
            "reference",
            "source",
            "sample",
            "run",
            "author"
        ]
    ):
        return "identifier_or_provenance"

    if (
        ("exp" in c or "experimental" in c)
        and
        (
            "temperature" in c
            or c.startswith("t")
        )
    ):
        return "reference_temperature"

    if (
        ("exp" in c or "experimental" in c)
        and
        (
            "pressure" in c
            or c.startswith("p")
        )
    ):
        return "reference_pressure"

    if any(
        term in c
        for term in [
            "gh84",
            "gh85",
            "gh90",
            "gh00",
            "ph80",
            "ph90",
            "ph94",
            "ph21",
            "hbl97",
            "gasp",
            "gbpq",
            "ghpq",
            "ph07",
            "ph15"
        ]
    ):

        if (
            c.startswith("t")
            or "temp" in c
        ):
            return "derived_temperature"

        if (
            c.startswith("p")
            or "press" in c
        ):
            return "derived_pressure"

    chemistry_terms = [
        "sio2",
        "tio2",
        "al2o3",
        "feo",
        "fe2o3",
        "mno",
        "mgo",
        "cao",
        "na2o",
        "k2o"
    ]

    if any(
        term in c
        for term in chemistry_terms
    ):
        return "mineral_chemistry"

    return "unclassified"


def build_leakage_table(df):

    table = pd.DataFrame(
        {
            "variable":
                df.columns
        }
    )

    table["role"] = (
        table["variable"]
        .apply(
            classify_variable_role
        )
    )

    table[
        "allowed_as_predictor_for_experimental_T"
    ] = (
        ~table["role"]
        .isin(
            [
                "derived_temperature",
                "reference_temperature"
            ]
        )
    )

    table[
        "allowed_as_predictor_for_experimental_P"
    ] = (
        ~table["role"]
        .isin(
            [
                "derived_pressure",
                "reference_pressure"
            ]
        )
    )

    return table


# %% ============================================================
# 29. PREDICTION ERROR FUNCTION
# ================================================================

def prediction_errors(
    observed,
    predicted
):

    observed = pd.to_numeric(
        observed,
        errors="coerce"
    )

    predicted = pd.to_numeric(
        predicted,
        errors="coerce"
    )

    error = (
        predicted
        - observed
    )

    result = pd.DataFrame(
        {
            "error":
                error,

            "absolute_error":
                error.abs(),

            "squared_error":
                error ** 2
        }
    )

    return result


# %% ============================================================
# 30. AGREEMENT METRICS FUNCTION
# ================================================================

def agreement_metrics(
    observed,
    predicted
):

    observed = pd.to_numeric(
        observed,
        errors="coerce"
    )

    predicted = pd.to_numeric(
        predicted,
        errors="coerce"
    )

    valid = (
        observed.notna()
        &
        predicted.notna()
    )

    y = observed[valid]
    yhat = predicted[valid]

    if len(y) == 0:

        return {
            "n": 0,
            "bias": np.nan,
            "mae": np.nan,
            "rmse": np.nan,
            "error_sd": np.nan,
            "correlation": np.nan
        }

    error = (
        yhat
        - y
    )

    metrics = {
        "n":
            len(y),

        "bias":
            error.mean(),

        "mae":
            error.abs().mean(),

        "rmse":
            np.sqrt(
                np.mean(
                    error ** 2
                )
            ),

        "error_sd":
            error.std(
                ddof=1
            ),

        "correlation":
            y.corr(
                yhat
            )
    }

    return metrics


# %% ============================================================
# 31. DATA DICTIONARY FUNCTION
# ================================================================

def make_data_dictionary(
    df,
    dataset_name
):

    rows = []

    for column in df.columns:

        series = df[column]

        example_values = (
            series
            .dropna()
            .astype(str)
            .unique()[:3]
        )

        rows.append(
            {
                "dataset":
                    dataset_name,

                "variable":
                    column,

                "dtype":
                    str(series.dtype),

                "missing_n":
                    int(
                        series.isna()
                        .sum()
                    ),

                "missing_pct":
                    100
                    * series.isna()
                    .mean(),

                "unique_n":
                    int(
                        series.nunique(
                            dropna=True
                        )
                    ),

                "examples":
                    " | ".join(
                        example_values
                    )
            }
        )

    return pd.DataFrame(
        rows
    )


# %% ============================================================
# 32. DATA-GENERATING PROCESS / PROVENANCE FIGURE
# ================================================================

fig, ax = plt.subplots(
    figsize=(11, 12)
)

ax.axis("off")

steps = [
    "Experimental system / natural metamorphic rock",
    "Mineral assemblage selection",
    "Mineral grain/domain selection",
    "Electron-microprobe / chemical analysis",
    "Oxide or cation composition",
    "Published experimental / natural-rock study",
    "Literature screening and compilation",
    "Electronic supplementary database S1-S4",
    "Thermobarometric calculation",
    "Data-quality and provenance audit",
    "Statistical / machine-learning analysis"
]

y_positions = np.linspace(
    0.95,
    0.05,
    len(steps)
)

for i, (step, y) in enumerate(
    zip(
        steps,
        y_positions
    )
):

    ax.text(
        0.5,
        y,
        step,
        ha="center",
        va="center",
        fontsize=11,
        bbox=dict(
            boxstyle="round,pad=0.5",
            edgecolor="black",
            facecolor="white"
        )
    )

    if i < len(steps) - 1:

        ax.annotate(
            "",
            xy=(
                0.5,
                y_positions[i + 1] + 0.025
            ),
            xytext=(
                0.5,
                y - 0.025
            ),
            arrowprops=dict(
                arrowstyle="->",
                linewidth=1.5
            )
        )

ax.set_title(
    "Data-Generating Process and Provenance "
    "of the Geothermobarometry Database",
    fontsize=14,
    fontweight="bold",
    pad=20
)

plt.tight_layout()

plt.savefig(
    FIGURES_DIR /
    "DS_A1_provenance_DGP.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# %% ============================================================
# 33. CREATE DATA CARD
# ================================================================

data_card = """
# DATA CARD

## Dataset title
Experimental and Natural-Rock Database for Comparative
Evaluation of Metamorphic Geothermobarometers

## Scientific domain
Metamorphic petrology / geothermobarometry

## Components
S1 - Garnet-hornblende experimental database
S2 - Plagioclase-hornblende experimental database
S3 - Al2SiO5-bearing natural metapelite database
S4 - Compositionally diverse natural metamorphic rocks

## Primary purpose
Evaluation of measurement integrity, provenance,
precision, accuracy, applicability and generalizability
of selected geothermometers and geobarometers.

## Observation units
S1-S2: experimental run
S3-S4: literature-derived natural-rock sample

## Source
Rabbani and Wu (2026)
Journal of Asian Earth Sciences 306, 107096

DOI:
10.1016/j.jseaes.2026.107096

## Data-quality criteria
Published database screening includes mineral-analysis
quality criteria, petrographic equilibrium requirements,
compositional consistency and treatment of mineral zoning.

## Known limitations
- Literature-derived heterogeneous sources
- Unequal representation of compositional domains
- Potential study-level dependence
- Uncertainty in Fe3+/Fe2+ estimation
- Calibration-domain limitations
- Some formulations based on unreversed experiments
- Natural-rock reference values are themselves model-derived

## Intended uses
- Thermobarometer comparison
- Statistical uncertainty analysis
- Predictive modelling
- Applicability-domain analysis
- Failure-mode analysis

## Prohibited uses
Do not interpret numerical agreement as proof of true
geological equilibration or universal applicability.

## License / redistribution status
TO BE VERIFIED BEFORE PUBLIC REPOSITORY RELEASE.

## Dataset version
Frozen using SHA-256 hashes stored in:
metadata/data_manifest_sha256.csv
"""

with open(
    METADATA_DIR /
    "DATA_CARD.md",
    "w",
    encoding="utf-8"
) as file:

    file.write(
        data_card
    )

print(
    "\nData Card saved to:",
    METADATA_DIR /
    "DATA_CARD.md"
)


# %% ============================================================
# 34. CREATE AI-USE / VERIFICATION LOG
# ================================================================

ai_log = pd.DataFrame(
    [
        {
            "date":
                datetime.now()
                .date()
                .isoformat(),

            "AI_tool":
                "ChatGPT",

            "task":
                "Design DS-A1 provenance and measurement audit workflow",

            "AI_recommendation":
                "Preserve raw data; separate experimental and natural datasets; "
                "audit provenance, schema, ranges, missingness, duplicates, "
                "anomalies and leakage.",

            "accepted_rejected":
                "Pending independent verification",

            "independent_verification":
                "Compare code outputs against published methodology and "
                "supplementary tables.",

            "verification_result":
                "To be completed by researcher"
        }
    ]
)

ai_log.to_csv(
    METADATA_DIR /
    "AI_use_verification_log.csv",
    index=False
)

print(
    "\nAI-use log saved to:",
    METADATA_DIR /
    "AI_use_verification_log.csv"
)


# %% ============================================================
# 35. INITIAL DS-A1 AUDIT CHECKLIST
# ================================================================

audit_summary = pd.DataFrame(
    {
        "check": [
            "Source/provenance documented",
            "SHA256 frozen",
            "Software environment recorded",
            "Thermobarometer inventory inspected",
            "Raw S1-S4 tables loaded",
            "Header candidates inspected",
            "Raw structural audit completed",
            "Missingness checked",
            "Blank strings checked",
            "Exact duplicates checked",
            "Key duplicates checked",
            "Published P-T domains checked",
            "Chemical validity checked",
            "Robust anomalies flagged",
            "Leakage reviewed",
            "Bias/counterexample documented",
            "Prohibited claim documented",
            "AI verification recorded"
        ],

        "status": [
            "complete",
            "complete",
            "complete",
            "complete",
            "complete",
            "complete",
            "complete",
            "pending finalized headers",
            "pending finalized headers",
            "pending finalized headers",
            "pending finalized headers",
            "pending finalized headers",
            "pending finalized headers",
            "pending finalized headers",
            "pending finalized headers",
            "complete",
            "complete",
            "started"
        ]
    }
)

audit_summary.to_csv(
    RESULTS_DIR /
    "DS_A1_audit_checklist.csv",
    index=False
)

print("\nINITIAL AUDIT CHECKLIST")
print("=" * 80)

print(
    audit_summary
    .to_string(index=False)
)


# %% ============================================================
# 36. FINAL MESSAGE FOR THIS FIRST EXECUTION
# ================================================================

print("\n")
print("=" * 80)
print("DS-A1 INITIAL AUDIT STAGE COMPLETED")
print("=" * 80)

print(
    "\nImportant:"
)

print(
    "The four supplementary datasets have been loaded as raw tables."
)

print(
    "Do not yet manually alter headers or delete rows."
)

print(
    "Inspect the Spyder console output for the first 15 rows of "
    "S1, S2, S3 and S4 and the candidate header rows."
)

print(
    "\nGenerated files can be found in:"
)

print("Results :", RESULTS_DIR)
print("Metadata:", METADATA_DIR)
print("Figures :", FIGURES_DIR)