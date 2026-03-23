# ============================================================
# script2_functions.py
# AlphaDefense Learning Track — Python Functions
# Author: km | DAV Jalandhar | AI Engineering Sem 4
# ============================================================
 
# TASK 1: Regular Parameters
# Fixed positional inputs — caller MUST provide both values
# Use case: when you know exact number of inputs
def task1(fee, amount):
    total_fee = fee * amount
    return total_fee
 
# TASK 2: *args — Variable Positional Arguments
# Packs ALL positional inputs into a TUPLE
# Use case: when input count is unknown (e.g. summing N transactions)
def task2(*amount):
    trans1 = sum(amount)   # sum() works on tuples — NOT .sum() (that's pandas)
    return trans1
 
# TASK 3: **kwargs — Variable Keyword Arguments
# Packs ALL named inputs into a DICTIONARY
# Use case: flexible labelled data (e.g. transaction metadata fields)
def task3(**t):
    return t
 
# TASK 4: Orchestrator
# Calls all 3 functions — no new logic, just coordination
# This pattern scales to full pipelines (AlphaDefense: extract → score → audit)
def taskcalling():
    firstcall  = task1(5000, 0.33)
    secondcall = task2(1200, 1300, 1400, 1500, 1600, 1777, 1893)
    thirdcall  = task3(full_name='krrish', score_marks=56,
                       location='india', region='punjab')
    print(firstcall)
    print(secondcall)
    print(thirdcall)
 
taskcalling()
 
# Expected Output:
# 1650.0
# 10670
# {'full_name': 'krrish', 'score_marks': 56, 'location': 'india', 'region': 'punjab'}
