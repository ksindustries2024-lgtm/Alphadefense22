# ============================================================
# Script 8: Pandas Operations - Data Cleaning & Preprocessing
# Project : AlphaDefense - Quantitative Fraud Detection System
# Author  : Krrish Malhan (Roll: 549/24)
# Phase   : Phase 1 - EDA → Feature Engineering
# Depends : Loads train_transaction.csv directly (standalone)
# ============================================================

# PURPOSE:
# Script 7 told us WHAT the data looks like.
# Script 8 makes the data MODEL-READY.
# Every operation here has a direct reason tied to XGBoost Phase 2.

# ============================================================
# IMPORTS
# ============================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

# ============================================================
# STEP 1: RELOAD DATA (standalone script)
# ============================================================

df = pd.read_csv(r'C:\Users\krrishmalhan122\AlphaDefense\train_transaction.csv')

print("=" * 60)
print("STEP 1: DATA LOADED")
print("=" * 60)
print(f"Shape: {df.shape}")
# Expected: (590540, 394)

# ============================================================
# STEP 2: DROP HIGH-NULL COLUMNS (>80% missing)
# ============================================================

# WHY 80% threshold?
# A column that is 80%+ empty cannot teach the model anything useful.
# Imputing 80% of values is not filling gaps — it's fabricating data.
# In fraud detection, fabricated data = fabricated patterns = wrong decisions.

print("\n" + "=" * 60)
print("STEP 2: DROPPING COLUMNS WITH >80% NULL VALUES")
print("=" * 60)

# Calculate null percentage for every column
null_percent = df.isnull().mean() * 100

# Boolean mask: True = column has >80% nulls
high_null_cols = null_percent[null_percent > 80].index.tolist()

print(f"Columns to drop (>80% null): {len(high_null_cols)}")
print(high_null_cols[:10], "...")  # Show first 10

# Drop them
df.drop(columns=high_null_cols, inplace=True)

print(f"Shape after dropping high-null columns: {df.shape}")
# Expect significant column reduction from 394

# ============================================================
# STEP 3: SEPARATE FEATURES AND TARGET
# ============================================================

print("\n" + "=" * 60)
print("STEP 3: SEPARATING FEATURES (X) AND TARGET (y)")
print("=" * 60)

# isFraud is the target — what we want to predict
# Everything else is a feature — what the model learns from

y = df['isFraud']
X = df.drop(columns=['isFraud']).copy()  # .copy() prevents SettingWithCopyWarning

print(f"X shape (features): {X.shape}")
print(f"y shape (target)  : {y.shape}")
print(f"Fraud cases       : {y.sum()} ({y.mean() * 100:.2f}%)")

# ============================================================
# STEP 4: ENCODE CATEGORICAL COLUMNS (object dtype)
# ============================================================

# WHY LabelEncoder?
# XGBoost needs numbers. 'ProductCD' = 'W', 'H', 'C' etc.
# LabelEncoder converts: 'C'→0, 'H'→1, 'R'→2, 'S'→3, 'W'→4
# It assigns an integer to each unique string value.
# Important: LabelEncoder is fine for tree models (XGBoost).
# For linear models you'd need OneHotEncoder — but XGBoost
# doesn't assume ordinal relationships between integers.

print("\n" + "=" * 60)
print("STEP 4: LABEL ENCODING CATEGORICAL COLUMNS")
print("=" * 60)

le = LabelEncoder()

# Identify all string columns
cat_cols = X.select_dtypes(include='object').columns.tolist()
print(f"Categorical columns to encode: {len(cat_cols)}")
print(cat_cols)

for col in cat_cols:
    # fillna('missing') → LabelEncoder cannot handle NaN
    # We replace NaN with the string 'missing' before encoding
    X[col] = X[col].fillna('missing')
    X[col] = le.fit_transform(X[col])

print("Encoding complete.")

# ============================================================
# STEP 5: FILL REMAINING NUMERIC NULLS WITH MEDIAN
# ============================================================

# WHY MEDIAN not MEAN?
# Fraud datasets have extreme outliers (e.g. TransactionAmt = $15,000)
# Mean gets pulled by outliers → bad fill value
# Median is the middle value → robust to outliers

print("\n" + "=" * 60)
print("STEP 5: FILLING NUMERIC NULLS WITH MEDIAN")
print("=" * 60)

