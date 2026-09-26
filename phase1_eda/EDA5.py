"""
EDA-5 — Categorical & High-Cardinality Encoding
AlphaDefense | IEEE-CIS Fraud Detection

Loads EDA-3 output (raw categorical columns intact) + EDA-4 output
(VIF-filtered numeric features), encodes all categorical columns
leak-free, merges everything into the final EDA-5 feature set.
"""

import pandas as pd

GLOBAL_FRAUD_RATE = 0.0351   # locked overall fraud rate from EDA-7
K = 10                        # smoothing strength

EDA3_PATH = 'eda3_output.csv'
EDA4_PATH = 'eda4_output.csv'
OUTPUT_PATH = 'eda5_output.csv'

# ---------------------------------------------------------------
# Step 1: Load EDA-3 output, sort by time (mandatory for leak-free encoding)
# ---------------------------------------------------------------
df = pd.read_csv(EDA3_PATH)
df = df.sort_values('TransactionDT').reset_index(drop=True)

# ---------------------------------------------------------------
# Step 2: Detect categorical columns — auto (dtype) + known numeric-but-categorical
# ---------------------------------------------------------------
object_dtype_cols = df.select_dtypes(include='object').columns.tolist()
numeric_id_cols = ['card1', 'card2', 'card3', 'card5', 'addr1', 'addr2']
categorical_cols = list(set(object_dtype_cols + numeric_id_cols))

print(f"Total categorical columns found: {len(categorical_cols)}")

# ---------------------------------------------------------------
# Step 3: Bucket by cardinality threshold (15)
# ---------------------------------------------------------------
onehot_cols = [col for col in categorical_cols if df[col].nunique() <= 15]
target_enc_cols = [col for col in categorical_cols if df[col].nunique() > 15]

print("One-hot bucket:", onehot_cols)
print("Target encoding bucket:", target_enc_cols)

# ---------------------------------------------------------------
# Step 4: One-hot encode low-cardinality columns
# ---------------------------------------------------------------
df_onehot = pd.get_dummies(df[onehot_cols], columns=onehot_cols)

# ---------------------------------------------------------------
# Step 5: Smoothed, leak-free (time-respecting, leave-one-out) target encoding
#   fraud_counts / total_counts = fraud history strictly BEFORE this row
#   smoothing blends toward GLOBAL_FRAUD_RATE when history is thin
# ---------------------------------------------------------------
for col in target_enc_cols:
    fraud_counts = df.groupby(col)['isFraud'].cumsum() - df['isFraud']
    total_counts = df.groupby(col).cumcount()
    df[f'{col}_encoded'] = (fraud_counts + K * GLOBAL_FRAUD_RATE) / (total_counts + K)

target_encoded_cols = [f'{col}_encoded' for col in target_enc_cols]

# ---------------------------------------------------------------
# Step 6: Merge onto EDA-4's VIF-filtered numeric base, via TransactionID
#   (position-based concat is unsafe — row order differs between files)
# ---------------------------------------------------------------
eda4_df = pd.read_csv(EDA4_PATH)

df_target_encoded = df[['TransactionID'] + target_encoded_cols]
df_onehot_with_id = pd.concat([df[['TransactionID']], df_onehot], axis=1)

df_final = eda4_df.merge(df_target_encoded, on='TransactionID', how='left')
df_final = df_final.merge(df_onehot_with_id, on='TransactionID', how='left')

# ---------------------------------------------------------------
# Step 7: Drop raw categorical columns and the merge key (not model features)
# ---------------------------------------------------------------
df_final = df_final.drop(columns=[c for c in categorical_cols if c in df_final.columns])
df_final = df_final.drop(columns=['TransactionID'])

# ---------------------------------------------------------------
# Step 8: Verification (must pass before export is trusted)
# ---------------------------------------------------------------
print("NaN count:", df_final.isna().sum().sum())
print("Row count:", len(df_final), "| Expected: 590540")
print("Final shape:", df_final.shape)

# ---------------------------------------------------------------
# Step 9: Export
# ---------------------------------------------------------------
df_final.to_csv(OUTPUT_PATH, index=False)
print(f"Saved {df_final.shape[1]} columns to {OUTPUT_PATH}")
