"""
AlphaDefense — Phase 1, EDA-6: Correlation & Leakage Audit
Input:  eda5_output.csv (590,540 rows x 166 cols — EDA-4's 102 surviving 
        V-columns + EDA-5's one-hot/target-encoded categoricals, already merged)
Output: eda6_output.csv (590,540 rows x 160 cols — 6 redundant columns dropped)

Four checks performed:
1. Integrity check — confirmed eda5_output.csv is already merged (no separate
   merge step needed); shape and column list verified before proceeding.
2. Global correlation-with-target scan — every feature's individual correlation
   with isFraud, to catch leakage (a feature correlating suspiciously high 
   because it secretly encodes post-fraud information, not real signal).
   Max |corr| found: 0.287 (V257, card1_encoded) — well under the 0.5-0.6 
   leakage-suspect threshold. No leakage found; top correlations interrogated
   and confirmed legitimate (e.g. card1_encoded's correlation reflects real 
   card-reuse-in-fraud behavior, not a leak).
3. Cross-column correlation matrix — every feature vs every other feature 
   (not vs target), closing the gap EDA-4 explicitly left open (VIF there was 
   block-scoped only, never cross-block). Threshold: |corr| >= 0.9.
   Same-original-column one-hot pairs (e.g. card6_credit/card6_debit) ignored 
   as structurally-forced artifacts of one-hot encoding, not real redundancy.
   Genuine cross-pipeline near-duplicates got an actual drop decision:
   interpretability tie-break when |corr(isFraud)| was too close to call
   (V1 vs ProductCD_W, V41 vs ProductCD_S), else kept higher |corr(isFraud)|.
4. Post-drop leakage re-verification — confirmed dropping unrelated columns 
   cannot retroactively change how a surviving encoded column (e.g. 
   card1_encoded) was computed, since each encoding used only its own source 
   column + isFraud as inputs, never another feature column.

Final drop list (6 columns): V1, id_28_Found, id_15_Found, V41, 
id_29_NotFound, id_16_NotFound
Final shape: (590540, 160)
"""


import pandas as pd
import numpy as np
eda5_df = pd.read_csv(r"C:\Users\krrishmalhan122\AlphaDefense\eda5_output.csv")
print(f"EDA5 output shape: {eda5_df.shape}")
print(eda5_df.columns.tolist())
correlation=eda5_df.corr()['isFraud'].sort_values(ascending=False)
print(correlation.head(10))
print(correlation.tail(10))

corr_matrix = eda5_df.drop(columns=['isFraud']).corr()

upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
high_corr_pairs = upper.stack()
high_corr_pairs = high_corr_pairs[abs(high_corr_pairs) > 0.8].sort_values(ascending=False)
print(high_corr_pairs)
print(correlation[['id_29_Found', 'id_28_Found', 'id_15_Found', 'id_16_Found', 'V72', 'V1','ProductCD_S', 'ProductCD_W', 'V41','id_29_NotFound','id_28_New','id_15_New','id_16_NotFound']])
new_correlation=eda5_df.drop(columns=['V1', 'id_28_Found', 'id_15_Found', 'V41', 'id_29_NotFound', 'id_16_NotFound'])
print(new_correlation.shape)
new_correlation.to_csv(r"C:\Users\krrishmalhan122\AlphaDefense\eda6_output.csv", index=False)
