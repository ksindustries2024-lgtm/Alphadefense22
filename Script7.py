# ============================================================
# Script 7: IEEE-CIS Fraud Dataset - Data Loading & Inspection
# Project  : AlphaDefense - Quantitative Fraud Detection System
# Author   : Krrish Malhan (Roll: 549/24)
# College  : DAV University, Jalandhar
# Phase    : Phase 1 - EDA Foundation
# Date     : May 2026
# GitHub   : ksindustries2024-lgtm/Alphadefense22
# ============================================================

# PURPOSE:
# This script is the entry point of AlphaDefense Phase 1 (EDA).
# We load the IEEE-CIS Fraud Detection dataset, inspect its structure,
# and extract key statistics that will drive all future modeling decisions
# (class imbalance ratio, missing value strategy, feature types).
#
# DATASET:
# Source  : IEEE-CIS Fraud Detection (Kaggle)
# Files   : train_transaction.csv + train_identity.csv
# Size    : 590,540 transactions | 3.5% fraud rate
# Task    : Binary classification → isFraud (0 or 1)

# ============================================================
# IMPORTS
# ============================================================

import pandas as pd    # pandas: core library for data manipulation
                       # DataFrame = 2D table (rows x columns) in memory
                       # Like Excel but controlled entirely by code

# ============================================================
# STEP 1: LOAD THE TRANSACTION FILE
# ============================================================

# pd.read_csv() reads a CSV file and returns a DataFrame object
# The file path points to local AlphaDefense project directory
df_trans = pd.read_csv(r'C:\Users\krrishmalhan122\AlphaDefense\train_transaction.csv')

print("=" * 55)
print("STEP 1: TRANSACTION FILE - SHAPE")
print("=" * 55)

# .shape returns a tuple (rows, columns)
# This tells us exactly how large the dataset is
print(df_trans.shape)

# OUTPUT:
# (590540, 394)
# → 590,540 transactions (rows)
# → 394 feature columns
# → This is a large-scale, real-world fraud dataset

# ============================================================
# STEP 2: INSPECT COLUMN DATA TYPES
# ============================================================

print("\n" + "=" * 55)
print("STEP 2: COLUMN DATA TYPES (dtypes)")
print("=" * 55)

# .dtypes shows the data type of every column
# int64   = whole numbers (e.g. TransactionID, isFraud)
# float64 = decimal numbers (e.g. TransactionAmt, V-features)
# object  = strings/text (e.g. ProductCD, card4, P_emaildomain)
#
# WHY THIS MATTERS FOR ALPHADEFENSE:
# XGBoost cannot handle 'object' (string) columns directly.
# Those columns need Label Encoding or One-Hot Encoding in Phase 1.
print(df_trans.dtypes)

# OUTPUT:
# TransactionID      int64
# isFraud            int64
# TransactionDT      int64
# TransactionAmt     float64
# ProductCD          object   ← string → needs encoding
# ...
# V335               float64
# V336               float64
# V337               float64
# V338               float64
# V339               float64
# Length: 394, dtype: object

# ============================================================
# STEP 3: MISSING VALUE AUDIT
# ============================================================

print("\n" + "=" * 55)
print("STEP 3: MISSING VALUES PER COLUMN")
print("=" * 55)

# .isnull() returns True/False for each cell (True = missing)
# .sum() counts the True values per column
# This gives us the count of missing values in each column
print(df_trans.isnull().sum())

# OUTPUT (key columns shown):
# TransactionID      0         ← no missing values
# isFraud            0         ← no missing values (target column)
# TransactionDT      0
# TransactionAmt     0
# ProductCD          0
# card1              0
# card2              8933      ← 8,933 missing
# card3              1565
# card4              1577
# card5              4259
# card6              1571
# addr1              65706     ← 65,706 missing (~11%)
# addr2              65706
# dist1              352271    ← 352,271 missing (~60%) → HIGH
# dist2              552913    ← 552,913 missing (~94%) → CRITICAL
# P_emaildomain      94456     ← 94,456 missing (~16%)
# R_emaildomain      453249    ← 453,249 missing (~77%) → HIGH
# C1                 0
# C2                 0
# C3                 0
# dtype: int64
#
# KEY INSIGHT:
# dist2 is 94% empty → likely to be dropped in feature engineering
# R_emaildomain is 77% empty → imputation or drop decision in Phase 1
# isFraud has 0 missing → target column is clean ✓

