# ============================================================
# script3_defaults.py
# AlphaDefense Learning Track — Default Arguments
# Author: km | DAV Jalandhar | AI Engineering Sem 4
# ============================================================
 
# DEFAULT ARGUMENT
# If caller does not provide a value, Python uses the default
# Syntax: def function(param=default_value)
# Rule: default params always come AFTER required params
 
def task(fee, amount=0.1):
    total_amount = fee * amount
    return total_amount
 
# Call 1: amount provided — default ignored
print(task(5000, 0.33))   # Output: 1650.0
 
# Call 2: amount NOT provided — default 0.1 used
print(task(5000))          # Output: 500.0
 
# ============================================================
# Key takeaway:
# task(5000, 0.33) → 5000 * 0.33 = 1650.0
# task(5000)       → 5000 * 0.1  = 500.0
# Default = fallback value when caller skips the argument
# AlphaDefense use: default risk_threshold=0.5 in scoring fn
# ============================================================
