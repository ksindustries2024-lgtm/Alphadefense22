"""
AlphaDefense — Phase 1 EDA-4: Numerical Distributions / Multicollinearity (VIF)
================================================================================
Goal: IEEE-CIS has 292 anonymized 'V' columns with heavy, overlapping
multicollinearity and structurally correlated missingness. This script:

    1. Groups V-columns into 12 "blocks" by identical null-count (columns
       that go missing together were almost certainly engineered from the
       same underlying signal, so they get treated as one redundancy group).
    2. Fills missing values per-ProductCD-group median (falls back to 0 when
       a whole group is 100% missing for that column — structural absence,
       not a value to estimate).
    3. Computes VIF per column, *within its own block only* (not globally —
       292x292 VIF is both computationally unstable and analytically noisy;
       block-scoping matches how the missingness/redundancy actually groups).
    4. Within each block's high-VIF columns, sub-clusters by pairwise
       correlation (VIF alone says "this column is redundant with something
       in the block," not *which* column — clustering answers that).
    5. Within each cluster, keeps only the single column with the strongest
       |correlation| to isFraud (with a floor — a cluster where even the
       best member is near-zero gets dropped entirely, not token-kept).
    6. Exports the surviving feature set to CSV for the modeling phase.

Output: eda4_output.csv — 102 surviving V-columns + isFraud.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt#for better visualization of the output 
from statsmodels.stats.outliers_influence import variance_inflation_factor
import json

df=pd.read_csv(r"C:\Users\krrishmalhan122\AlphaDefense\clean_data.csv")
# Load only the V-columns + isFraud (memory-safe: don't reload the whole 394-col file if you already have df in memory from Script 7)
# If starting fresh in this script, specify dtype at read time like you learned in EDA-1 — don't skip that lesson here.

v_cols = [col for col in df.columns if col.startswith('V')]
print(f"Number of V-columns: {len(v_cols)}")
print(df[v_cols].dtypes)
v_null_counts = df[v_cols].isnull().sum().sort_values(ascending=False)
print(v_null_counts.head(20))
# Take the top one, say it's called 'V1' for example
top_missing_col = v_null_counts.index[0]
print(f"Top missing column: {top_missing_col}")

# Now check: does missingness in this column relate to ProductCD, same as EDA-3?
null_check=df.groupby('ProductCD')[["V277","V95",'V279','V167','V12','V53', 'V75','V169','V35','V220', 'V1','V281']].apply(lambda x: x.isnull().mean())
print(f"checking the null% with productCD which is:{null_check}")
# Group V-columns by identical null count — this IS the block boundary
null_counts_per_col = df[v_cols].isnull().sum()

# Group column names by their null count value
from collections import defaultdict
blocks_by_nullcount = defaultdict(list)
for col, count in null_counts_per_col.items():
    blocks_by_nullcount[count].append(col)

# Show block sizes — sorted by how many columns share that null count, biggest blocks first
block_summary = sorted(blocks_by_nullcount.items(), key=lambda x: -len(x[1]))
for null_count, cols in block_summary:
    print(f"Null count {null_count}: {len(cols)} columns -> {cols}")
null_rate=df[v_cols].isnull().sum().sum()#actually here first sum() gives sum for each v column then second sum() give for whole dataframe
print(f"Total null values in V-columns: {null_rate}")

def group_aware_impute(df, v_cols, group_col='ProductCD'):
    df_filled = df.copy()
    for col in v_cols:
        # Compute median per ProductCD group, ignoring NaNs automatically
        group_medians = df.groupby(group_col)[col].median()
        
        for group_value in df[group_col].unique():
            mask = df[group_col] == group_value
            median_val = group_medians[group_value]
            
            if pd.isna(median_val):
                # 100% missing in this group — no real median exists, structural absence
                fill_value = 0
            else:
                fill_value = median_val
            
            # Fill only the null rows within this specific group
            col_mask = mask & df[col].isnull()
            df_filled.loc[col_mask, col] = fill_value
    
    return df_filled
null_fill=group_aware_impute(df, v_cols, group_col='ProductCD') 
print(f"Null values after group-aware imputation: {null_fill[v_cols].isnull().sum()}and for the whole dataframe is:{null_fill[v_cols].isnull().sum().sum()}")
#Here we will actually build full list of v columns pair as per null count as blocks


RECOMPUTE_VIF = False  # ← flip this to False after the first successful run

if RECOMPUTE_VIF:
    vif_results = {}
    for null_count, cols in blocks_by_nullcount.items():
        block_df = null_fill[cols]
        block_array = block_df.values
        for i in range(len(block_df.columns)):
            vif_value = variance_inflation_factor(block_array, i)
            vif_results[block_df.columns[i]] = vif_value
            print(f"VIF for {block_df.columns[i]}: {vif_value}")
    with open(r"C:\Users\krrishmalhan122\AlphaDefense\vif_results.json", 'w') as f:
        json.dump(vif_results, f)
else:
    with open(r"C:\Users\krrishmalhan122\AlphaDefense\vif_results.json", 'r') as f:
        vif_results = json.load(f)   


def cluster_block(high_vif_cols, corr_matrix, threshold=0.8):
    clusters = []
    claimed = set()
    for col in high_vif_cols:
        if col in claimed:
            continue
        cluster = [col]
        claimed.add(col)
        for other_col in high_vif_cols:
            if other_col in claimed or other_col == col:
                continue
            if all(corr_matrix[other_col][member] >= threshold for member in cluster):
                cluster.append(other_col)
                claimed.add(other_col)
        clusters.append(cluster)
    return clusters

corr_matrix_target = null_fill.select_dtypes(include=['integer', 'float']).corr()['isFraud']

columns_to_keep = []   # ← created ONCE, before the loop. This is your FINAL answer,
                        #   collected piece by piece from all 12 blocks. It must survive
                        #   across every loop iteration, so it sits outside the loop.

for null_count, cols in blocks_by_nullcount.items():   # ← this loop already existed — runs once per block, 12 times total
    high_vif_cols = [col for col in cols if vif_results[col] > 10]
    low_vif_cols = [col for col in cols if vif_results[col] <= 10]
    print(f"Block {null_count}: {len(high_vif_cols)} high VIF, {len(low_vif_cols)} low VIF")

    # THE ACTUAL FIX: everything below this line used to sit OUTSIDE the loop.
    # Moving it INSIDE means it now runs fresh, once per block, instead of once total.

    block_corr = null_fill[high_vif_cols].corr()
    # ↑ correlation matrix for THIS block's high-VIF columns only — computed fresh
    #   every iteration, so block 1 gets its own matrix, block 2 gets its own, etc.
    #   This is what "corr_matrix" was missing entirely before — it never existed.

    choosen_cluster = cluster_block(high_vif_cols, block_corr, threshold=0.8)
    # ↑ THIS is the actual fix to the main bug. Before: called once, after the loop,
    #   using only the leftover last block's high_vif_cols. Now: called 12 times,
    #   once per block, each time using THAT block's own columns and THAT block's
    #   own correlation matrix. Every block now actually gets clustered.

    for cluster in choosen_cluster:
        best_col, best_score = None, -1
        for col in cluster:
            score = abs(corr_matrix_target[col])
            if score > best_score:
                best_score, best_col = score, col
        if best_score > 0.01:
            columns_to_keep.append(best_col)
    # ↑ your keep/drop logic — unchanged from what you already wrote and understood.
    #   Now runs once per block too, appending THIS block's winners into the SAME
    #   columns_to_keep list every time — so it grows across all 12 blocks instead
    #   of being overwritten.

    for col in low_vif_cols:
        if abs(corr_matrix_target[col]) > 0.01:
            columns_to_keep.append(col)
    # ↑ same idea — this block's low-VIF survivors get added to the same growing list.

print(f"Final columns to keep (length {len(columns_to_keep)}),smample: {columns_to_keep[:10]}")

print('V95' in columns_to_keep, 'V96' in columns_to_keep, 'V97' in columns_to_keep)
# Only AFTER all 12 blocks have run and columns_to_keep has everyone's survivors:
null_fill[columns_to_keep + ['isFraud', 'TransactionID']].to_csv(r"C:\Users\krrishmalhan122\AlphaDefense\eda4_output.csv", index=False)
print(f"Saved {len(columns_to_keep)} features + isFraud + TransactionID to {df}")
print('TransactionID' in null_fill.columns)
#for eda 5 merging we add transaction id as to merge eda3 and eda4 csv for eda5 csv

