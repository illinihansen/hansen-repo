# -*- coding: utf-8 -*-
"""
Created on Fri Nov 02 11:03:37 2012

@author: thansen
"""

import re
import commands
from datetime import date, timedelta, datetime
from optparse import OptionParser


timeFormat = "%H:%M:%S.%f"
path = r"/Public2/thansen/python/IVintraday/"
dataList = []
uniqueList = []
user = commands.getoutput('whoami')

usage = "USAGE: %prog [symbol]"
parser = OptionParser(usage=usage)
parser.add_option("-u", "--user", dest="user", help="MySQL user name", metavar="USER NAME", default="ctsuser")
parser.add_option("-p", "--password", dest="password", help="MySQL password", metavar="PASSWORD", default="c9t8s2")
parser.add_option("-d", "--database", dest="database", help="MySQL database name", metavar="DB", default="Hull")
parser.add_option("-n", "--nototal", dest="nototal", help="Doesn't sum up positions", metavar="NOTOTAL")
parser.add_option("-o", "--outfile", dest="outfile", help="Writes to outfile instead of stdout", metavar="OUTFILE")
(options,args) = parser.parse_args()
optClass = str(args[0].upper())


if 'ES' in optClass:
    yestPath = "/Public2/Archive/AUPRODCTS17/"
    symbolServer = 'AUPRODCTS17'
else:
    yestPath = "/Public2/Archive/AUPRODCTS13/"
    symbolServer = 'AUPRODCTS13'

if date.weekday(date.today()) == 0:
    y = date.today() - timedelta(3)
else:
    y = date.today() - timedelta(1)
yesterday = y.isoformat()
    
yestFile = yestPath + "KODBData.log." + yesterday

if 'ES' in optClass:
    yestData = commands.getoutput('grep ' + optClass + ' ' + yestFile + ' | grep "15:14:5.*INFO" ')
else:
    yestData = commands.getoutput('grep ' + optClass + ' ' + yestFile + ' | grep "13:14:5.*INFO" ')

commands.getoutput("scp thansen@" + symbolServer + ":/var/cts/Logs/KODBData.log /Public2/thansen/python/IVintraday/KODBData.log; " + \
                    " grep " + optClass + " /Public2/thansen/python/IVintraday/KODBData.log > /Public2/thansen/python/IVintraday/opData.txt")


for item in reversed(yestData):
    RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}\.\d{3}) INFO.*uTV=([0-9]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*", yestData, re.M)
    if RX_OptionMarket and float(RX_OptionMarket.group(3)) != 0.000000:
        dataList.append([RX_OptionMarket.group(1), RX_OptionMarket.group(2), RX_OptionMarket.group(3), RX_OptionMarket.group(4), RX_OptionMarket.group(5)])
        break
    


dataFile = open(path + "opData.txt", "r") 

for line in dataFile:
    RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}\.\d{3}) INFO.*uTV=([0-9]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*", line, re.M)
    match = RX_OptionMarket
    if match and float(match.group(2)) != 0 and float(match.group(3)) != 0 and float(match.group(4)) != 0:
        dataList.append([match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)])
                        
dataFile.close()                  

outputFile = open(path + "output.txt", "w")


count = 0
high = 0
low = 1
print "Timestamp\tuTV\tuMSP\tMyIV\tTheoIV"
outputFile.write("Timestamp\tuTV\tuMSP\tMyIV\tTheoIV\n")
for i, item in enumerate(dataList):

    splitTime = (item[0].split("."))[0]
    if splitTime not in uniqueList:
        uniqueList.append(splitTime)
        if i == 0:
            startIV = item[2]
            print(item[0] + "\t" + item[1] + "\t" + item[4] + '\t' + item[2] + "\t" + item[3]) 
            
        if count != 1 and i != 0:
            print(item[0] + "\t" + item[1] + "\t" + item[4]+ "\t" + item[2] + "\t" + item[3])
            count = 1
            
        outputFile.write(item[0] + '\t' + item[1] + "\t" + item[4] + "\t" +  item[2] + "\t" + item[3] + '\n')
        
        if float(high) < float(item[2]):
            high = item[2]
        if float(low) > float(item[2]):
            low = item[2]
        endIV = item[2]
        if 'ES' in optClass:
            closeTime = datetime.strptime("15:14:50","%H:%M:%S")
        else:
            closeTime = datetime.strptime("13:14:50","%H:%M:%S")
        if datetime.strptime(item[0], timeFormat) > closeTime and i != 0:
            print(item[0] + "\t" + item[1] + "\t" + item[4] + "\t" + item[2] + "\t" + item[3])
            break
        if i == len(dataList) - 5:
            print(item[0] + "\t" + item[1] + "\t" + item[4] + "\t"+ item[2] + "\t" + item[3])

print "\n"
changeIV = float(endIV) - float(startIV)

print("High = " + str(high))
print("Low = " + str(low))
print("Change in IV = " + str(changeIV))

print("\n\n")
print("Complete output file at /Public/thansen/python/IVintraday/output.txt\n")
outputFile.close()