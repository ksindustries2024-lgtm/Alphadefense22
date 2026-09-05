import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# STEP 1: Null% for each confounder column, split by ProductCD
# (replace this block with your actual df.groupby(...) call)
# ============================================================
df=pd.read_csv(r"C:\Users\krrishmalhan122\AlphaDefense\clean_data.csv")  # Example: load a sample of the dataset
null_perc_finding = df.groupby("ProductCD")[
    ['addr2', 'id_16', 'id_13', 'DeviceType', 'DeviceInfo']
].apply(lambda x: x.isnull().mean())

# ============================================================
# STEP 2: Fraud rate for each ProductCD
# ============================================================
fraud_rate_by_product = df.groupby('ProductCD')['isFraud'].apply(lambda x: x.mean())

# ============================================================
# STEP 3: Combine into one table, side by side
# ============================================================
null_perc_finding['fraud_rate'] = fraud_rate_by_product
print(null_perc_finding)

# sample size sanity check -- always check this before trusting a rate
print(df['ProductCD'].value_counts())

# ============================================================
# STEP 4: Dual-axis grouped bar chart
# fig = the whole canvas. ax1/ax2 = two chart areas sharing
# the same x-axis (ProductCD) but with independent y-scales.
# ============================================================
null_cols = ['addr2', 'id_16', 'id_13', 'DeviceType', 'DeviceInfo']

fig, ax1 = plt.subplots(figsize=(11, 6))

# draw the 5 null% columns as grouped bars onto ax1 (left y-axis, 0-1 scale)
null_perc_finding[null_cols].plot(kind='bar', ax=ax1, width=0.7)
ax1.set_ylabel('Null Rate (0-1)')
ax1.set_ylim(0, 1.05)
ax1.legend(loc='upper left', title='Null% columns')
ax1.set_xticklabels(null_perc_finding.index, rotation=0)

# ax2 = a second Axes, same x positions, but its OWN y-scale
ax2 = ax1.twinx()
x_pos = range(len(null_perc_finding))
ax2.plot(x_pos, null_perc_finding['fraud_rate'], color='black',
         marker='o', linewidth=2, label='fraud_rate')
ax2.set_ylabel('Fraud Rate (0-1)')
ax2.set_ylim(0, null_perc_finding['fraud_rate'].max() * 1.3)
ax2.legend(loc='upper right')

plt.title('Confounder Check: Null% (bars) vs Fraud Rate (line) by ProductCD')
plt.tight_layout()
plt.savefig('eda3_confounder_analysis.png')
plt.show()

# ============================================================
# STEP 5: Written conclusion -- log this in your notebook/report
# ============================================================
print("""
CONCLUSION: addr2, id_13, id_16, DeviceType, and DeviceInfo nullness rates
vary by ProductCD due to differences in each product type's data-collection
system, not due to any direct relationship with fraud. The direction of
missingness does not consistently track the direction of fraud risk across
categories -- e.g. ProductCD W has near-total missingness on id_16, id_13,
DeviceType, and DeviceInfo but the LOWEST fraud rate (0.020), while
ProductCD C has moderate missingness on these same fields but the HIGHEST
fraud rate (0.117). Fraud risk is driven by ProductCD itself (likely due to
differences in transaction type, verification requirements, or fraud
opportunity), not by these fields' missingness. These fields are confounded
proxies for ProductCD, not independent fraud signals. Note: ProductCD 'S'
has the smallest sample size (11,628 rows vs 33k-440k for others), so its
5.9% fraud rate estimate carries more uncertainty than C's or W's.
""")