# ============================================================
# STEP 4: LOAD THE IDENTITY FILE
# ============================================================

print("\n" + "=" * 55)
print("STEP 4: IDENTITY FILE - SHAPE")
print("=" * 55)

# The identity file contains device/browser info per transaction
# Not every transaction has identity data → smaller file
df_identity = pd.read_csv(r'C:\Users\krrishmalhan122\AlphaDefense\train_identity.csv')

print(df_identity.shape)

# OUTPUT:
# (144233, 41)
# → Only 144,233 of 590,540 transactions have identity data
# → 41 identity-related columns (device type, browser, OS, etc.)
# → Merge with transaction file will be done on Google Colab (RAM limit)

# ============================================================
# STEP 5: FRAUD CLASS DISTRIBUTION (MOST IMPORTANT STEP)
# ============================================================

print("\n" + "=" * 55)
print("STEP 5: FRAUD CLASS DISTRIBUTION")
print("=" * 55)

# value_counts(normalize=True) gives proportion (%) instead of raw count
# This tells us how imbalanced the dataset is
print(df_trans['isFraud'].value_counts(normalize=True))

# OUTPUT:
# isFraud
# 0    0.96501    ← 96.5% legitimate transactions
# 1    0.03499    ← 3.5%  fraud transactions
# Name: proportion, dtype: float64
#
# KEY CALCULATION FOR ALPHADEFENSE PHASE 1:
# Class imbalance ratio = 0.96501 / 0.03499 = 27.58
#
# This value becomes scale_pos_weight in XGBoost:
#   xgb_model = XGBClassifier(scale_pos_weight=27.58, ...)
#
# scale_pos_weight tells XGBoost: "treat each fraud case as
# if it's worth 27.58 legitimate cases" → fixes class imbalance
# Without this → model predicts everything as legitimate (96% accuracy
# but catches ZERO fraud) → useless for real-world deployment

# ============================================================
# STEP 6: MERGE TRANSACTION + IDENTITY (COLAB - RAM CONSTRAINT)
# ============================================================

print("\n" + "=" * 55)
print("STEP 6: MERGE NOTE")
print("=" * 55)

# NOTE: Full merge operation requires ~6-8GB RAM
# Local machine RAM is insufficient for this operation
# Merge will be executed on Google Colab / Kaggle Notebook in Phase 1
#
# Merge code (preserved for reference):
# df_merged = df_trans.merge(df_identity, on='TransactionID', how='left')
# how='left' → keep ALL transactions, add identity cols where available
# Transactions without identity data get NaN in identity columns
# print(df_merged.shape)
# Expected output: (590540, 434) → 394 + 41 - 1 shared column

print("Merge operation flagged for Google Colab execution.")
print("RAM constraint on local machine.")
print("Merge code preserved in script comments above.")

# ============================================================
# SCRIPT 7 SUMMARY
# ============================================================

print("\n" + "=" * 55)
print("SCRIPT 7 SUMMARY - ALPHADEFENSE PHASE 1 EDA FOUNDATION")
print("=" * 55)
print(f"Transaction File : 590,540 rows × 394 columns")
print(f"Identity File    : 144,233 rows × 41 columns")
print(f"Fraud Rate       : 3.499%")
print(f"Legit Rate       : 96.501%")
print(f"scale_pos_weight : {round(0.96501 / 0.03499, 2)} (for XGBoost Phase 1)")
print(f"Critical Nulls   : dist2 (94%), R_emaildomain (77%), dist1 (60%)")
print(f"String Columns   : ProductCD, card4, card6, P/R_emaildomain (need encoding)")
print(f"EDA Gate         : CLEARED → Script 8 (Pandas Operations) unlocked")
print("=" * 55)
