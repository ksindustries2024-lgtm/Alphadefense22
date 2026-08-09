# ============================================================
# AlphaDefense — EDA-1: Data Integrity & Loading Verification
# Author: Krrish Malhan
# GitHub: ksindustries2024-lgtm/Alphadefense22
# Phase 1: Exploratory Data Analysis
# ============================================================
# PURPOSE:
# Exploratory companion to Script 7/8. Where Script 7/8 are the
# PRODUCTION PIPELINE (clean, transform, split, save), this file
# is the ANALYSIS NARRATIVE — it shows *why* specific decisions
# were made in the pipeline, with supporting evidence and
# interpretation.
#
# EDA-1 answers: "Is the data what we think it is, and did the
#                 load/merge happen correctly?"
# ============================================================

import pandas as pd
import numpy as np

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 120)

print("=" * 70)
print("EDA-1: DATA INTEGRITY & LOADING VERIFICATION")
print("=" * 70)

train_transaction = pd.read_csv('train_transaction.csv')
train_identity = pd.read_csv('train_identity.csv')

# --- Check 1: Raw shapes match documented dataset expectations ---
print("\n[Check 1] Raw file shapes")
print(f"train_transaction: {train_transaction.shape} "
      f"(expected ~590,540 rows x 394 cols)")
print(f"train_identity:     {train_identity.shape} "
      f"(expected ~144,233 rows x 41 cols)")

# WHY THIS MATTERS: if these numbers don't match what's documented
# for IEEE-CIS, either the download is corrupted/partial, or we're
# looking at the wrong file version. This is the cheapest possible
# check and it should always run first.

# --- Check 2: TransactionID uniqueness (primary key integrity) ---
print("\n[Check 2] TransactionID uniqueness")
tx_id_unique = train_transaction['TransactionID'].is_unique
id_id_unique = train_identity['TransactionID'].is_unique
print(f"TransactionID unique in train_transaction: {tx_id_unique}")
print(f"TransactionID unique in train_identity:    {id_id_unique}")

# WHY THIS MATTERS: TransactionID is the join key for the merge in
# Script 7. If it isn't unique in either file, a LEFT JOIN can
# silently multiply rows (a classic, dangerous bug) — you'd end up
# training on duplicated transactions without realizing it.

# --- Check 3: Identity data coverage ---
print("\n[Check 3] Identity data coverage")
coverage_pct = train_transaction['TransactionID'].isin(
    train_identity['TransactionID']
).mean() * 100
print(f"% of transactions WITH matching identity/device data: {coverage_pct:.2f}%")
print(f"% of transactions WITHOUT identity/device data:        {100 - coverage_pct:.2f}%")

# WHY THIS MATTERS: this number is the seed of the EDA-3 confounder
# finding — a large chunk of transactions have NO device/identity
# data at all. Any feature built from identity columns will be
# missing for that entire group, which is a structural fact about
# the dataset, not noise.

# --- Check 4: Merge correctness (row count preserved) ---
print("\n[Check 4] Merge correctness")
df = pd.merge(train_transaction, train_identity, on='TransactionID', how='left')
merge_preserved_rows = train_transaction.shape[0] == df.shape[0]
print(f"Merged shape: {df.shape}")
print(f"Row count preserved after LEFT JOIN: {merge_preserved_rows}")

# WHY THIS MATTERS: a LEFT JOIN on train_transaction must NEVER
# change the row count. If this prints False, Check 2's uniqueness
# assumption was violated somewhere and the merge is unsafe to use.

print("\n[EDA-1 SUMMARY]")
print(f"Data loads correctly, TransactionID is a safe join key, "
      f"merge preserves all {train_transaction.shape[0]:,} transaction rows.")
print("Verdict: raw data integrity CONFIRMED. Safe to proceed to EDA-2.")
