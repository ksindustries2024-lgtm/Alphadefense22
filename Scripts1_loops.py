# ============================================================
# script1_loops.py
# AlphaDefense Learning Track — Loops & Conditionals
# Author: km | DAV Jalandhar | AI Engineering Sem 4
# ============================================================
 
# TASK 1: for loop + if condition
# Print only transactions above 10000
# Pattern: filter inside a loop using if
 
transactions = [250, 1500, 89, 4200, 73000]
 
for trans in transactions:
    if trans > 10000:
        print(trans)
 
# Output:
# 73000
 
# ============================================================
 
# TASK 2: while loop + break
# Start with balance=100000, subtract transactions one by one
# Stop as soon as balance drops below 50000
# Pattern: while for condition-driven repetition, break to exit early
 
transactions = [250, 1500, 89, 4200, 73000]
balance = 100000
i = 0
 
while balance >= 50000:
    balance = balance - transactions[i]
    if balance < 50000:
        break
    print(balance)
    i += 1
 
# Output:
# 99750
# 98250
# 98161
# 93961
 
# Key rule: operate FIRST, then check — expensive check after cheap operation
# Here: subtract first, THEN check if below 50000
 
# ============================================================
 
# TASK 3: for loop + continue
# Skip transactions below 500, process the rest
# Pattern: continue = skip this iteration, move to next
 
transactions = [250, 1500, 89, 4200, 73000]
balance = 10000
 
for trans in transactions:
    if trans <= 500:
        continue              # skip small transactions
    balance = balance - trans  # only runs if trans > 500
    print(balance)
 
# Output:
# 8500
# 4300
# -68700
 
# ============================================================
# Core distinctions:
# for   — use when you know iteration count (list, range)
# while — use when you iterate on a CONDITION (unknown count)
# break — exit loop immediately
# continue — skip current iteration, continue loop
#
# AlphaDefense rule:
# Apply condition BEFORE costly operation (e.g. model inference)
# Apply condition AFTER cheap operation (e.g. simple subtraction)
# ============================================================
#donot put condition before first possible operation so the variable should get new data after operation then check it sometimes allow first operation costly apply condition first
    
        
