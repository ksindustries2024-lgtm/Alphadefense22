# ============================================================
# script4_composition.py
# AlphaDefense Learning Track — Function Composition
# Author: km | DAV Jalandhar | AI Engineering Sem 4
# ============================================================
 
# FUNCTION COMPOSITION
# Output of one function becomes input of another
# Pattern: outer(inner(value)) — inner runs first, outer gets its result
# AlphaDefense pipeline: extract → score → flag → audit
 
# FUNCTION 1: Calculate risk score from transaction amount
def calculate_risk(amount):
    if amount > 5000:
        risk_score = 0.8    # high amount = high risk
        return risk_score
    else:
        risk_score = 0.3    # low amount = low risk
        return risk_score
 
# FUNCTION 2: Flag fraud based on risk score
def flag_fraud(risk_score):
    if risk_score > 0.5:
        return True         # fraud suspected
    else:
        return False        # transaction clean
 
# COMPOSITION: calculate_risk() output -> flag_fraud() input
print(flag_fraud(calculate_risk(34445)))   # Output: True  (34445 > 5000 -> 0.8 -> fraud)
print(flag_fraud(calculate_risk(1000)))    # Output: False (1000 < 5000 -> 0.3 -> clean)
 
# ============================================================
# Core idea:
# flag_fraud(calculate_risk(34445))
# Step 1: calculate_risk(34445) runs -> returns 0.8
# Step 2: flag_fraud(0.8) runs -> returns True
# One line, two functions, clean pipeline
#
# This IS AlphaDefense at micro scale:
# calculate_risk  -> XGBoost scoring function
# flag_fraud      -> threshold-based decision layer
# ============================================================
#concept of args and kwargs as in functions
# they are actually used to help functions to take positional and key-word arguments easily
#*args- it actually helps function to take positional arguments easily convert them into the tuple example-(1,2,3)
#**kwargs- its actually used to help functions to take key-word types of arguments easily example-name:'km122'
def f(*args, **kwargs):
    print(args) #here you have to take that you only have to put  args only not*
    print(kwargs) #here you have to take that you only have to put  kwargs only not*
    
f(1,2,3,name='krrish',age=21)
#output: ==================
#(1, 2, 3)
#{'name': 'krrish', 'age': 21}

