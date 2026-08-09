# ============================================================
# AlphaDefense — EDA-2: Target Distribution & Class Imbalance
# Author: Krrish Malhan
# GitHub: ksindustries2024-lgtm/Alphadefense22
# Phase 1: Exploratory Data Analysis
# ============================================================
# PURPOSE:
# Exploratory companion to Script 7/8. This file understands the
# shape of the target variable (isFraud) and derives the
# scale_pos_weight value handed to XGBoost in Phase 2, with the
# reasoning documented, not just the number.
#
# EDA-2 answers: "What does the target variable look like, and
#                 what does that imply for modeling?"
#
# NOTE: This assumes EDA-1 has already run and confirmed data
# integrity. It reloads and re-merges independently so it can be
# run standalone.
# ============================================================

import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 120)

print("=" * 70)
print("EDA-2: TARGET DISTRIBUTION & CLASS IMBALANCE ANALYSIS")
print("=" * 70)

train_transaction = pd.read_csv('train_transaction.csv')
train_identity = pd.read_csv('train_identity.csv')
df = pd.merge(train_transaction, train_identity, on='TransactionID', how='left')

fraud_counts = df['isFraud'].value_counts()
fraud_pct = (fraud_counts / len(df)) * 100

print("\n[Check 1] Raw class counts")
print(fraud_counts)
print("\n[Check 2] Class percentages")
print(fraud_pct.round(2))

neg = fraud_counts[0]
pos = fraud_counts[1]
scale_pos_weight = neg / pos

print(f"\n[Check 3] scale_pos_weight calculation")
print(f"Legitimate transactions (0): {neg:,}")
print(f"Fraud transactions (1):      {pos:,}")
print(f"scale_pos_weight = {neg:,} / {pos:,} = {scale_pos_weight:.2f}")

# --- The reasoning layer: why raw accuracy is misleading here ---
naive_accuracy = fraud_pct[0]
print(f"\n[Check 4] Why accuracy alone is a misleading metric here")
print(f"A model that predicts 'legitimate' for EVERY transaction, "
      f"with zero fraud-detection capability, achieves {naive_accuracy:.2f}% accuracy.")
print("That number looks excellent on paper and is completely useless in production —")
print("it catches 0% of fraud, which is the entire point of this system.")

print("\n[EDA-2 SUMMARY]")
print(f"""
isFraud is severely imbalanced: {fraud_pct[1]:.2f}% fraud vs {fraud_pct[0]:.2f}% legitimate.
A naive always-legitimate classifier scores {naive_accuracy:.2f}% accuracy while being
functionally worthless — this is why accuracy is not the evaluation metric for this
system (AUC-ROC / precision-recall / recall-at-fixed-FPR are used instead in Phase 2).

scale_pos_weight = {scale_pos_weight:.2f} is passed to XGBoost so that missing a single
fraud transaction during training is penalized ~{scale_pos_weight:.0f}x more heavily than
misclassifying a legitimate transaction. Mechanically, XGBoost multiplies the gradient
contribution of each positive-class (fraud) sample by this factor during training,
which shifts the model's decision boundary to actively avoid missing fraud cases,
rather than passively defaulting to the majority class.

Verdict: target distribution understood, scale_pos_weight derived and justified.
Ready to hand this value to Phase 2 (XGBoost training).
""")

print("=" * 70)
print("EDA-2 COMPLETE")
print("=" * 70)
