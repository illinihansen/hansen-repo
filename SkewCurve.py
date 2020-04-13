# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 08:42:59 2012

@author: thansen
"""

import re
import commands
import os.path
from datetime import date, datetime, time, timedelta
from operator import itemgetter
from optparse import OptionParser



class yData():
    _registry = []
    def __init__(self):
        self._registry.append(self)
        
class tData():
    _registry = []
    def __init__(self):
        self._registry.append(self)



usage = "USAGE: %prog [class] "
parser = OptionParser(usage=usage)
(options, args) = parser.parse_args()
usr = commands.getoutput('whoami')
symbolClass = str(args[0].upper())

boxSymbol = "AUPRODCTS13"

yestPath = "/Public2/Archive/" + boxSymbol + "/"
path = r"/Public2/thansen/python/SkewCurve/"
yDataList = []
tDataList = []
optFutDict = {}
Ketchum_SymbolDict = {}
tDataDict = {}
yDataDict = {}

#posfile = commands.getoutput('hull_getcombinedpos --password=c9t8s2')
#
#position = open("pos.txt",'w')
#position.writelines(posfile)
#position.close()
#
#position = open("pos.txt",'r')
#for line in position:
#    if '_' in line:
#        symbolSplit = line.split('_')[0]
#        if len(symbolSplit) == 5:
#            fut = symbolSplit[1:5]
#        elif len(symbolSplit) == 4:
#            fut = symbolSplit
#        if not optFutDict.has_key(fut):
#            optFutDict[symbolSplit] = fut


m = ""
sec = ""
qTime = ""
currentTime = datetime.time(datetime.now())

if datetime.time(datetime.now()) >= time(15,15,0):
    qTime = "15:14:5"
else:
    if currentTime.second < 10:
        sec = "0"
    if currentTime.minute < 10:
        m = "0"
    qTime = str(currentTime.hour) + ":" + m + str(currentTime.minute) + ":"

if date.weekday(date.today()) == 0:
    y = date.today() - timedelta(3)
else:
    y = date.today() - timedelta(1)
yesterday = y.isoformat() 
yestFile = yestPath + "KODBData.log." + yesterday    

while not os.path.exists(yestFile):   #3 day weekend
    print "3 day weekend\n"
    print yestFile
    y = y - timedelta(1)
    yesterday = y.isoformat()
    yestFile = yestPath + "KODBData.log." + yesterday
     
commands.getoutput("scp thansen@" + boxSymbol + ":/var/cts/Logs/KODBData.log /Public2/thansen/python/SkewCurve/KODBData.log;" \
                    + "grep " + symbolClass + " /Public2/thansen/python/SkewCurve/KODBData.log | grep " + qTime + ".*INFO | grep 'Type= T' | grep -v 'RiskVol=0.00' > /Public2/thansen/python/SkewCurve/opData.txt")


if 'ES' in symbolClass: yestData = commands.getoutput('grep ' + symbolClass + ' ' + yestFile + ' | grep "15:14:50.*INFO" | grep "Type= T" | grep -v "RiskVol=0.00" ' )
else: yestData = commands.getoutput('grep ' + symbolClass + ' ' + yestFile + ' | grep "13:14:50.*INFO" | grep "Type= T" | grep -v "RiskVol=0.00" ' )


dataFile = open(path + 'yData.txt', 'w')
dataFile.write(yestData)
dataFile.close()

yestData = open(path + 'yData.txt', 'r')

for line in yestData:
    match = re.match (".*Symbol=([0-9A-Z_]+).*RiskVol=([0-9.]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*", line, re.M)
    if match:
        data = yData()
        data.symbol = match.group(1)
        data.riskVol = float(match.group(2))
        data.myIV = match.group(3)
        data.theoIV = match.group(4)
        data.uMSP = float(match.group(5))
yestData.close

dataFile = open(path + "opData.txt", "r") 
print (path + "opData.txt")

for line in dataFile:
    match = re.match (".*Symbol=([0-9A-Z_]+).*RiskVol=([0-9.]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*", line, re.M)
    if match:
        data = tData()
        data.symbol = match.group(1)
        data.riskVol = float(match.group(2))
        data.myIV = match.group(3)
        data.theoIV = match.group(4)
        data.uMSP = float(match.group(5))          
dataFile.close()

for data in tData._registry:
    symbolCP = data.symbol.split("_")[1][0]
    symbolStrike = int(data.symbol.split("_")[1][1:])
    if symbolStrike <= (data.uMSP / 1000) and symbolCP == 'P':
        if not tDataDict.has_key(symbolStrike):
            tDataDict[symbolStrike] = (data.riskVol, data.myIV)
    if symbolStrike > (data.uMSP / 1000) and symbolCP == 'C':
        if not tDataDict.has_key(symbolStrike):
            tDataDict[symbolStrike] = (data.riskVol, data.myIV)
            

for data in yData._registry:
    symbolCP = data.symbol.split("_")[1][0]
    symbolStrike = int(data.symbol.split("_")[1][1:])
    if symbolStrike <= (data.uMSP / 1000) and symbolCP == 'P':
        if not yDataDict.has_key(symbolStrike):
            yDataDict[symbolStrike] = (data.riskVol, data.myIV)
    if symbolStrike > (data.uMSP / 1000) and symbolCP == 'C':
        if not yDataDict.has_key(symbolStrike):
            yDataDict[symbolStrike] = (data.riskVol, data.myIV)
            
               
print("Strike\tCurrentMyIV\tYestMyIV\tCurrentTheoIV\tYestTheoIV")

outputFile = open(path + "output.txt", "w")
sortList = []
for key in tDataDict:
    if yDataDict.has_key(key):
        sortList.append([key, tDataDict[key][0], yDataDict[key][0]])
sortList = sorted(sortList, key=itemgetter(0))

for line in sortList:
    outputFile.write(str(line[0]) + '\t' + str(line[1]) + '\t' + str(line[2]))
    print(str(line[0]) + '\t' + str(line[1]) + '\t' + str(line[2]))

print("Complete output file at /Public/thansen/python/SkewCurve/output.txt\n")    
outputFile.close()
    