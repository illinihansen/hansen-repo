# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 15:02:18 2012

@author: thansen
"""

import re
import commands

path = r"/Public2/thansen/python/ContractsTraded/"
orderList = []
commissionDict = {}
volumeDict = {}
user = commands.getoutput('whoami') 

with open(r"/Public2/thansen/python/symbolCommissions.txt") as f:
    for line in f:
        (key, val) = line.split('\t')
        commissionDict[key] = float(val)


print('\n')
print("Run this script in production: \n")
print("#1: grep FILL /var/cts/Logs/Fills.log > /home/" + user + "/orders.txt; scp /home/" + \
       user + "/orders.txt " + "eqctsutil02:/Public2/thansen/python/ContractsTraded" )

print('\n')
raw_input("Press 'Enter' when done")
print('\n')    

orderFile = open(path + "orders.txt")
for line in orderFile:
    RX_OptionMarket = re.match (".*BUY\s([0-9]+)\s([0-9A-Z_]+).*", line, re.M)
    match = RX_OptionMarket
    RX_OptionMarket1 = re.match (".*SELL\s([0-9]+)\s([0-9A-Z_]+).*", line, re.M)
    match1 = RX_OptionMarket1
    if match:
        orderList.append([match.group(1), match.group(2)])
    if match1:
        orderList.append([match1.group(1), match1.group(2)])
        
totalSum = 0
optSum = 0
futSum = 0
totalCommission = 0
for line in orderList:
    totalSum = totalSum + int(line[0])
    if '_' in line[1]:
        optSum += int(line[0])
        symbol = line[1].split("_")[0]
        if len(symbol) == 4:
            symbol += "_"
        totalCommission += int(line[0]) * commissionDict[line[1][0:5]]
    else:
        futSum += int(line[0])
        totalCommission += int(line[0]) * commissionDict[line[1]]
        symbol = line[1]
    if not volumeDict.has_key(symbol):
        volumeDict[symbol] = int(line[0])
    else:
        volumeDict[symbol] += int(line[0])
        
print("Total contracts traded: " + str(totalSum) )
print("Total options traded: " + str(optSum) )
print("Total futures traded: " + str(futSum) )
print("Total Commission: $" + str(totalCommission) )



print(volumeDict)
for key in volumeDict:
    print(str(key) + "\t" + str(volumeDict[key]))