null_before = X.isnull().sum().sum()
X.fillna(X.median(numeric_only=True), inplace=True)
null_after = X.isnull().sum().sum()

print(f"Null values before fill: {null_before}")
print(f"Null values after fill : {null_after}")
# After fill: should be 0

# ============================================================
# STEP 6: CALCULATE scale_pos_weight FOR XGBOOST
# ============================================================

# This is the single most important number for Phase 2.
# scale_pos_weight = count(negative class) / count(positive class)
#                  = legitimate transactions / fraud transactions
#
# Effect: XGBoost internally multiplies the gradient of each
# fraud sample by this weight → forces the model to treat
# 1 fraud case as if it were ~27.58 legitimate cases.
# Without this, XGBoost just predicts 0 for everything
# and achieves 96.5% accuracy — which is completely useless.

print("\n" + "=" * 60)
print("STEP 6: SCALE_POS_WEIGHT CALCULATION")
print("=" * 60)

neg = (y == 0).sum()  # legitimate
pos = (y == 1).sum()  # fraud
spw = round(neg / pos, 2)

print(f"Legitimate transactions : {neg}")
print(f"Fraud transactions      : {pos}")
print(f"scale_pos_weight        : {spw}")
# Expected: ~27.58

# ============================================================
# STEP 7: STANDARD SCALING
# ============================================================

# WHY SCALE for XGBoost?
# Strictly speaking, XGBoost (tree-based) doesn't REQUIRE scaling.
# But we scale here because Phase 6 will use FastAPI with multiple
# model types, and scaled data is the standard contract between
# data pipeline and model layer in production systems.

print("\n" + "=" * 60)
print("STEP 7: STANDARD SCALING FEATURES")
print("=" * 60)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

print(f"Scaling complete. Shape: {X_scaled.shape}")
print(f"TransactionAmt mean after scaling: {X_scaled['TransactionAmt'].mean():.4f}")
print(f"TransactionAmt std after scaling : {X_scaled['TransactionAmt'].std():.4f}")
# After StandardScaler: mean ≈ 0.0, std ≈ 1.0

# ============================================================
# STEP 8: STRATIFIED TRAIN/TEST SPLIT (80/20)
# ============================================================

# WHY STRATIFIED?
# Random split on imbalanced data can put almost no fraud cases
# in the test set by chance. stratify=y ensures BOTH train and
# test sets maintain the same 3.5% fraud ratio as the full dataset.
# This gives us a reliable AUC-ROC score in Phase 2.

print("\n" + "=" * 60)
print("STEP 8: STRATIFIED 80/20 TRAIN/TEST SPLIT")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y,
    test_size=0.2,
    random_state=42,
    stratify=y          # ← this is the key parameter
)

print(f"X_train : {X_train.shape}")
print(f"X_test  : {X_test.shape}")
print(f"Train fraud rate: {y_train.mean() * 100:.2f}%")
print(f"Test fraud rate : {y_test.mean() * 100:.2f}%")
# Both should be ~3.5% — confirming stratification worked

# ============================================================
# STEP 9: SAVE OUTPUTS TO CSV
# ============================================================

print("\n" + "=" * 60)
print("STEP 9: SAVING PROCESSED DATA TO CSV")
print("=" * 60)

X_train.to_csv(r'C:\Users\krrishmalhan122\AlphaDefense\X_train.csv', index=False)
X_test.to_csv(r'C:\Users\krrishmalhan122\AlphaDefense\X_test.csv', index=False)
y_train.to_csv(r'C:\Users\krrishmalhan122\AlphaDefense\y_train.csv', index=False)
y_test.to_csv(r'C:\Users\krrishmalhan122\AlphaDefense\y_test.csv', index=False)

print("Saved: X_train.csv, X_test.csv, y_train.csv, y_test.csv")
print("These 4 files are the direct input to Phase 2 XGBoost training.")

# ============================================================
# SCRIPT 8 SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("SCRIPT 8 SUMMARY")
print("=" * 60)
print(f"High-null columns dropped : {len(high_null_cols)}")
print(f"Categorical cols encoded  : {len(cat_cols)}")
print(f"Nulls remaining           : {null_after}")
print(f"scale_pos_weight          : {spw}")
print(f"Train set size            : {X_train.shape[0]} rows")
print(f"Test set size             : {X_test.shape[0]} rows")
print(f"Gate : Script 8 COMPLETE → Script 9 unlocked")
print("=" * 60) 
