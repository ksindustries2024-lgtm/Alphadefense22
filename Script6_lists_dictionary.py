# ============================================================
# script6_lists_dicts.py — Lists & Dictionaries for AlphaDefense
# Topic: Lists, Dictionaries, List of Dictionaries
# Project: AlphaDefense — Quantitative Fraud Detection System
# ============================================================
 
# ─────────────────────────────────────────────
# CONCEPT 1: LIST
# ─────────────────────────────────────────────
# List = ordered collection of values under one variable
# Use karo jab: ek cheez ki series chahiye — amounts over time,
# f1_scores across models, transactions over a week/month/year
# Order matters — index se access hota hai (0 se shuru)
# Duplicates allowed
 
# ─────────────────────────────────────────────
# CONCEPT 2: for loop with list — jo main galat samjha tha
# ─────────────────────────────────────────────
# GALAT soch: for i in list → i = index (increment hota hai)
# SAHI soch:  for i in list → i = VALUE directly, ek ek karke
# i = i+1 likhne ki zaroorat NAHI — for loop khud handle karta hai
# Agar index chahiye: for i in range(len(list)) use karo
# Agar value chahiye: for i in list use karo — i IS the value
 
# ─────────────────────────────────────────────
# CONCEPT 3: DICTIONARY
# ─────────────────────────────────────────────
# Dictionary = key-value pairs — ek entity ki poori profile
# Use karo jab: ek transaction/user ka complete snapshot chahiye
# Access: dict['key'] — naam se dhundho, index se nahi
# GALTI: 'dict' Python ka built-in keyword hai — kabhi variable
# naam mat rakho 'dict' — use karo: transaction_info, record, etc.
 
# ─────────────────────────────────────────────
# CONCEPT 4: LIST OF DICTIONARIES
# ─────────────────────────────────────────────
# Yeh AlphaDefense ka real data structure hai
# CSV ka har row = ek dictionary (ek transaction ki profile)
# Poora CSV = list of dictionaries (series of transactions)
# Loop mein: i = ek dictionary → i['key'] se value nikalo
 
 
# ─────────────────────────────────────────────
# TASK 1: List of 5 transaction amounts + loop
# ─────────────────────────────────────────────
# List stores series — amounts over time
# for loop directly deta hai value, index nahi
 
transaction_amounts = [1234, 765, 6543, 765, 876]
 
print("--- TASK 1: Transaction Amounts ---")
for amount in transaction_amounts:
    print(amount)
 
# Output:
# 1234
# 765
# 6543
# 765
# 876
 
 
# ─────────────────────────────────────────────
# TASK 2: Single transaction dictionary
# ─────────────────────────────────────────────
# Dictionary = ek transaction ki poori profile
# merchant = kahan hua (karyana store, amazon, hospital)
# device = kis device se hua (phone, laptop, ATM)
# NOTE: variable naam 'dict' mat rakho — Python ka built-in hai
# Sahi naam: transaction_info
 
transaction_info = {
    'amount': 1233,
    'is_fraud': True,
    'merchant': 'karyana store',
    'device': 'phone'
}
 
print("\n--- TASK 2: Single Transaction Profile ---")
print(transaction_info)
print(transaction_info['amount'])
print(transaction_info['is_fraud'])
print(transaction_info['merchant'])
print(transaction_info['device'])
 
# Output:
# {'amount': 1233, 'is_fraud': True, 'merchant': 'karyana store', 'device': 'phone'}
# 1233
# True
# karyana store
# phone
 
 
# ─────────────────────────────────────────────
# TASK 3: List of 3 dictionaries — AlphaDefense core structure
# ─────────────────────────────────────────────
# Yeh real fraud pipeline ka foundation hai
# Har dictionary = ek transaction
# List = multiple transactions (user history, batch data)
# Loop mein i = ek poora dictionary
# i['amount'] = us dictionary ki amount value
 
user_history = [
    {'amount': 1299,  'is_fraud': True},
    {'amount': 12345, 'is_fraud': False},
    {'amount': 7654,  'is_fraud': True}
]
 
print("\n--- TASK 3: User Transaction History ---")
for transaction in user_history:
    print(transaction['amount'], transaction['is_fraud'])
 
# Output:
# 1299 True
# 12345 False
# 7654 True
 
 
# ─────────────────────────────────────────────
# ALPHADEFENSE CONNECTION
# ─────────────────────────────────────────────
# IEEE-CIS dataset load hoga → list of dictionaries
# Har transaction = ek dictionary with 400+ features
# amount, device, merchant, ip, time → sab keys honge
# Loop se har transaction process hogi → fraud score milega
# Script 5 ki Transaction class + Script 6 ka data structure
# = AlphaDefense ka complete transaction pipeline
 
