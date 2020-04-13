# -*- coding: utf-8 -*-
"""
Created on Wed Dec 12 11:06:06 2012

@author: thansen
"""

import re
import commands
from datetime import datetime
import numpy

path = r"/Public2/thansen/python/MakerOrderLength/"
orderList = []
resultList = []
timeLengthList = []
timeOrderList = []
symbolList = []
timeFormat = "%H:%M:%S.%f"

user = commands.getoutput('whoami')

print('\n')
print("Run this script in production: \n")
print("#1: grep 'ORDER (.*MAKER' /var/cts/Logs/Orders.log > /home/" + user + "/orders.txt;  egrep 'FILL|CANCEL ' /var/cts/Logs/Orders.log > " + \
        " /home/" + user + "/result.txt; scp /home/" + user + "/orders.txt /home/" + user + "/result.txt eqctsutil02:/Public2/thansen/python/MakerOrderLength/" )
print('\n')
raw_input("Press 'Enter' when done")
print('\n')    

orderFile = open(path + "orders.txt") 

for line in orderFile:
    RX_OptionMarket = re.match (".*\(.*(\d{2}\:\d{2}\:\d{2}\.\d{6}).*\s([0-9A-Z_]+)\s@.*#:\s([0-9]+).*", line, re.M)
    match = RX_OptionMarket
    if match:
        orderList.append([match.group(1), match.group(3),match.group(2)])
                        
orderFile.close()      

resultFile = open(path + "result.txt") 

for line in resultFile:
    RX_OptionMarket = re.match (".*\(.*(\d{2}\:\d{2}\:\d{2}\.\d{6}).*#:\s([0-9]+).*", line, re.M)
    match = RX_OptionMarket
    if match:
        resultList.append([match.group(1), match.group(2)])
                        
orderFile.close() 

secondCount = 0
futureSecondCount = 0
varCount = 0
futureVarCount = 0
varCount1 = 0
futureVarCount1 = 0
varCount2 = 0
futureVarCount2 = 0
totalCount = 0
futureTotalCount = 0

max = 0
tradeType = ""

for item in orderList:
    for line in resultList:
        if item[1] == line[1]:
            tradeType = item[2][0]                
            startTime = datetime.strptime(item[0], timeFormat)
            endTime = datetime.strptime(line[0], timeFormat)
            
            orderLength = float(str((endTime - startTime).seconds)    + "." + str((endTime - startTime).microseconds))
            if orderLength < float(1):
                secondCount += 1
                if tradeType != 'O':
                    futureSecondCount += 1
            if orderLength < float(.5):
                varCount += 1
                if tradeType != 'O':
                    futureVarCount += 1
            if orderLength < float(.2):
                varCount1 += 1
                if tradeType != 'O':
                    futureVarCount1 += 1
                if item[2][0] == 'O':
                    timeOrderList.append([orderLength, item[1]])
                if item[2] not in symbolList:
                    symbolList.append(item[2])
            if orderLength < float(.1):
                varCount2 += 1
                if tradeType != 'O':
                    futureVarCount2 += 1
            timeLengthList.append(orderLength) 
            
            totalCount += 1
            if tradeType != 'O':
                    futureTotalCount += 1


print("Total orders: " + str(totalCount))
print("Orders under 1 second in duration: " + str(secondCount))
print("Percentage of orders under 1 second: " + str((float(secondCount)/float(totalCount))*100)[0:5] + "%")
print("Average order length (in seconds): " + str(numpy.average(timeLengthList))[0:5])
print("Median order length (in seconds): " + str(numpy.median(timeLengthList))[0:5])
print("# of orders under .5 seconds: " + str(varCount))
print("# of orders under .2 seconds: " + str(varCount1))
print("# of orders under .1 seconds: " + str(varCount2))
print("\n")

print("Total futures orders: " + str(futureTotalCount))
print("Futures orders under 1 second in duration: " + str(futureSecondCount))
print("Percentage of futures orders under 1 second: " + str((float(futureSecondCount)/float(futureTotalCount))*100)[0:5] + "%")
print("# of futures orders under .5 seconds: " + str(futureVarCount))
print("# of futures orders under .2 seconds: " + str(futureVarCount1))
print("# of futures orders under .1 seconds: " + str(futureVarCount2))