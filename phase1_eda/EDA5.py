"""
EDA-5 — Categorical & High-Cardinality Encoding
AlphaDefense | IEEE-CIS Fraud Detection

Loads EDA-3 output (raw categorical columns intact) + EDA-4 output
(VIF-filtered numeric features), encodes all categorical columns
leak-free, merges everything into the final EDA-5 feature set.
"""

import pandas as pd
df=pd.read_csv(r"C:\Users\krrishmalhan122\AlphaDefense\clean_data.csv")
df = df.sort_values('TransactionDT').reset_index(drop=True)  # mandatory — confirm this runs before any encoding
# Columns you're checking for
target_cols = ['ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6',
               'addr1', 'addr2', 'P_emaildomain', 'R_emaildomain',
               'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9']

# Which of these actually exist in eda3_output.csv?
present = [col for col in target_cols if col in df.columns.tolist()]
missing = [col for col in target_cols if col not in df.columns.tolist()]

print("Present in eda3_output.csv:", present)
print("Missing from eda3_output.csv:", missing)

#autodetects all the columns with dtype as object(string) as list as convert series into list by tolist()
auto_categorical=df.select_dtypes(include=['object']).columns.tolist()

#columns which are actually categorical but actually numeric
known_categorical_but_numeric=['card1','card2','card3','card5','addr1','addr2']

#considering all the columns which are categorical
all_categorical_cols=list(set(auto_categorical+known_categorical_but_numeric))

print(f"Total categorical columns found: {len(all_categorical_cols)}")
print("Categorical columns:", all_categorical_cols)

#finding uniques numbers of the categories exist in each columns
for col in all_categorical_cols:
   print(col,df[col].nunique())

#making a list of columns where one_hot encoding will be applied as thershold set as less or eqaul to 15
onehot_cols=[col for col in all_categorical_cols if df[col].nunique()<=15]

#making a list of columns where label encoding will be applied as thershold set as greater than 15
target_enc_cols = [col for col in all_categorical_cols if df[col].nunique() > 15]

print("One-hot bucket:", onehot_cols)
print("Target encoding bucket:", target_enc_cols)

# Step B: one-hot encoding — pandas has this built in, one line, whole bucket at once
df_onehot = pd.get_dummies(df[onehot_cols], columns=onehot_cols)

#stepc:here use cumsum-total fraud values as those only contribute
K = 10  # smoothing strength — you can tune this later

GLOBAL_FRAUD_RATE = 0.0351
for col in target_enc_cols:
    fraud_counts = df.groupby(col)['isFraud'].cumsum() - df['isFraud']
    total_counts = df.groupby(col).cumcount()
    
    smoothed = (fraud_counts + K * GLOBAL_FRAUD_RATE) / (total_counts + K)
    df[f'{col}_encoded'] = smoothed.fillna(GLOBAL_FRAUD_RATE)
# Step 4: check the result
print(df[['card2', 'isFraud', 'card2_encoded']].head(10))    

#step5:checking  for all the columns like proper considering all repeated more than once
for col in target_enc_cols:
    repeat_val = df[col].value_counts()
    repeat_val = repeat_val[repeat_val > 3]
    if len(repeat_val) == 0:
        print(f"{col}: no value repeats more than 3 times — skip")
        continue
    sample_val = repeat_val.index[0]
    print(f"\n--- {col} (sample value: {sample_val}) ---")
    print(df[df[col] == sample_val][[col, 'isFraud', f'{col}_encoded']].head(10))

fraud_rows = df[df['isFraud'] == 1]
print(fraud_rows[['card1', 'isFraud', 'card1_encoded']].head(10))    

eda4_df = pd.read_csv(r"C:\Users\krrishmalhan122\AlphaDefense\eda4_output.csv")

target_encoded_cols = [f'{col}_encoded' for col in target_enc_cols]
df_target_encoded = df[['TransactionID'] + target_encoded_cols]
df_onehot_with_id = pd.concat([df[['TransactionID']], df_onehot], axis=1)

df_final = eda4_df.merge(df_target_encoded, on='TransactionID', how='left')
df_final = df_final.merge(df_onehot_with_id, on='TransactionID', how='left')

print("NaN count:", df_final.isna().sum().sum())
print("Row count:", len(df_final))
print("Columns:", df_final.shape[1])
print(df['TransactionID'].isna().sum())      # should be 0
print(df['TransactionID'].duplicated().sum()) # should be 0 — each transaction appears once

# Step 1: drop original raw categorical columns (keep only their _encoded / one-hot versions)
df_final = df_final.drop(columns=[c for c in all_categorical_cols if c in df_final.columns])

# Step 2: drop TransactionID — only needed it for the merge, not as a model feature
df_final = df_final.drop(columns=['TransactionID'])

# Step 3: export
df_final.to_csv(r"C:\Users\krrishmalhan122\AlphaDefense\eda5_output.csv", index=False)

print("Final shape:", df_final.shape)
print("Final columns:", df_final.columns.tolist())

print(f"Your onehot_cols count:, {len(onehot_cols)}")
print(f"Your target_enc_cols count:, {len(target_enc_cols)}")
