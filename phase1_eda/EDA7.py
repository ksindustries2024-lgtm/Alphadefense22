"""
============================================================
AlphaDefense v2.0 — Script 8
Leakage-Free Preprocessing, Chronological Split & Scaling
============================================================

Purpose
-------
Takes the cleaned, merged transaction data (output of Script 7) and produces
model-ready train/test matrices for XGBoost, while enforcing three hard
constraints throughout every step:

  1. Chronological split, not random — the test set must simulate "the
     future," since a fraud model in production only ever sees the past
     at prediction time. A random shuffle split would let the model learn
     from transactions that happen chronologically after some test rows,
     inflating validation metrics with information a production model
     would never actually have.

  2. Zero test-set leakage into any fitted parameter — encoders, imputation
     medians, the scaler, and even the scale_pos_weight ratio for XGBoost
     are all fit/computed on the TRAINING split only, then applied to test.
     This holds even for a single aggregate statistic like scale_pos_weight,
     where the practical numeric impact of leaking is small — the point is
     enforcing the discipline uniformly, since not every leak elsewhere in
     a pipeline will be this forgiving.

  3. Every transformation applied to train is reproducible on test using
     ONLY parameters learned from train (fit_transform on train,
     transform-only on test) — this is what "leakage-free" means in
     practice, step by step, not just at the split.

Output
------
X_train.csv, X_test.csv, y_train.csv, y_test.csv — scaled, encoded,
imputed, leakage-free matrices ready for XGBoost training with a
dynamically computed scale_pos_weight for class imbalance.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, StandardScaler


# ============================================================
# STEP 1 — Load Script 7's output
# ============================================================
# We load the already-cleaned/merged file, not the raw Kaggle transaction
# file — Script 7 already handled merging + initial cleaning, so re-loading
# raw data here would undo that work and risk reintroducing dirty rows.
print("STEP 1: Loading merged clean_data.csv...")
df = pd.read_csv('clean_data.csv')
print(f"Loaded dataset shape: {df.shape}")

# Re-confirm chronological order defensively (idempotent if already sorted
# by Script 7) — TransactionDT is the raw timestamp offset used purely to
# establish real-world time order, nothing else.
df = df.sort_values('TransactionDT').reset_index(drop=True)


# ============================================================
# STEP 2 — Isolate target and features
# ============================================================
# isFraud is the target vector — what the model predicts.
#
# TransactionID is dropped because it's a serial number with zero causal
# relationship to fraud — a tree model given raw sequential IDs risks
# overfitting on their ordering, learning nothing generalizable.
#
# TransactionDT is dropped AFTER being used to sort — once it has done its
# one job (chronological ordering), keeping it as a raw feature would let
# the model key off "how late in the dataset's timeline is this row,"
# which doesn't generalize to real production behavior the way genuine
# transaction-pattern features do.
y = df['isFraud']
X = df.drop(columns=['isFraud', 'TransactionID', 'TransactionDT']).copy()


# ============================================================
# STEP 3 — Chronological (time-based) train/test split
# ============================================================
# No shuffling, no randomness. Positional (.iloc) 80/20 cutoff on data
# already sorted by TransactionDT: the first 80% of rows chronologically
# become train, the last 20% become test. This directly simulates the
# real production constraint — predict the present using only the past.
print("\nSTEP 3: Performing 80/20 Chronological Split...")
split_idx = int(len(X) * 0.8)

X_train = X.iloc[:split_idx].copy()
X_test  = X.iloc[split_idx:].copy()
y_train = y.iloc[:split_idx].copy()
y_test  = y.iloc[split_idx:].copy()

print(f"Training set rows : {X_train.shape[0]:,} (fraud: {y_train.mean()*100:.2f}%)")
print(f"Test set rows     : {X_test.shape[0]:,} (fraud: {y_test.mean()*100:.2f}%)")
# Verified result: train 472,432 rows @ 3.51% fraud, test 118,108 rows @
# 3.44% fraud. A 0.07pp gap — fraud prevalence is stable across the two
# time windows, a property of the raw labels checked before any model
# exists. This is the fair-comparison sanity check EDA-7 exists to run.


# ============================================================
# STEP 4 — Classify column types
# ============================================================
# Numeric and categorical columns need different treatment downstream
# (median imputation vs 'missing'-placeholder + encoding), so we split
# them explicitly rather than assuming dtypes are already correct.
num_cols = X_train.select_dtypes(include=['int64', 'float64']).columns.tolist()
cat_cols = X_train.select_dtypes(include=['object']).columns.tolist()
print(f"\nIdentified {len(num_cols)} Numeric features and {len(cat_cols)} Categorical features.")


# ============================================================
# STEP 5 — Categorical imputation (placeholder, not encoding yet)
# ============================================================
# NaN values are filled with the literal string 'missing' before encoding,
# because OrdinalEncoder cannot interpret NaN directly — it needs an actual
# category label to assign a numeric code to. Treating "missing" as its own
# category (rather than silently dropping or median-filling it) preserves
# the information that a value was absent, which can itself be predictive.
print("\nSTEP 5: Imputing Categorical Columns with 'missing' placeholder...")
X_train[cat_cols] = X_train[cat_cols].fillna('missing')
X_test[cat_cols]  = X_test[cat_cols].fillna('missing')


# ============================================================
# STEP 6 — Ordinal encoding (fit on train only)
# ============================================================
# OrdinalEncoder converts category strings into integer codes. It is fit
# ONLY on X_train — fitting on the full dataset (or on test) would leak
# knowledge of which categories exist in the test set into a parameter
# used during training.
#
# unknown_value=-1 means any category appearing in test/production that
# was never seen during training gets safely mapped to -1 instead of
# crashing the pipeline — critical for a real-world deployed system where
# genuinely novel category values will eventually show up.
#
# Known limitation (Problem A, distinct from any leakage concern): ordinal
# encoding imposes an artificial numeric order on categories that may have
# no real ordinal relationship (e.g. ProductCD W < C < H < R < S has no
# real-world meaning). XGBoost trees can still work around this reasonably
# well since they split on arbitrary thresholds across multiple splits,
# but it remains an imperfection of this encoding choice worth knowing.
print("Encoding Categorical features using OrdinalEncoder with Unknown fallback...")
encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

X_train[cat_cols] = encoder.fit_transform(X_train[cat_cols])
X_test[cat_cols]  = encoder.transform(X_test[cat_cols])


# ============================================================
# STEP 7 — Numeric imputation (train-only medians)
# ============================================================
# Missing numeric values are filled with the TRAINING set's median only.
# Using test-set values (or the full dataset) to compute the median used
# to fill test rows would leak test-set distribution information into
# what should be an unseen evaluation set.
print("\nSTEP 7: Imputing Numeric Columns using training-set Medians only...")
train_medians = X_train[num_cols].median()

X_train[num_cols] = X_train[num_cols].fillna(train_medians)
X_test[num_cols]  = X_test[num_cols].fillna(train_medians)


# ============================================================
# STEP 8 — Standard scaling (fit on train only)
# ============================================================
# StandardScaler is fit on X_train only, then applied to both train and
# test — same leakage-prevention logic as Steps 6 and 7.
#
# Worth naming explicitly: this scales ALL columns, including the ordinal-
# encoded categorical columns from Step 6. Scaling those is harmless but
# unnecessary for XGBoost specifically — StandardScaler is a strictly
# monotonic linear transform (subtract mean, divide by std), so it can
# never change the relative ORDER of values in a column. Since a decision
# tree split only ever asks "is this value above or below threshold T,"
# and relative order is fully preserved, XGBoost finds the exact same
# split boundaries whether these columns are scaled or not. It neither
# helps nor hurts tree-based model performance here — pure inert compute.
# (It would matter more for a linear or distance-based model, where the
# encoded numbers' magnitude is treated as meaningful.)
print("Standard Scaling features...")
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)

X_test_scaled = scaler.transform(X_test)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)


# ============================================================
# STEP 9 — scale_pos_weight for XGBoost class imbalance
# ============================================================
# Computed from y_train ONLY — this ratio feeds directly into XGBoost's
# loss function, controlling how much more heavily a missed fraud case is
# penalized relative to a false alarm. Computing it from the full dataset
# (train+test combined) would let test-set fraud counts influence a value
# that shapes how the model trains — the same category of leakage as a
# random split, just at the scale of a single aggregate statistic instead
# of entire feature rows. In this specific case the numeric impact is
# small (~27.46 train-only vs ~27.58 if computed on the full set) — but
# the discipline of computing every fitted parameter from train alone,
# with zero exceptions, is what protects against larger leaks elsewhere
# in the pipeline that would NOT be this forgiving.
neg_cases = (y_train == 0).sum()
pos_cases = (y_train == 1).sum()
scale_pos_weight = round(neg_cases / pos_cases, 2)
print(f"\nCalculated scale_pos_weight for XGBoost: {scale_pos_weight}")


# ============================================================
# STEP 10 — Save leakage-free matrices
# ============================================================
print("\nSTEP 10: Saving final leakage-free matrices to CSV...")
X_train_scaled.to_csv('X_train.csv', index=False)
X_test_scaled.to_csv('X_test.csv', index=False)
y_train.to_csv('y_train.csv', index=False)
y_test.to_csv('y_test.csv', index=False)

print("\n[SUCCESS] Preprocessing Pipeline complete! Files saved:")
print("→ X_train.csv, X_test.csv, y_train.csv, y_test.csv")
print("These files are 100% safe, leakage-free, chronological, and ready for model training!")
