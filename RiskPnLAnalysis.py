# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 13:34:36 2013

@author: thansen
"""

import re
import commands
from operator import itemgetter

dataList = []
uniqueList = []
optFutDict = {}
Ketchum_SymbolDict = {}
optClass = ""

unixPath = r"/Public2/thansen/python/RiskPnLAnalysis/"
path = unixPath


posfile = commands.getoutput('hull_getcombinedpos --password=c9t8s2')

position = open("pos.txt",'w')
position.writelines(posfile)
position.close()

position = open("pos.txt",'r')
for line in position:
    if '_' in line:
        symbolSplit = line.split('_')[0]
        if len(symbolSplit) == 5:
            fut = symbolSplit[1:5]
        elif len(symbolSplit) == 4:
            fut = symbolSplit
        if not optFutDict.has_key(fut):
            optFutDict[symbolSplit] = fut


print('\n')
#while not optClass in optFutDict.values:
optClass = raw_input('Pick option class ' + str(optFutDict.values()) + ': ')
print('\n')




user = commands.getoutput('whoami')

print('\n')
print("Run this script in production: \n")
print("#1: grep " + optClass + " /var/cts/Logs/KODBStrategy.log | grep 'CLASS SNAPSHOT' | grep 'risk valid=1' > /home/" + user + "/datafile.txt; scp /home/" + user + "/datafile.txt eqctsutil02:/Public2/thansen/python/RiskPnLAnalysis" )
print('\n')
raw_input("Press 'Enter' when done")
print('\n') 


dataFile = open(path + "datafile.txt") 

for line in dataFile:
    RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}).*]\s:\s([A-Z0-9:]+).*pp=([0-9.-]+).*delta=.*/.*/([0-9.-]+).*vega=.*/.*/([0-9.-]+).*gamma.*.*term1ATMVol=([0-9.]+).*", line, re.M)
#    RX_OptionMarket = re.match (".*TRACE.*", line, re.M)
    match = RX_OptionMarket
    if match and int(float((match.group(4)))) != 0 and int(float(match.group(5))) != 0:
        dataList.append([match.group(1),match.group(2),match.group(3), match.group(4), match.group(5), match.group(6)])

dataFile.close()

outputFile = open(path + "output.txt", "w")
dataList.sort(key=itemgetter(1,0))
outputFile.write("Symbol\tTime\tTotalPnL\tuDelta\tuVega\tIV\n")
print("Symbol\tTime\tTotalPnL\tuDelta\tuVega\tATMIV\n")
for item in dataList:
    print(item[1] + '\t' + item[0] + '\t' + item[2] + '\t' + item[3] + '\t' + item[4] + '\t' + item[5])
    outputFile.write(item[1] + '\t' + item[0] + '\t' + item[2] + '\t' + item[3] + '\t' + item[4] + '\t' + item[5] + '\n')
outputFile.close

print('Paste output file into Excel')
    