# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 14:44:13 2013

@author: thansen
"""
import re
import commands
import pdb
from datetime import datetime, time

winPath = '\\\\eqprodnas01\\vg01.vol01.Public2\\thansen\\python\\IVForecast_withPos\\'
path = r"/Public2/thansen/python/IVForecast_withPos/"
DataList = []
resultList = []
IVList = []
timeList = []
optFutDict = {}
Ketchum_SymbolDict = {}
optClass = ""

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
while not optFutDict.has_key(optClass):
    optClass = raw_input('Pick option class ' + str(optFutDict.keys()) + ': ')
    print('\n')


user = commands.getoutput('whoami')



m = ""
sec = ""
qTime = ""
currentTime = datetime.time(datetime.now())

if datetime.time(datetime.now()) >= time(13,15,0):
    qTime = "13:14:50"
else:
    if currentTime.second < 10:
        sec = "0"
    if currentTime.minute < 10:
        m = "0"
    qTime = str(currentTime.hour) + ":" + m + str(currentTime.minute) + ":" + sec + str(currentTime.second)
    

print("Run these scripts in production: \n")
print("#1: grep 'MyVValid=1' /var/cts/Logs/KODBData.log | grep KMarketsValid=1 | grep ' Type= T' > /home/" + user + "/opData.txt; cp /var/cts/Logs/Fills.log /home/" + user + "/fills.log; scp /home/" + \
        user + "/opData.txt /home/" + user + "/fills.log eqctsutil02:/Public2/thansen/python/IVForecast_withPos/")
        
    
print('\n')
raw_input("Press 'Enter' when done")
print('\n') 
        
dataFile = open(path + "opData.txt", "r") 

print "Processing Datafile"

for line in dataFile:
    RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}).*INFO.*Symbol=([A-Z0-9_]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*", line, re.M)
    match = RX_OptionMarket
    if match:
        DataList.append([match.group(1), round((float(match.group(4)) - float(match.group(3))),5), match.group(2)])
                        
dataFile.close()

fillFile = open(path + "fills.txt", "r")

for line in fillFile:
    RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}).*):\s([A-Z]+)\s([0-9]+)\s([A-Z0-9_]+).*([0-9]+).*#:\s([0-9]+).*", line, re.M)
    match = RX_OptionMarket
    if match:
        pdb.set_trace()
        DataList.append([match.group(1), match.group(2)])


for item in DataList:
    if item[0] not in timeList:
        timeList.append(item[0])


print "Processing Records"

lastTime = ""



for line in timeList:
    
    IVList = []
    if line[0] == lastTime:
        continue
    print datetime.strptime(line, '%H:%M:%S')
    n = 0
    for index, item in enumerate(DataList):
        if item[0] == line:
            IVList.append([item[2], item[1]])
            
        if datetime.strptime(item[0], '%H:%M:%S') > datetime.strptime(line, '%H:%M:%S'):
            DataList = DataList[index:]
            break
            
    resultList.append([line, IVList])
    #pdb.set_trace()
    lastTime = line

print "Cleaning results"

count = 0

for item in resultList:
    low = 1
    high = -1
    
    for number in item[1]:
        if number[1] > high:
            high = number[1]
        if number[1] < low:
            low = number[1]
    if high - low > .005:
        print item
        count += 1

#    gt = 0       
#    lt = 0
#    for number in item[1]:
##        pdb.set_trace()
#        if number[1] > 0.002:
#            gt = 1
#        if number[1] < -0.002:
#            lt = 1
#    if gt == 1 and lt == 1:
#        count += 1

print "result count: " + str(count)
print "len of result list: " + str(len(resultList))
        
    

