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

print("STEP 1: Loading raw datasets...")

# Peek at a small sample to find float64 columns, so the real load uses float32
sample = pd.read_csv(r"C:\Users\krrishmalhan122\AlphaDefense\train_transaction.csv", nrows=1000)
float_cols = sample.select_dtypes(include='float64').columns.tolist()
dtype_map = {col: 'float32' for col in float_cols}
del sample  # free the small sample, no longer needed

# train_identity is small — load normally
train_identity = pd.read_csv(r"C:\Users\krrishmalhan122\AlphaDefense\train_identity.csv")
print(f"Raw identity shape: {train_identity.shape}")

# train_transaction is large — read AND merge in chunks
print("STEP 2: Reading and merging in chunks...")
merged_chunks = []
chunk_num = 0
for chunk in pd.read_csv(
    r"C:\Users\krrishmalhan122\AlphaDefense\train_transaction.csv",
    dtype=dtype_map,
    chunksize=100000
):
    chunk_num += 1
    merged_piece = pd.merge(chunk, train_identity, on='TransactionID', how='left')
    merged_chunks.append(merged_piece)
    print(f"  Processed chunk {chunk_num}, rows so far: {sum(len(c) for c in merged_chunks):,}")

del train_identity  # free it, already used in every merge

df = pd.concat(merged_chunks, ignore_index=True)
del merged_chunks  # free the list of pieces, now combined into df
print(f"\nMerged & combined shape: {df.shape}")

# STEP 3: Sort chronologically — inplace avoids building a full copy
print("STEP 3: Sorting chronologically...")
df.sort_values('TransactionDT', inplace=True)
df.reset_index(drop=True, inplace=True)

# STEP 4: Missing value analysis
print("STEP 4: Analyzing missing values...")
missing_pct = (df.isnull().sum() / len(df)) * 100
cols_to_drop = missing_pct[missing_pct > 80].index.tolist()
print(f"Columns with >80% missing values ({len(cols_to_drop)} found)")

# STEP 5: Drop high-null columns — inplace avoids building a full copy
print("STEP 5: Dropping high-null columns...")
df.drop(columns=cols_to_drop, inplace=True)
print(f"Shape after dropping high-null features: {df.shape}")

# STEP 6: Save
print("STEP 6: Saving clean_data.csv...")
df.to_csv(r"C:\Users\krrishmalhan122\AlphaDefense\clean_data.csv", index=False)
print("\n[SUCCESS] Saved clean_data.csv. Ready for Script 8!")
