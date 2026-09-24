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

import json
from collections import defaultdict

import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor

DATA_PATH = r"C:\Users\krrishmalhan122\AlphaDefense\clean_data.csv"
VIF_CACHE_PATH = r"C:\Users\krrishmalhan122\AlphaDefense\vif_results.json"
OUTPUT_PATH = r"C:\Users\krrishmalhan122\AlphaDefense\eda4_output.csv"

RECOMPUTE_VIF = False  # False = load cached VIF from disk (fast). Flip to
                        # True only if the underlying data/imputation changes
                        # — a full recompute takes 5-10 minutes.


# ---------------------------------------------------------------------------
# STEP 1 — Load data and isolate the V-columns
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH)

v_cols = [col for col in df.columns if col.startswith('V')]
print(f"Number of V-columns: {len(v_cols)}")
print(df[v_cols].dtypes)

v_null_counts = df[v_cols].isnull().sum().sort_values(ascending=False)
print(v_null_counts.head(20))

top_missing_col = v_null_counts.index[0]
print(f"Top missing column: {top_missing_col}")

# Sanity check inherited from EDA-3: is missingness here explained by
# ProductCD the same way it was for the identity/device columns?
null_check = df.groupby('ProductCD')[
    ["V277", "V95", "V279", "V167", "V12", "V53", "V75", "V169", "V35", "V220", "V1", "V281"]
].apply(lambda x: x.isnull().mean())
print(f"checking the null% with productCD which is:{null_check}")


# ---------------------------------------------------------------------------
# STEP 2 — Group V-columns into blocks by identical null-count
# ---------------------------------------------------------------------------
# Columns that are missing in exactly the same rows almost certainly came
# from the same underlying Vesta feature-engineering process. Grouping by
# null-count is a cheap, reliable proxy for "these columns are related."
null_counts_per_col = df[v_cols].isnull().sum()

blocks_by_nullcount = defaultdict(list)
for col, count in null_counts_per_col.items():
    blocks_by_nullcount[count].append(col)

block_summary = sorted(blocks_by_nullcount.items(), key=lambda x: -len(x[1]))
for null_count, cols in block_summary:
    print(f"Null count {null_count}: {len(cols)} columns -> {cols}")

null_rate = df[v_cols].isnull().sum().sum()
print(f"Total null values in V-columns: {null_rate}")


# ---------------------------------------------------------------------------
# STEP 3 — Group-aware imputation
# ---------------------------------------------------------------------------
def group_aware_impute(df, v_cols, group_col='ProductCD'):
    """
    Fill each V-column's missing values using the median of its own
    ProductCD group — not a global median, since EDA-3 showed missingness
    itself is ProductCD-driven (different transaction types trigger
    different fields entirely).

    If a whole ProductCD group has zero non-null values for a column,
    there is no median to compute — that's structural absence (the field
    genuinely doesn't apply to that transaction type), so it's filled
    with 0 rather than left null or back-filled from other groups.
    """
    df_filled = df.copy()
    for col in v_cols:
        group_medians = df.groupby(group_col)[col].median()

        for group_value in df[group_col].unique():
            mask = df[group_col] == group_value
            median_val = group_medians[group_value]
            fill_value = 0 if pd.isna(median_val) else median_val

            col_mask = mask & df[col].isnull()
            df_filled.loc[col_mask, col] = fill_value

    return df_filled


null_fill = group_aware_impute(df, v_cols, group_col='ProductCD')
print(
    f"Null values after group-aware imputation: {null_fill[v_cols].isnull().sum()}"
    f"and for the whole dataframe is:{null_fill[v_cols].isnull().sum().sum()}"
)


# ---------------------------------------------------------------------------
# STEP 4 — VIF, computed block-scoped (not globally)
# ---------------------------------------------------------------------------
# Each column's VIF is computed using only the other columns in its own
# null-count block as context, not all 292 V-columns. Global VIF on this
# many correlated columns is numerically unstable and doesn't match how
# the redundancy actually clusters (block membership already IS the
# grouping signal from Step 2).
if RECOMPUTE_VIF:
    vif_results = {}
    for null_count, cols in blocks_by_nullcount.items():
        block_df = null_fill[cols]
        block_array = block_df.values
        for i in range(len(block_df.columns)):
            vif_value = variance_inflation_factor(block_array, i)
            vif_results[block_df.columns[i]] = vif_value
            print(f"VIF for {block_df.columns[i]}: {vif_value}")
    with open(VIF_CACHE_PATH, 'w') as f:
        json.dump(vif_results, f)
