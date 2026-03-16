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
    if balance < 50000:
        break
    balance=balance-transaction[i]
    i=i+1


#task3:add continue:loop over the same transaction list.skip any amount below 500
#using continue.print the rest.
#program-
transaction=[250,1500,89,4200,73000]
for trans in transaction:
    if trans<=500:
        continue
    balance=balance-trans
    print(balance)
    
        
