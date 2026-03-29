# ============================================================
# script5_classes.py — OOP Foundations for AlphaDefense
# Topic: Classes, Objects, __init__, self, Methods
# Project: AlphaDefense — Quantitative Fraud Detection System
# ============================================================
 
# ─────────────────────────────────────────────
# CONCEPT 1: Class vs Object
# ─────────────────────────────────────────────
# Class  = blueprint. Defines structure and behaviour.
# Object = actual instance created from that blueprint.
# Transaction is the class. t1 and t2 are objects.
 
# ─────────────────────────────────────────────
# CONCEPT 2: __init__
# ─────────────────────────────────────────────
# __init__ is a special method that runs AUTOMATICALLY
# the moment an object is created.
# Purpose: give the object its full identity at birth.
# Without __init__, the object has no data.
 
# ─────────────────────────────────────────────
# CONCEPT 3: self
# ─────────────────────────────────────────────
# self = the current object being worked on.
# When you call t1.check_fraud(), Python does:
#     Transaction.check_fraud(t1)
#     self = t1
# self lets every method know WHOSE data to use.
# Same class, different objects — self separates them.
 
class Transaction:
 
    def __init__(self, amount, is_fraud):
        # __init__ fires automatically when object is created
        # self.amount = THIS object's amount
        # self.is_fraud = THIS object's fraud status
        self.amount = amount
        self.is_fraud = is_fraud
 
    def check_fraud(self):
        # Regular method — only runs when explicitly called
        # Uses self to access THIS object's is_fraud value
        if self.is_fraud:
            return "ALERT: Fraudulent transaction"
        else:
            return "CLEAR: Legitimate transaction"
 
    def transaction_summary(self):
        # Method calling another method of the same object
        # self.check_fraud() works because both belong to same object
        return f"Amount: {self.amount} | Fraud: {self.is_fraud} | Status: {self.check_fraud()}"
 
 
# ─────────────────────────────────────────────
# CREATING OBJECTS
# ─────────────────────────────────────────────
# The moment this line runs — __init__ fires automatically
# Python internally does: Transaction.__init__(t1, 5000, False)
# self = t1 in that moment
 
t1 = Transaction(5000, False)   # legitimate transaction
t2 = Transaction(99999, True)   # fraudulent transaction
 
# ─────────────────────────────────────────────
# USING METHODS
# ─────────────────────────────────────────────
 
# Accessing attributes directly
print(t1.amount)        # 5000
print(t2.is_fraud)      # True if some_value: ka matlab hai if some_value == True: — shorthand hai bas.
 
# Calling check_fraud method
# Note: check_fraud vs check_fraud()
# check_fraud   = pointing at the method (does NOT run it)
# check_fraud() = actually calling the method (runs it)
print(t1.check_fraud())     # CLEAR: Legitimate transaction
print(t2.check_fraud())     # ALERT: Fraudulent transaction
 
# Calling transaction_summary — method calling another method
print(t1.transaction_summary())
print(t2.transaction_summary())
 
# ─────────────────────────────────────────────
# KEY OBSERVATIONS FROM THIS SESSION
# ─────────────────────────────────────────────
 
# 1. self is replaced by the object name under the hood
#    t1.check_fraud() → Transaction.check_fraud(t1) → self = t1
 
# 2. __init__ vs check_fraud:
#    __init__     → automatic, runs at object birth, sets up data
#    check_fraud  → manual, runs only when called, uses that data
 
# 3. Without () — you point at the method, you don't call it
#    print(t1.check_fraud)  → shows memory address of method
#    print(t1.check_fraud()) → actually executes and returns value
 
# 4. One method can call another method via self
#    transaction_summary calls check_fraud using self.check_fraud()
 
# ─────────────────────────────────────────────
# ALPHADEFENSE CONNECTION
# ─────────────────────────────────────────────
# Every transaction in your fraud detection system
# will be an object like this — with amount, user_id,
# merchant, device fingerprint as attributes,
# and methods like compute_risk_score(), apply_garch(),
# get_shap_explanation() as behaviour.
# This Transaction class is the seed of AlphaDefense.
