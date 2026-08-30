# ============================================================
# AlphaDefense — Script 8 (UPDATED & CORRECTED)
# Topic: Leakage-Free Preprocessing, Chronological Split & Scaling
# ============================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

# STEP 1: Load the actual output of Script 7 (No reloading of raw transaction file!)
print("STEP 1: Loading merged clean_data.csv...")
df = pd.read_csv('clean_data.csv')
print(f"Loaded dataset shape: {df.shape}")

# Double check that the data is sorted chronologically
df = df.sort_values('TransactionDT').reset_index(drop=True)

# STEP 2: Isolate targets and features, dropping TransactionID and raw timestamps
# 'isFraud' is our target vector.
# 'TransactionID' is a serial number (useless for learning patterns).
# 'TransactionDT' is a raw timestamp offset which we used to sort/split chronologically.
# We drop both to prevent decision trees from overfitting on sequential numbers!
y = df['isFraud']
X = df.drop(columns=['isFraud', 'TransactionID', 'TransactionDT']).copy()

# STEP 3: Chronological (Time-Based) Split first (NO SHUFFLING, NO TIME TRAVEL!)
print("\nSTEP 3: Performing 80/20 Chronological Split...")
split_idx = int(len(X) * 0.8)

X_train = X.iloc[:split_idx].copy()
X_test  = X.iloc[split_idx:].copy()
y_train = y.iloc[:split_idx].copy()
y_test  = y.iloc[split_idx:].copy()

print(f"Training set rows : {X_train.shape[0]:,} (fraud: {y_train.mean()*100:.2f}%)")
print(f"Test set rows     : {X_test.shape[0]:,} ( fraud: {y_test.mean()*100:.2f}%)")

# STEP 4: Classify Column Types to prevent Ordinal/Median math errors
num_cols = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
cat_cols = X_train.select_dtypes(include=['object']).columns.tolist()
print(f"\nIdentified {len(num_cols)} Numeric features and {len(cat_cols)} Categorical features.")

# STEP 5: Safe Missing Categorical Imputation (Filling with a string placeholder first)
print("\nSTEP 5: Imputing Categorical Columns with 'missing' placeholder...")
X_train[cat_cols] = X_train[cat_cols].fillna('missing')
X_test[cat_cols]  = X_test[cat_cols].fillna('missing')

# STEP 6: Fit Encoders ONLY on Train, Transform BOTH (Secure Fallback Setup)
print("Encoding Categorical features using OrdinalEncoder with Unknown fallback...")
# Any category seen in the test set/production that wasn't in X_train becomes -1. No crashes!
encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

X_train[cat_cols] = encoder.fit_transform(X_train[cat_cols])
X_test[cat_cols]  = encoder.transform(X_test[cat_cols])

# STEP 7: Safe Numerical Imputation using Training set Median (No test leakage!)
print("\nSTEP 7: Imputing Numeric Columns using training-set Medians only...")
train_medians = X_train[num_cols].median()

X_train[num_cols] = X_train[num_cols].fillna(train_medians)
X_test[num_cols]  = X_test[num_cols].fillna(train_medians) # Imputing test set with train parameters

# STEP 8: Safe Scaling using Training set Mean/Std (No test leakage!)
print("Standard Scaling features...")
scaler = StandardScaler()

# fit_transform ONLY on training features
X_train_scaled = scaler.fit_transform(X_train)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)

# transform ONLY on test features (Unseen parameters)
X_test_scaled = scaler.transform(X_test)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)

# STEP 9: Calculate scale_pos_weight dynamically from training split
neg_cases = (y_train == 0).sum()
pos_cases = (y_train == 1).sum()
scale_pos_weight = round(neg_cases / pos_cases, 2)
print(f"\nCalculated scale_pos_weight for XGBoost: {scale_pos_weight}")

# STEP 10: Save clean, leakage-free matrices to CSV
print("\nSTEP 10: Saving final leakage-free matrices to CSV...")
X_train_scaled.to_csv('X_train.csv', index=False)
X_test_scaled.to_csv('X_test.csv', index=False)
y_train.to_csv('y_train.csv', index=False)
y_test.to_csv('y_test.csv', index=False)

print("\n[SUCCESS] Preprocessing Pipeline complete! Files saved:")
print("→ X_train.csv, X_test.csv, y_train.csv, y_test.csv")
print("These files are 100% safe, leakage-free, chronological, and ready for model training!")