else:
    with open(VIF_CACHE_PATH, 'r') as f:
        vif_results = json.load(f)


# ---------------------------------------------------------------------------
# STEP 5 — Sub-cluster each block's high-VIF columns by pairwise correlation
# ---------------------------------------------------------------------------
def cluster_block(high_vif_cols, corr_matrix, threshold=0.8):
    """
    VIF > 10 only says "this column is redundant with SOMETHING in its
    block" — not which one, and not whether all high-VIF columns in a
    block form a single group. This clusters them properly.

    Critical rule: a candidate joins an existing cluster only if it
    correlates >= threshold with EVERY current member of that cluster
    (not just one). A weaker "matches any member" rule breaks under
    non-transitive correlation — e.g. A-B=0.85, B-C=0.85, A-C=0.60 would
    wrongly chain A and C into one cluster via B, even though A and C
    aren't actually redundant with each other. Requiring agreement with
    ALL members prevents that chaining trap while still correctly forming
    genuine all-mutual clusters. Columns that don't cluster with anyone
    naturally end up as their own size-1 cluster — no special case needed.
    """
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


# Correlation of every numeric column against isFraud, computed ONCE — this
# value doesn't change per block (unlike block_corr below, which is
# block-specific), so it lives outside the loop.
corr_matrix_target = null_fill.select_dtypes(include=['integer', 'float']).corr()['isFraud']


# ---------------------------------------------------------------------------
# STEP 6 — Per block: split by VIF, cluster, keep the best of each cluster
# ---------------------------------------------------------------------------
columns_to_keep = []  # Shared accumulator across all 12 blocks.

for null_count, cols in blocks_by_nullcount.items():
    high_vif_cols = [col for col in cols if vif_results[col] > 10]
    low_vif_cols = [col for col in cols if vif_results[col] <= 10]
    print(f"Block {null_count}: {len(high_vif_cols)} high VIF, {len(low_vif_cols)} low VIF")

    # Pairwise correlation matrix for THIS block's high-VIF columns only —
    # recomputed fresh every iteration, matching the block-scoped VIF design.
    block_corr = null_fill[high_vif_cols].corr()
    clusters = cluster_block(high_vif_cols, block_corr, threshold=0.8)

    # Keep/drop rule: within each cluster, keep the single strongest
    # |correlation with isFraud|. If even the best member is near-zero
    # (<= 0.01), drop the whole cluster — a token survivor with no real
    # signal isn't worth the feature slot.
    for cluster in clusters:
        best_col, best_score = None, -1
        for col in cluster:
            score = abs(corr_matrix_target[col])
            if score > best_score:
                best_score, best_col = score, col
        if best_score > 0.01:
            columns_to_keep.append(best_col)

    # Low-VIF columns skip clustering entirely — no redundancy to resolve,
    # just check them against the same isFraud-signal floor individually.
    for col in low_vif_cols:
        if abs(corr_matrix_target[col]) > 0.01:
            columns_to_keep.append(col)

print(f"Final columns to keep (length {len(columns_to_keep)}), sample: {columns_to_keep[:10]}")

# Verification: V95/V96/V97 have hand-checked correlation with isFraud of
# roughly -0.004 to -0.005 (below the 0.01 floor) despite huge pairwise VIF
# with each other — they should NOT survive. Confirms keep/drop logic works
# on a known case, not just "the code ran without erroring."
print('V95' in columns_to_keep, 'V96' in columns_to_keep, 'V97' in columns_to_keep)

# NOTE (documented limitation, not a bug): clustering here is block-wise
# only, never cross-block, since VIF itself was only ever computed
# within-block. A genuine but coincidental cross-block correlation would
# not be caught by this method. Full 292x292 cross-block correlation was
# judged intractable/noisy relative to the benefit for this phase.

null_fill[columns_to_keep + ['isFraud']].to_csv(OUTPUT_PATH, index=False)
print(f"Saved {len(columns_to_keep)} features + isFraud to {OUTPUT_PATH}")
