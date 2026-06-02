# ============================================================
# AlphaDefense — Script 7: CSV + Pandas
# Topic: Loading, Exploring, and Cleaning IEEE-CIS Fraud Data
# Author: Krrish Malhan
# GitHub: ksindustries2024-lgtm/Alphadefense22
# ============================================================
# WHAT: Loads IEEE-CIS transaction and identity CSVs,
#       merges them, performs EDA, drops high-null columns,
#       calculates class imbalance and scale_pos_weight.
# WHY:  Produces clean_data.csv as input for all future scripts.
# HOW:  pandas read_csv → merge → missing analysis → drop → save
# ============================================================

import pandas as pd
import numpy as np

# ── STEP 1: Load raw CSVs ───────────────────────────────────
# Loading both IEEE-CIS files. train_transaction has 590,540 rows x 394 cols.
# train_identity has supplementary device/browser info for a subset of transactions.

train_transaction = pd.read_csv('train_transaction.csv')
train_identity = pd.read_csv('train_identity.csv')

print("=" * 60)
print("STEP 1: Raw Data Shapes")
print("=" * 60)
print(f"train_transaction shape: {train_transaction.shape}")
print(f"train_identity shape:    {train_identity.shape}")

# ── STEP 2: Inspect dtypes and first rows ───────────────────
# dtypes tell us which columns are numeric vs categorical.
# This matters because XGBoost needs numeric input — categoricals must be encoded.

print("\n" + "=" * 60)
print("STEP 2: Data Types (first 20 columns)")
print("=" * 60)
print(train_transaction.dtypes.head(20))

print("\nFirst 5 rows of train_transaction:")
print(train_transaction.head())

# ── STEP 3: Merge on TransactionID ──────────────────────────
# Left join: keeps ALL transaction rows, adds identity info where available.
# Transactions without identity data get NaN in identity columns — that's fine.

df = pd.merge(train_transaction, train_identity, on='TransactionID', how='left')

print("\n" + "=" * 60)
print("STEP 3: Merged DataFrame Shape")
print("=" * 60)
print(f"Merged df shape: {df.shape}")

# ── STEP 4: Missing Value Analysis ──────────────────────────
# IEEE-CIS has many columns with massive nulls (V-columns especially).
# We need to know which columns are worth keeping.

print("\n" + "=" * 60)
print("STEP 4: Missing Value Report")
print("=" * 60)

missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_report = pd.DataFrame({
    'missing_count': missing,
    'missing_pct': missing_pct
})
missing_report = missing_report[missing_report['missing_count'] > 0].sort_values(
    'missing_pct', ascending=False
)

print(missing_report.head(15))
print(f"\nTotal columns with ANY missing values: {len(missing_report)}")

# ── STEP 5: Basic Statistics for Numeric Columns ────────────
# describe() gives mean, std, min, 25th/50th/75th percentile, max.
# Critical for spotting outliers in TransactionAmt before model training.

print("\n" + "=" * 60)
print("STEP 5: Basic Statistics (numeric columns)")
print("=" * 60)
print(df.describe())

# ── STEP 6: Class Imbalance Analysis ────────────────────────
# isFraud: 0 = legitimate, 1 = fraud
# IEEE-CIS is heavily imbalanced — ~96.5% legit, ~3.5% fraud
# A naive model predicting "all legit" gets 96.5% accuracy — completely useless.

print("\n" + "=" * 60)
print("STEP 6: Class Imbalance (isFraud)")
print("=" * 60)

fraud_counts = df['isFraud'].value_counts()
fraud_pct = (fraud_counts / len(df)) * 100

print(fraud_counts)
print(f"\nPercentage breakdown:")
print(fraud_pct.round(2))

# scale_pos_weight = count(non-fraud) / count(fraud)
# Tells XGBoost: "Treat each fraud sample as X times more important"
scale_pos_weight = fraud_counts[0] / fraud_counts[1]
print(f"\nscale_pos_weight for XGBoost: {scale_pos_weight:.2f}")
print("→ Each fraud transaction is weighted ~27x more than a legitimate one")

# ── STEP 7: Drop High-Null Columns (>80% missing) ───────────
# A column that is 80%+ null cannot contribute meaningful signal.
# Imputing it would mean inventing data — worse than dropping.
# Memory benefit: IEEE-CIS V-columns alone are hundreds of columns.

print("\n" + "=" * 60)
print("STEP 7: Dropping Columns with >80% Missing Values")
print("=" * 60)

threshold = 0.8
cols_to_drop = missing_pct[missing_pct > 80].index.tolist()
print(f"Columns to drop ({len(cols_to_drop)} total): {cols_to_drop[:10]} ...")

df_clean = df.drop(columns=cols_to_drop)
print(f"\nShape BEFORE drop: {df.shape}")
print(f"Shape AFTER drop:  {df_clean.shape}")
print(f"Columns removed:   {df.shape[1] - df_clean.shape[1]}")

# ── STEP 8: Save Cleaned Data for Script 8+ ─────────────────
# All future scripts load clean_data.csv — no re-cleaning needed.

df_clean.to_csv('clean_data.csv', index=False)
print("\n" + "=" * 60)
print("STEP 8: Saved clean_data.csv")
print("=" * 60)
print(f"Final clean dataset: {df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns")
print("clean_data.csv is ready for Script 8 (Pandas Operations).")
print("=" * 60)
