"""
Script 9 — Python Comprehensions for ML Pipelines
AlphaDefense v2.0 | Phase 2 — Feature Engineering Utilities

Gate Quiz: 5/5 cleared
Certificate ID: ADF-S9-PY-COMP-2026

Demonstrates list, dict, and ternary comprehensions applied to the
IEEE-CIS fraud dataset (394 raw columns / 338 engineered features
from the Script 8 pipeline).
"""

import pandas as pd

# df = output of Script 8 pipeline (cleaned, 338 engineered features)
# df = pd.read_csv("train_transaction_cleaned.csv")


# ---------------------------------------------------------------
# 1. LIST COMPREHENSION — Filter V-features from the column set
# ---------------------------------------------------------------
# IEEE-CIS V-columns are capital 'V' (V1, V2, ... V339).
# .startswith('v') would silently return an empty list since case matters —
# no error, no warning, just wrong data. Caught this during debugging.
v_features = [col for col in df.columns if col.startswith('V')]


# ---------------------------------------------------------------
# 2. DICT COMPREHENSION — Map column -> null count (nulls > 0 only)
# ---------------------------------------------------------------
null_counts = {
    col: df[col].isnull().sum()
    for col in df.columns
    if df[col].isnull().sum() > 0
}


# ---------------------------------------------------------------
# 3. TERNARY LIST COMPREHENSION — Per-transaction risk label
# ---------------------------------------------------------------
# Rule: TransactionAmt > 100 -> 'High Risk', else 'Low Risk'.
# Every transaction gets a label — this is NOT a filter (list size stays
# the same), unlike comprehensions that use `if` to drop elements.
risk_labels = [
    'High Risk' if amt > 100 else 'Low Risk'
    for amt in df['TransactionAmt']
]


# ---------------------------------------------------------------
# 4. MULTI-DICT COMPREHENSION — Cross-reference importance + nulls
# ---------------------------------------------------------------
# Phase 3 use case: shortlist features that are both important (SHAP-ready)
# and clean (low missingness). feature_importance and null_counts are
# populated once Phase 3 SHAP values exist.
#
# Safety pattern: iterate the dict you trust, guard the second lookup with
# `col in null_counts` — protects against KeyError if the two dicts don't
# share identical keys.
#
# feature_importance = {...}   # from SHAP / model.feature_importances_
candidate_features = [
    col for col in feature_importance
    if col in null_counts
    and feature_importance[col] > 0.05
    and null_counts[col] < 50
]


# ---------------------------------------------------------------
# 5. SHAP THRESHOLD FILTER — Phase 3 prep pattern
# ---------------------------------------------------------------
# Will be wired to the real SHAP TreeExplainer output once Phase 3 starts.
# shap_values = {...}   # e.g. {'V1': 0.003, 'card1': 0.045, ...}
important_features = [col for col in shap_values if shap_values[col] > 0.01]
