#SCRIPT1-LOOP EXPLAINING WITH 3 TASK'S
#TASK1:add a condition inside a loop here we will consider for loop where
#will print only transactions above 100000.you have list and if statement also in the loop
#program-
transaction=[250,1500,89,4200,73000]
for trans in transaction:
    if trans>10000:
        print(trans)


#task2:add a while loop below-write a while loop balance=100000,keep subracting
#transaction amounts one by one till it's below 50000 and use break also.
#program-
transaction=[250,1500,89,4200,73000]
i=0
balance=100000
while balance >=50000:
    balance=balance-transaction[i]
    if balance < 50000:
        break
    print(balance)
    i=i+1

#task3:add continue:loop over the same transaction list.skip any amount below 500
#using continue.print the rest.
#program-
transaction=[250,1500,89,4200,73000]
balance=10000
for trans in transaction:
    if trans <= 500:      # 1. decide: skip or not
        continue
    balance = balance - trans  # 2. only operate on what passed the filter
    print(balance)             # 3. show result
    
#donot put condition before first possible operation so the variable should get new data after operation then check it sometimes allow first operation costly apply condition first
    
        
