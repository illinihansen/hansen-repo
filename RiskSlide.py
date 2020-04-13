#!/usr/bin/python

import re
import commands
import func
from datetime import datetime, timedelta
from optparse import OptionParser
import MySQLdb
#from datetime import time

# this program must be run in UTIL

path = r"/Public2/thansen/python/"
optClass = ""
ulInputStr = "s"
Ketchum_SymbolDict = {}
RangeRisk = []
rangeList = []
opDataList = []
multiplier = 50
counter = 0
volJump = [2,1,.75]
endPnL = 0
sec = ""
min = ""
qTime = ""
optFutDict = {}
productServerDict = {}
closingTimeDict = {}
contractInfoList = []
contractList = []


def getContractInfo(db, classSymbol):
        c = db.cursor()
        c.execute("SELECT Symbol FROM Instruments WHERE InstrumentClass = '" + classSymbol + "' AND InstrumentType = 2")
        dbRows = c.fetchall()
        poses = []
        symbolList = []
        for row in dbRows:
            poses.extend(list(row))
        for item in poses:
            temp = item[:-2]
            symbolList.append(temp)
        return symbolList


usage = "USAGE: %prog [option class] ["
parser = OptionParser(usage=usage)
parser.add_option("-u", "--user", dest="user", help="MySQL user name", metavar="USER NAME", default="ctsuser")
parser.add_option("-p", "--password", dest="password", help="MySQL password", metavar="PASSWORD", default="c9t8s2")
parser.add_option("-d", "--database", dest="database", help="MySQL database name", metavar="DB", default="Hull")
parser.add_option("-n", "--nototal", dest="nototal", help="Doesn't sum up positions", metavar="NOTOTAL")
parser.add_option("-o", "--outfile", dest="outfile", help="Writes to outfile instead of stdout", metavar="OUTFILE")
(options,args) = parser.parse_args()
optClass = str(args[0].upper())


with open(path + "classServer.txt") as f:
    for line in f:
        (key, val) = line.split('\t')
        if key == optClass:
            productServerDict[key] = val.rstrip()
       
db = MySQLdb.connect(host=productServerDict[optClass], user=options.user, db = "Hull", passwd=options.password)

contractInfoList = getContractInfo(db, optClass)
contractInfoList.append(optClass)

print contractInfoList

symbolServer = productServerDict[optClass]

with open(path + "closingTime.txt") as f:
    for line in f:
        (key, val) = line.split('\t')
        closingTimeDict[key] = val.rstrip()


posfile = commands.getoutput('hull_getcombinedpos --password=c9t8s2')

position = open("pos.txt",'w')
position.writelines(posfile)
position.close()

position = open("pos.txt",'r')
for line in position:
    (symbol, qty) = line.split(" ")
    if '_' in symbol: 
        splitSymbol = symbol.split('_')[0]
        if splitSymbol in contractInfoList:
            if len(splitSymbol) == 5: fut = splitSymbol[1:5]
            elif len(splitSymbol) == 4:
                fut = splitSymbol
                if not optFutDict.has_key(fut):
                    optFutDict[splitSymbol] = fut
            Ketchum_SymbolDict[symbol]=int(qty)
    elif symbol in contractInfoList:
        Ketchum_SymbolDict[symbol]=int(qty)
        
print Ketchum_SymbolDict
    
currentTime = datetime.time(datetime.now())

if datetime.time(datetime.now()) >= datetime.time(datetime.strptime(closingTimeDict[optClass], "%H:%M:%S")):
    qTime = datetime.strptime(closingTimeDict[optClass], "%H:%M:%S") - timedelta(0,10)
    qTime = qTime.__format__("%H:%M:%S")
else:
    if currentTime.minute < 10: min = "0"
    qTime = str(currentTime.hour) + ":" + min + str(currentTime.minute) + ":"

commands.getoutput("scp thansen@" + symbolServer + ":/var/cts/Logs/KODBData.log /Public2/thansen/python/RiskSlide/KODBData.log; " + \
                    " grep " + optClass[:2] + " /Public2/thansen/python/RiskSlide/KODBData.log | grep " + str(qTime) + ".*INFO |  grep 'Type= T' > /Public2/thansen/python/RiskSlide/opData.txt")

  
opFile = open( path + "/RiskSlide/opData.txt",'r')

for line in opFile: 
    RX_OptionMarket = re.match (".*Symbol=([A-Z0-9_]+).*MyIV=([0-9.]+).*uMSP=([0-9]+).*DaysToExp=([0-9.]+).*", line, re.M)
    match = RX_OptionMarket
    if match:
        matchSymbol = match.group(1)
        matchMyIV = match.group(2)
        matchuMSP = match.group(3)
        matchDTE = match.group(4)

        opDataList.append([matchSymbol, matchMyIV, matchuMSP, matchDTE])           
opFile.close()

if 'ES' in optClass:
    uMSP = float(opDataList[0][2]) / 100
else:
    uMSP = float(opDataList[0][2]) / 1000


IR = 0 
for item in opDataList:
    if not float(item[3]) == 0: 
        DTE = float(item[3]) / 252
    if not float(item[1]) == 0:
        atmIV = float(item[1])


while not ulInputStr.isdigit():
    ulInputStr = raw_input('Enter underlying value(currently ' + str(uMSP) + ') or type "0" to see full risk slide: ')
    print('\n')
ulInput = float(ulInputStr)

if int(ulInput) == 0:
    rangeList.append(float(uMSP * 1.20))
    rangeList.append(float(uMSP * 1.15))
    rangeList.append(float(uMSP * 1.10))
    rangeList.append(float(uMSP * 1.05))
    rangeList.append(float(uMSP * .95))
    rangeList.append(float(uMSP * .90))
    rangeList.append(float(uMSP * .85))
    rangeList.append(float(uMSP * .80))
    
for optionKey in Ketchum_SymbolDict:
    IV = -1    
    
    counter += 1
    strikeDataList = []
    if '_' in optionKey:
        for line in opDataList:
            if line[0] == optionKey:
                IV = float(line[1])
        symbolSplit = optionKey.split('_')[1]
        PCF = symbolSplit[0:1]
        indexflag = 0
        strike = int(symbolSplit[1:])
    else:
        PCF = "F"

    if int(ulInput) != 0:
        if PCF != 'F':
            currentPrice = func.BS_Pricer(PCF, uMSP, strike, DTE, IR, atmIV)
            rangePrice = func.BS_Pricer(PCF, ulInput, strike, DTE, IR, atmIV)
        else:
            currentPrice = uMSP
            rangePrice = ulInput
        strikePnL = (rangePrice - currentPrice) * Ketchum_SymbolDict[optionKey] * multiplier
        endPnL += strikePnL
    else:
        for range in rangeList:
            i = rangeList.index(range)
            opList = []
            for item in volJump:
                j = volJump.index(item)
                if PCF != 'F':
                    currentPrice = func.BS_Pricer(PCF, uMSP, strike, DTE, IR, atmIV)
                    rangePrice = func.BS_Pricer(PCF, range, strike, DTE, IR, (atmIV*item))
                else:
                    currentPrice = uMSP
                    rangePrice = range
                strikePnL = (rangePrice - currentPrice) * Ketchum_SymbolDict[optionKey] * multiplier
                opList.append(strikePnL)
                if len(RangeRisk) > 7:
                    RangeRisk[i][j] += strikePnL
            if len(RangeRisk) < 8:
                RangeRisk.append(opList)

                    
print("Base Underlying for " + optClass + " = " + str(uMSP))
print("***************************************\n")

if ulInput != 0:
    print("@ " + str(round(ulInput, 1)) + "  IV = " + str(round(atmIV,3)) + " PnL = " + str(round(endPnL,2)) + '\n')
else:
    if len(RangeRisk) != 0:
        for range in rangeList: 
            i = rangeList.index(range)
            for item in volJump:
                j = volJump.index(item)
                print("@ " + str(round(range,1)) + "  IV = " + str(round(item*atmIV, 3)) + " PnL= " + str(round(RangeRisk[i][j],2)))
            print("\n")
    else:
        print("Option Data File was invalid\n")
print("***************************************\n")

    

                                          


        
