# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 14:25:10 2012

@author: thansen
"""

import re
import commands
from datetime import datetime, timedelta, time, date
import os, os.path
#import pdb
import func, gzip, numpy


timeFormat = "%H:%M:%S.%f"
timeFormat1 = "%H:%M:%S"
secondsAhead = [5,10,30,60,180,300, 600] 
uPath = r"/Public2/thansen/python/TradeAnalyzer/"
winPath = '\\\\eqprodnas01\\vg01.vol01.Public2\\thansen\\python\\TradeAnalyzer\\'
path = r"/Public2/thansen/python/TradeAnalyzer/"
pathChoice = 'U'
inputStr = ""
recurse = 0
dollarizerDict = {}
futOptLookupDict = {}
optFutLookupDict = {}

if pathChoice == 'U':
    futOptFile = open('/Public2/thansen/python/futOptLookup.txt', 'r')
elif pathChoice == 'W':
    futOptFile = open('\\\\eqprodnas01\\vg01.vol01.Public2\\thansen\\python\\futOptLookup.txt', 'r')

for line in futOptFile:
    k, v = line.strip().split('\t')
    futOptLookupDict[k] = v
    optFutLookupDict[v] = k



def getTimePrice(orderTime, symbol, timeAhead, recurse, orderDate, timeStamp):
    
    splitTime = datetime.strftime(timeStamp, "%H:%M:%S")
    m = ""
    sec = ""
    #    different EOD times
    if orderDate < date(2013,4,8):
        closingTime = datetime.strptime("14:00:00", timeFormat1)
    else:
        closingTime = datetime.strptime("13:15:00", timeFormat1)

    tradePlusTime = datetime.strptime(splitTime, timeFormat1) + timedelta(0,timeAhead)
    if tradePlusTime >= closingTime:
        return (-1,-1, -1)
    if tradePlusTime.second < 10:
        sec = "0"    
    if tradePlusTime.minute < 10:
        m = "0"
    tradePlusTimeStr = str(tradePlusTime.hour) + ":" + m + str(tradePlusTime.minute) + ":" + sec + str(tradePlusTime.second)

    priceOutput = commands.getoutput("grep " + str(symbol) + ".*" + str(tradePlusTimeStr) + " "  + path + "timeFile.txt")

    splitList = priceOutput.split("\n") 

    splitRecord = splitList[0].split(",") 

    # if the returned record is not null
    if splitRecord != ['']:
        midPrice = (int(splitRecord[4]) + int(splitRecord[3])) / 2.0
        uMSP = splitRecord[5]
        MyIV = float(splitRecord[6])
        oMSP = float(splitRecord[7])
        return (oMSP, uMSP, MyIV)
    else:
        # go through the function again if returned null, but one second ahead, max 5 times through function
        tradePlusTime = datetime.strptime(splitTime, timeFormat1) + timedelta(0,timeAhead+1)
        recurse += 1
        if recurse < 5:
            midPrice = getTimePrice(orderTime, symbol, timeAhead+1, recurse, orderDate, timeStamp)
            return (midPrice)
        else:
            return (-1,-1,-1)
            

def getTVCross(orderTime, symbol, xList, TheoIV, uTV, BuySell, FutCallPut):
    uCrossTime = -1
    ivCrossTime = -1
    uCrossLevel = -1
    ivCrossLevel = -1
    if FutCallPut == 'F':
        symbol = futOptLookupDict[symbol]
        ivCrossTime = -1
    for item in xList:
        if FutCallPut == 'F':
            timeSymbol = item[0].split("_")[0]
        else:
            timeSymbol = item[0]
        if timeSymbol == symbol:
            if item[1] >= orderTime:
                if BuySell == 'BUY' and FutCallPut == 'C':
                    if item[3] >= uTV and uCrossTime == -1:
                        uCrossTime = item[1] - orderTime
                        uCrossLevel = item[3]
                    if item[2] >= TheoIV and ivCrossTime == -1:
                        ivCrossTime = item[1] - orderTime
                        ivCrossLevel = item[2]
                    if uCrossTime != -1 and ivCrossTime != -1:
                        return (int(uCrossTime.total_seconds()), int(ivCrossTime.total_seconds()), uCrossLevel, ivCrossLevel)
                        
                elif BuySell == 'BUY' and FutCallPut == 'P':
                    if item[3] <= uTV and uCrossTime == -1:
                        uCrossTime = item[1] - orderTime
                        uCrossLevel = item[3]
                    if item[2] >= TheoIV and ivCrossTime == -1:
                        ivCrossTime = item[1] - orderTime
                        ivCrossLevel = item[2]
                    if uCrossTime != -1 and ivCrossTime != -1:
                        return (int(uCrossTime.total_seconds()), int(ivCrossTime.total_seconds()), uCrossLevel, ivCrossLevel)
                        
                elif BuySell == 'SELL' and FutCallPut == 'C':
                    if item[3] <= uTV and uCrossTime == -1:
                        uCrossTime = item[1] - orderTime
                        uCrossLevel = item[3]
                    if item[2] <= TheoIV and ivCrossTime == -1:
                        ivCrossTime = item[1] - orderTime
                        ivCrossLevel = item[2]
                    if uCrossTime != -1 and ivCrossTime != -1:
                        return (int(uCrossTime.total_seconds()), int(ivCrossTime.total_seconds()), uCrossLevel, ivCrossLevel)
                        
                elif BuySell == 'SELL' and FutCallPut == 'P':
                    if item[3] >= uTV and uCrossTime == -1:
                        uCrossTime = item[1] - orderTime
                        uCrossLevel = item[3]
                    if item[2] <= TheoIV and ivCrossTime == -1:
                        ivCrossTime = item[1] - orderTime
                        ivCrossLevel = item[2]
                    if uCrossTime != -1 and ivCrossTime != -1:
                        return (int(uCrossTime.total_seconds()), int(ivCrossTime.total_seconds()), uCrossLevel, ivCrossLevel)
                        
                elif BuySell == 'BUY' and FutCallPut == 'F':
                    if item[3] >= uTV:
                        uCrossTime = item[1] - orderTime
                        uCrossLevel = item[3]
                        return (int(uCrossTime.total_seconds()), -1, uCrossLevel, -1)
                        
                elif BuySell == 'SELL' and FutCallPut == 'F':
                    if item[3] <= uTV:
                        uCrossTime = item[1] - orderTime
                        uCrossLevel = item[3]
                        return (int(uCrossTime.total_seconds()), -1, uCrossLevel, -1)
                        
    if uCrossTime != -1:
        uCrossTime = int(uCrossTime.total_seconds())
    if ivCrossTime != -1:
        ivCrossTime = int(ivCrossTime.total_seconds())

    return (uCrossTime, ivCrossTime, uCrossLevel, ivCrossLevel)
     


with open(r"/Public2/thansen/python/symbolDollarizer.txt") as f:
    for line in f:
        (key, val) = line.split('\t')
        dollarizerDict[key] = float(val)


while not (inputStr == 't' or inputStr == 'p'):
    inputStr = raw_input('Select today\'s data (t) or previous data (p) : ')
if inputStr == 'p':
    while True:
        startDateRaw = raw_input('Enter start date (yyyy-mm-dd):')
        endDateRaw = raw_input('Enter end date (yyyy-mm-dd):')
        startDate = datetime.strptime(startDateRaw, "%Y-%m-%d").date()
        endDate = datetime.strptime(endDateRaw, "%Y-%m-%d").date()
        if startDate > endDate:
            print "Error in Date Range"
            continue
        if startDate > date.today():
            print "Error in Date Range"
            continue
        if endDate > date.today():
            print "Error in Date Range"
            continue
        break
elif inputStr == 't':
    startDate = date.today()    
    endDate = startDate     


currentDate = startDate
outputFile = open(path + "output.txt", "w")
outputFile.write("Date\tTime\tSymbol\tOrderID\tTradeType\tF/C\tM/T\tKicker\tSize\tPrice\tCurrPrice\tPnLPerContract\tCurrTheoPnL\tCurrIVPnL\tCurrUPnL\t5sPnL\t10sPnL\t30sPnL\t60sPnL\t180sPnL\t300sPnL\t600sPnL\txtraEdge\tTVEdge\tTTC\tSpeed(uSec)\tCancelFill\tRiskOnOff\tRiskTradeType\tFutBias\tVolBias\tuCrossTime\tIVCrossTime\ttimeuMSP\ttimeMyIV\tuMSP\tuTV\tTheoIV\tMyIV\tuMidpoint\tivEdge$\tuEdge$\tEdgeCompare\tiv15sec\tiv30sec\tiv60sec\tiv120sec\tiv180sec\tiv300sec\tiv600sec\tu15sec\tu30sec\tu60sec\tu120sec\tu180sec\tu300sec\tu600sec\ttheo15sec\ttheo30sec\ttheo60sec\ttheo120sec\ttheo180sec\ttheo300sec\ttheo600sec\n")
logFile = open(path + "log.txt", "w")
logFile.write("Date\tTime\tSymbol\tOrderID\tTradeType\tF/C\tM/T\tKicker\tSize\tPrice\tCurrPrice\tPnLPerContract\tCurrTheoPnL\tCurrIVPnL\tCurrUPnL\t15sPnL\t30sPnL\t60sPnL\t120sPnL\t180sPnL\t300sPnL\t600sPnL\txtraEdge\tTVEdge\tTTC\tSpeed(uSec)\tCancelFill\tRiskOnOff\tRiskTradeType\tFutBias\tVolBias\tuCrossTime\tIVCrossTime\ttimeuMSP\ttimeMyIV\tuMSP\tuTV\tTheoIV\tMyIV\tuMidpoint\tivEdge$\tuEdge$\tEdgeCompare\tiv15sec\tiv30sec\tiv60sec\tiv120sec\tiv180sec\tiv300sec\tiv600sec\tu15sec\tu30sec\tu60sec\tu120sec\tu180sec\tu300sec\tu600sec\ttheo15sec\ttheo30sec\ttheo60dsec\ttheo120sec\ttheo180sec\ttheo300sec\ttheo600sec\n")


totalFuturesQty = 0
TotalOptionsQty = 0
makerFuturesQty = 0
makerOptionsQty = 0
takerFuturesQty = 0
takerOptionsQty = 0
takerFuturesFills = 0
makerFuturesFills = 0
takerOptionsFills = 0
makerOptionsFills = 0
takerFuturesMiss = 0
takerOptionsMiss = 0
takerFills = 0
takerMiss = 0
takerKicker = 0
takerKickerHit = 0
takerKickerMiss = 0
takerKickerOptionHit = 0
takerKickerFutureHit = 0
takerKickerOptionMiss = 0
takerKickerFutureMiss = 0
makerKicker = 0
futMakerKicker = 0
optMakerKicker = 0


makerAvePnLList = [0,0,0,0,0,0,0]
makeruXTime = 0
makerIVXTime = 0
makeruXCounter = 0
makerIVXCounter = 0
optMakerAvePnLList = [0,0,0,0,0,0,0]
optMakeruXTime = 0
optMakerIVXTime = 0
optMakeruXCounter = 0
optMakerIVXCounter = 0
futMakerAvePnLList = [0,0,0,0,0,0,0]
futMakeruXTime = 0
futMakeruXCounter = 0
makerAvePnLCounter = [0,0,0,0,0,0,0]
optMakerAvePnLCounter = [0,0,0,0,0,0,0]
futMakerAvePnLCounter = [0,0,0,0,0,0,0]


takerAveHitPnLList = [0,0,0,0,0,0,0]
takerHituXTime = 0
takerHitIVXTime = 0
takerHituXCounter = 0
takerHitIVXCounter = 0
optTakerAveHitPnLList = [0,0,0,0,0,0,0]
optTakerHituXTime = 0
optTakerHitIVXTime = 0
optTakerHituXCounter = 0
optTakerHitIVXCounter = 0
futTakerAveHitPnLList = [0,0,0,0,0,0,0]
futTakerHituXTime = 0
futTakerHituXCounter = 0
takerAveHitPnLCounter = [0,0,0,0,0,0,0]
optTakerAveHitPnLCounter = [0,0,0,0,0,0,0]
futTakerAveHitPnLCounter = [0,0,0,0,0,0,0]

takerAveMissPnLList = [0,0,0,0,0,0,0]
takerMissuXTime = 0
takerMissIVXTime = 0
takerMissuXCounter = 0
takerMissIVXCounter = 0
optTakerAveMissPnLList = [0,0,0,0,0,0,0]
optTakerMissuXTime = 0
optTakerMissIVXTime = 0
optTakerMissuXCounter = 0
optTakerMissIVXCounter = 0
futTakerAveMissPnLList = [0,0,0,0,0,0,0]
futTakerMissuXTime = 0
futTakerMissuXCounter = 0
takerAveMissPnLCounter = [0,0,0,0,0,0,0]
optTakerAveMissPnLCounter = [0,0,0,0,0,0,0]
futTakerAveMissPnLCounter = [0,0,0,0,0,0,0]

kickerAveHitPnLList = [0,0,0,0,0,0,0]
kickerHituXTime = 0
kickerHitIVXTime = 0
kickerHituXCounter = 0
kickerHitIVXCounter = 0
optKickerAveHitPnLList = [0,0,0,0,0,0,0]
optKickerHituXTime = 0
optKickerHitIVXTime = 0
optKickerHituXCounter = 0
optKickerHitIVXCounter = 0
futKickerAveHitPnLList = [0,0,0,0,0,0,0]
futKickerHituXTime = 0
futKickerHituXCounter = 0
kickerAveHitPnLCounter = [0,0,0,0,0,0,0]
optKickerAveHitPnLCounter = [0,0,0,0,0,0,0]
futKickerAveHitPnLCounter = [0,0,0,0,0,0,0]

kickerAveMissPnLList = [0,0,0,0,0,0,0]
kickerMissuXTime = 0
kickerMissIVXTime = 0
kickerMissuXCounter = 0
kickerMissIVXCounter = 0
optKickerAveMissPnLList = [0,0,0,0,0,0,0]
optKickerMissuXTime = 0
optKickerMissIVXTime = 0
optKickerMissuXCounter = 0
optKickerMissIVXCounter = 0
futKickerAveMissPnLList = [0,0,0,0,0,0,0]
futKickerMissuXTime = 0
futKickerMissuXCounter = 0
kickerAveMissPnLCounter = [0,0,0,0,0,0,0]
optKickerAveMissPnLCounter = [0,0,0,0,0,0,0]
futKickerAveMissPnLCounter = [0,0,0,0,0,0,0]

recordNumber = 0
orderType = ''
buySell = ''
endTime = datetime.now()


while currentDate <= endDate:
    
    orderList = []
    currentList = []
    cancelFillList = []
    makerList = []
    dataList = []
    crossList = []    
    
    
    if date.weekday(currentDate) == 5:
        currentDate = currentDate + timedelta(2)
    elif date.weekday(currentDate) == 6:
        currentDate = currentDate + timedelta(1)
    
#    if date.weekday(date.today()) in (0,1,2):
#        unzipDate = date.today() - timedelta(5)
#    elif date.weekday(date.today()) in (3,4):
#        unzipDate = date.today() - timedelta(3)
#    else:
#        print "****WEEKEND?****"
    
    if currentDate < date(2013,3,13):  
        pastPath = r"/Public2/Archive/AUPRODCTS09/" 
    elif currentDate >= date(2013,3,13) and currentDate < date(2013,4,26):
        pastPath = r"/Public2/Archive/AUPRODCTS17/"
    elif currentDate >= date(2013,4,26) and currentDate < date(2013,5,14):
        pastPath = r"/Public2/Archive/AUPRODCTS16/"
    elif currentDate >= date(2013,5,14):
        pastPath = r"/Public2/Archive/AUPRODCTS13/"
    
    if currentDate != date.today():
        if not os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat() + ".gz"):
            if not os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat()):
                currentDate = currentDate + timedelta(1)
                continue

    if currentDate == date.today():
        currentTime = datetime.time(datetime.now())
        if datetime.time(datetime.now()) >= time(13,14,45):
            qTime = "13:14:"
        else:
            if currentTime.second < 10:
                sec = "0"
            else:
                sec = ""
            if currentTime.minute < 10:
                m = "0"
            else:
                m = ""
            qTime = str(currentTime.hour) + ":" + m + str(currentTime.minute) + ":"
    
    elif currentDate < date(2013,4,8):
        qTime = " 13:5"
    else:
        qTime = ' 13:1' 
    print("\nAccessing all relevant files for " + str(currentDate) + " @ " + str(datetime.now()) + "\n")
    
    if currentDate == date.today():
        user = commands.getoutput('whoami')    
        print('\n')
        print("Run this script in production: \n")
        print("#1: cp /var/cts/Logs/KODBData.log  /home/" + user + "/KODBData.log; egrep 'FILL|ORDER CANCELLED' /var/cts/Logs/Orders.log > /home/" + user + "/orders.txt; " \
                "grep 'CANCEL REJECTED' /var/cts/Logs/Orders.log > /home/" + user + "/cancelFills.log;scp /home/" + user + "/KODBData.log /home/" + user + "/orders.txt /home/" + user + "/cancelFills.log eqctsutil02:/Public2/thansen/python/TradeAnalyzer;")
        print('\n')
        raw_input("Press 'Enter' when done")
        print('\n') 
        
  
    elif os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat()):
        commands.getoutput("cp " + pastPath + "KODBData.log." + currentDate.isoformat() + "  /Public2/thansen/python/TradeAnalyzer/KODBData.log; egrep 'FILL|ORDER CANCELLED' " \
                            + pastPath + "Orders.log." + currentDate.isoformat() + " > /Public2/thansen/python/TradeAnalyzer/orders.txt; grep 'CANCEL REJECTED' " \
                            + pastPath + "Orders.log." + currentDate.isoformat() + " > /Public2/thansen/python/TradeAnalyzer/cancelFills.log")
        
    elif os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat() + ".gz"):
        commands.getoutput("zcat " + pastPath + "KODBData.log." + currentDate.isoformat() + ".gz > /Public2/thansen/python/TradeAnalyzer/KODBData.log; " \
                            + "zcat " + pastPath + "Orders.log." + currentDate.isoformat() + ".gz |  egrep 'FILL|ORDER CANCELLED' > /Public2/thansen/python/TradeAnalyzer/orders.txt; " \
                            + "zcat " + pastPath + "Orders.log." + currentDate.isoformat() + ".gz | grep 'CANCEL REJECTED' > /Public2/thansen/python/TradeAnalyzer/cancelFills.log")
       
    commands.getoutput("grep 'MType=.*FILL' /Public2/thansen/python/TradeAnalyzer/KODBData.log > /Public2/thansen/python/TradeAnalyzer/makerData.txt; " + \
                        "grep ' Type= SENT' /Public2/thansen/python/TradeAnalyzer/KODBData.log  > /Public2/thansen/python/TradeAnalyzer/takerData.txt; " + \
                        "grep 'MType=.*SENT' /Public2/thansen/python/TradeAnalyzer/KODBData.log > /Public2/thansen/python/TradeAnalyzer/makerSentData.txt; " + \
                        "grep 'Type= T' /Public2/thansen/python/TradeAnalyzer/KODBData.log | grep MyVValid=1 | grep KMarketsValid=1 | grep -v ' MSP=0.0' > /Public2/thansen/python/TradeAnalyzer/PriceData.txt; " + \
                        "grep '" + str(qTime) + ".*INFO' /Public2/thansen/python/TradeAnalyzer/KODBData.log | grep MyVValid=1 > /Public2/thansen/python/TradeAnalyzer/currentData.txt")  
    
    
    priceFile = open( path + "PriceData.txt",'r')
    timeFile = open(path + "timeFile.txt", 'w')
      
    print("Processing KODBData records @ " + str(datetime.now()) + "\n")
    
    if currentDate >= date(2013,4,8):   
        closeTime = '19:15:00'
        for line in priceFile:
            RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}).*Symbol=([0-9A-Z_]+).*(\d{2}\:\d{2}\:\d{2}).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*MSP=([0-9.]+).*RiskVol=([0-9.]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*", line, re.M)
           
            match = RX_OptionMarket
            if match and match.group(1) == closeTime:
                break
            if match and (float(match.group(7)) != 0):
                matchTimeStamp = match.group(1)            
                symbol = match.group(2)
                transTime = match.group(3)
                uTV = match.group(4)
                mktBid = match.group(5)
                mktAsk = match.group(6)
                matchMSP = match.group(7)
                matchRiskVol = match.group(8)
                MyIV = match.group(9)
                theoIV = match.group(10)
                uMSP = match.group(11)
                
                if MyIV == 0:
                    matchIV = matchRiskVol
                else:
                    matchIV = MyIV
                    
                timeFile.write(symbol + ", " + matchTimeStamp + ", " + uTV + ", " + mktBid + ", " + mktAsk + ", " + uMSP + ", " + matchIV + ', ' + matchMSP + '\n')
                crossList.append([symbol, datetime.strptime(transTime, timeFormat1), matchIV, uMSP, uTV, theoIV])
    else:
        closeTime = '20:00:00'
        for line in priceFile:
            RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}).*Symbol=([0-9A-Z_]+).*(\d{2}\:\d{2}\:\d{2}).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*MSP=([0-9.]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*", line, re.M)
            match = RX_OptionMarket
            if match and match.group(1) == closeTime:
                break
            if match and (float(match.group(7)) != 0):
                matchTimeStamp = match.group(1)            
                symbol = match.group(2)
                transTime = match.group(3)
                uTV = match.group(4)
                mktBid = match.group(5)
                mktAsk = match.group(6)
                matchMSP = match.group(7)
                MyIV = match.group(8)
                theoIV = match.group(9)
                uMSP = match.group(10)
                    
                timeFile.write(symbol + ", " + matchTimeStamp + ", " + uTV + ", " + mktBid + ", " + mktAsk + ", " + uMSP + ", " + MyIV + ', ' + matchMSP + '\n')
                crossList.append([symbol, datetime.strptime(transTime, timeFormat1), MyIV, uMSP, uTV, theoIV])
    timeFile.close()
    priceFile.close()
   
    cancelFillFile = open(path + "cancelFills.log") 
    for line in cancelFillFile:
        RX_OptionMarket = re.match (".*#:\s([0-9]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            cancelFillList.append([match.group(1)])
    cancelFillFile.close()    
    
    
    orderFile = open(path + "orders.txt") 
    for line in orderFile:
        RX_OptionMarket = re.match (".*\:\s([A-Z]+).*(\d{4}\-\d{2}\-\d{2}).*(\d{2}\:\d{2}\:\d{2}).*\):\s([A-Z]+).*#:\s([0-9]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            orderList.append([match.group(1), match.group(3), match.group(5), match.group(4), match.group(2)])
    orderFile.close()   
                          
    takerFile = open( path + "takerData.txt",'r')
    
    for line in takerFile:
        RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}\.\d{3}).*Symbol=([0-9A-Z_]+).*\sType=([A-Z ]+).*Side=([A-Z]+).*OrderID=([0-9]+).*TransTime=.*(\d{2}\:\d{2}\:\d{2}).*OrderPrice=([0-9]+).*OrderSize=([0-9]+).*uTV=([0-9]+).*MktBid=([0-9]+).*" \
                                    + "MktAsk=([0-9]+).*Delta=([0-9.-]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*DaysToExp=([0-9.]+).*RiskBuy=([0-9-]+).*RiskSell=([0-9-]+).*TheoValue=([0-9]+).*KTBid=([0-9]+).*KTAsk=([0-9]+).*", line, re.M)          
        #RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}).*Symbol=([0-9A-Z_]+).*\sType=([A-Z ]+).*Side=([A-Z]+).*OrderID=([0-9]+).*TransTime=.*(\d{2}\:\d{2}\:\d{2}).*OrderPrice=([0-9]+).*OrderSize=([0-9]+).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*DaysToExp=([0-9.]+).*RiskBuy=([0-9-]+).*RiskSell=([0-9-]+).*TheoValue=([0-9]+).*KTBid=([0-9]+).*KTAsk=([0-9]+).*", line, re.M)    
        match = RX_OptionMarket
        if match:

            matchTimeStamp = match.group(1)            
            matchSymbol = match.group(2)
            matchType = match.group(3)
            matchSide = match.group(4)
            matchOrderID = match.group(5)
            matchTransTime =  match.group(6)
            matchOrderPrice =  match.group(7)
            matchOrderSize =  match.group(8)
            matchuTV =  match.group(9)
            matchMktBid =  match.group(10)
            matchMktAsk =  match.group(11)
            matchDelta = match.group(12)
            matchMyIV =  match.group(13)
            matchTheoIV =  float(match.group(14))
            matchuMSP =  match.group(15)
            matchDTE =  float(match.group(16)) / 252
            matchRiskBuy = match.group(17)
            matchRiskSell =  match.group(18)
            matchTheoValue =  match.group(19)
            matchKTBid =  match.group(20)
            matchKTAsk =  match.group(21)       
            
            dataList.append([matchSymbol, matchType, matchSide, matchOrderID, matchTransTime, matchOrderPrice, matchOrderSize, matchMktBid, matchMktAsk, matchRiskBuy, matchRiskSell, matchKTBid, matchKTAsk, 'T', matchMyIV, matchTheoIV, matchuMSP, matchTheoValue, matchuTV, matchTimeStamp, matchDTE, matchDelta])
    
    takerFile.close() 
    
    makerFile = open( path + "makerData.txt",'r')
    
    for line in makerFile:
        RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}\.\d{3}).*OrderID=([0-9]+).*TransTime=.*(\d{2}\:\d{2}\:\d{2}).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*Delta=([0-9.-]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*RiskBuy=([0-9-]+).*RiskSell=([0-9-]+).*TheoValue=([0-9]+).*KMBid=([0-9]+).*KMAsk=([0-9]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            matchTimeStamp = match.group(1)            
            matchOrderID = match.group(2)
            matchTransTime = match.group(3)
            matchuTV = match.group(4)
            matchMktBid = match.group(5)
            matchMktAsk = match.group(6)
            matchDelta = match.group(7)
            matchMyIV = match.group(8)
            matchTheoIV = match.group(9)
            matchuMSP = match.group(10)
            matchRiskBuy = match.group(11)
            matchRiskSell =  match.group(12)
            matchTheoValue =  match.group(13)
            matchKMBid =  match.group(14)
            matchKMAsk =  match.group(15) 
            makerList.append([matchOrderID, matchTransTime, matchuTV, matchMktBid, matchMktAsk, matchMyIV, matchTheoIV, matchuMSP, matchTheoValue, matchRiskBuy, matchRiskSell, matchKMBid, matchKMAsk, matchTimeStamp, matchDelta, 0])
    makerFile.close()
    
    makerSentFile = open( path + "makerSentData.txt",'r')
    
    for line in makerSentFile:
        RX_OptionMarket = re.match (".*Symbol=([0-9A-Z_]+).*\sType=([A-Z ]+).*Side=([A-Z]+).*OrderID=([0-9]+).*OrderPrice=([0-9]+).*OrderSize=([0-9]+).*DaysToExp=([0-9.]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            matchSymbol = match.group(1)
            matchType = match.group(2)
            matchSide = match.group(3)
            matchOrderID = match.group(4)
            matchOrderPrice = match.group(5)
            matchOrderSize = match.group(6)
            matchDTE =  float(match.group(7)) / 252
    
            for item in makerList:
                if item[0] == match.group(4):
                    matchTransTime = item[1]
                    matchuTV = item[2]
                    matchMktBid = item[3]
                    matchMktAsk = item[4]
                    matchMyIV = item[5]
                    matchTheoIV = item[6]
                    matchuMSP = item[7]
                    matchTheoValue =  item[8]
                    matchRiskBuy = item[9]
                    matchRiskSell = item[10]
                    matchKMBid = item[11]
                    matchKMAsk = item[12]
                    matchTimeStamp = item[13]
                    matchDelta = item[14]
                    
                    
                    dataList.append([matchSymbol, matchType, matchSide, matchOrderID, matchTransTime, matchOrderPrice, matchOrderSize, matchMktBid, matchMktAsk, matchRiskBuy, matchRiskSell, matchKMBid, matchKMAsk, 'M', matchMyIV, matchTheoIV, matchuMSP, matchTheoValue, matchuTV, matchTimeStamp, matchDTE, matchDelta, 0])
             
                    
    makerSentFile.close()
    
    currentFile = open( path + "currentData.txt",'r')

    
    if currentDate >= date(2013,4,8):     
        for line in currentFile:
            RX_OptionMarket = re.match (".*Symbol=([0-9A-Z_]+).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*\sMSP=([0-9.]+).*RiskVol=([0-9.]+).*MyIV=([0-9.]+).*uMSP=([0-9.]+).*TheoValue=([0-9]+).*", line, re.M)
            match = RX_OptionMarket
            if match:
                matchSymbol = match.group(1)
                matchuTV = float(match.group(2))
                matchMktBid = float(match.group(3))
                matchMktAsk = float(match.group(4))
                matchMSP = float(match.group(5)) 
                matchRiskVol = float(match.group(6))
                matchMyIV = float(match.group(7))
                matchuMSP = float(match.group(8))
                matchTheoVal = float(match.group(9))
                
                if matchMyIV == 0:
                    currentIV = matchRiskVol
                else:
                    currentIV = matchMyIV
                    
                currentList.append([matchSymbol, matchuTV, matchMktBid, matchMktAsk, matchMSP, matchuMSP, matchTheoVal, currentIV])
    else:   
            for line in currentFile:
                RX_OptionMarket = re.match (".*Symbol=([0-9A-Z_]+).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*\sMSP=([0-9.]+).*MyIV=([0-9.]+).*uMSP=([0-9.]+).*TheoValue=([0-9]+).*", line, re.M)
                match = RX_OptionMarket
                if match:
                    matchSymbol = match.group(1)
                    matchuTV = float(match.group(2))
                    matchMktBid = float(match.group(3))
                    matchMktAsk = float(match.group(4))
                    matchMSP = float(match.group(5)) 
                    matchMyIV = float(match.group(6))
                    matchuMSP = float(match.group(7))
                    matchTheoVal = float(match.group(8))
                    
    
                    currentIV = matchMyIV
                        
                    currentList.append([matchSymbol, matchuTV, matchMktBid, matchMktAsk, matchMSP, matchuMSP, matchTheoVal, currentIV])
        
    currentFile.close()
    
    
    print("Processing " + str(len(dataList)) + " records @ " + str(datetime.now()))    
    logFile.write("Processing " + str(len(dataList)) + " records")
    
    timeFile = open(path + "timeFile.txt", 'r')
    
   
    for item in dataList:
        ErrorTrade = ""
        riskTradeType = 0
        currentPrice = 'n/a'
        currentIV = 'n/a'
        currentuMSP = 'n/a'
        uXTime = 0
        ivXTime = 0
        timeuMSP = 0
        timeMyIV = 0
        timePriceList = []
        midPriceList = []
        timePnLList = []
        ivPriceTimeList = []
        uPriceTimeList = []
        theoPriceTimeList = []
        ivPnLList = []
        uPnLList = []
        theoPnLList = []
        dollarizer = dollarizerDict[item[0].split("_")[0]]
        cancelFill = False
        ktBid = float(item[11])
        ktAsk = float(item[12])
        orderPrice = float(item[5])
        orderID = item[3]
        uTV = float(item[18])
        theoVal = float(item[17])
        theoIV = float(item[15])
        makerTaker = item[13]
        myIV = float(item[14])
        uMSP = float(item[16])
        mktBid = float(item[7])
        mktAsk = float(item[8])
        symbol = item[0]
        buySell = item[2]
        executionTime = datetime.strptime(item[4], "%H:%M:%S")
        timeStamp = datetime.strptime(item[19], "%H:%M:%S.%f")
        xTime = datetime.combine(currentDate, time(timeStamp.hour, timeStamp.minute, timeStamp.second, timeStamp.microsecond))
        DTE = item[20]
        delta = float(item[21])
        midpoint = (mktAsk + mktBid) / 2
        futBias = 'error'
        volBias = 'error'
        orderDate = ""
        orderSize = 0
        uTVBSPrice = 0
        ivTVBSPrice = 0
        tradePnL = 0
        size = int(item[6])
    
        
        
        recordNumber += 1

        logFile.write("datalist: " + str(item))
        
        if '_' in item[0]:    
            symbolCPF = item[0].split("_")[1][0]
            strike = int(item[0].split("_")[1][1:])
        else:
            symbolCPF = 'F'
       
        
        if "KIST" in item[1].split(" ") or "KIBT" in item[1].split(" "):
            takerKicker += 1
            kicker = 1
        elif "KISM" in item[1].split(" ") or "KIBM" in item[1].split(" "):
            makerKicker += 1
            kicker = 1
        else:
            kicker = 0
            
        if '_' in item[0]:
            tradeType = 'O'
        else:
            tradeType = 'F'
        
        if makerTaker == 'T':    
            for line in orderList:
                if line[2] == item[3]:
                    orderType = line[0]
                    endTime = datetime.strptime(line[1], timeFormat1)   
                    logFile.write("orderList: " + str(line))
                    orderDate = line[4]
                    break
                
            if orderType == 'FILL':
                orderType = 'F'
            elif orderType == 'ORDER':
                orderType = 'C'
            else:
                orderType = 'X'
        elif makerTaker == 'M':
            for line in orderList:
                if line[2] == item[3]:
                    orderType = 'F'
                    endTime = datetime.strptime(line[1], timeFormat1)
                    logFile.write("orderList: " + str(line))
                    orderDate = line[4]
                    break
        for record in cancelFillList:
            if item[3] == record[0]:
                logFile.write("cancelFillList: " + str(record))
                cancelFill = True
                if makerTaker == 'T':
                    break
        
        
        riskBuy = float(item[9])
        riskSell = float(item[10])    
        
        if tradeType == 'O':
            for line in reversed(currentList):
                if line[0] == item[0]:
                    if line[4] != 0 and currentPrice == 'n/a':
                        currentPrice = line[4]
                    if line[7] != 0 and currentIV == 'n/a':
                        currentIV = line[7]
                    if line[5] != 0 and currentuMSP == 'n/a':
                        currentuMSP = line[5]
                    logFile.write("currentList: " + str(line))
                    if currentPrice != 'n/a' and currentIV != 'n/a' and currentuMSP != 'n/a':
                        break
#            print("utv " + symbolCPF + " " + str(uTV/1000) + " " + str(strike) + " " + str(DTE) + " " + str(myIV))
#            print("ivtv " + symbolCPF + " " + str(uMSP/1000) + " " + str(strike) + " " + str(DTE) + " " + str(theoIV) + "\n")
            
            if myIV != 0:
                uTVBSPrice = func.BS_Pricer(symbolCPF, (uTV/1000), strike, DTE, 0, myIV) * 1000
                mspBSPrice = func.BS_Pricer(symbolCPF, (uMSP/1000), strike, DTE, 0, myIV) * 1000
            else:
                uTVBSPrice = 'error'
                mspBSPrice = 'error'
                
            if theoIV != 0:
                ivTVBSPrice = func.BS_Pricer(symbolCPF, (uMSP/1000), strike, DTE, 0, theoIV) * 1000
                TVBSPrice = func.BS_Pricer(symbolCPF, (uTV/1000), strike, DTE, 0, theoIV) * 1000
            else:
                ivTVBSPrice = 'error'
                TVBSPrice = 'error'
            
#            print "IV", uMSP/1000, strike, currentIV
#            print "U", currentuMSP/1000, strike, myIV
            if currentIV != 0 and currentIV != 'n/a':
                currentIVPrice = func.BS_Pricer(symbolCPF, (uMSP/1000), strike, DTE, 0, currentIV) * 1000
            else:
                currentIVPrice = 'n/a'
            if not myIV == 0 and currentuMSP != 'n/a':
                currentUPrice = func.BS_Pricer(symbolCPF, (currentuMSP/1000), strike, DTE, 0, myIV) * 1000
            else:
                currentUPrice = 'n/a'
            if currentIV !=0 and currentIV != 'n/a' and currentuMSP != 'n/a':
                currentTheoPrice = func.BS_Pricer(symbolCPF, (currentuMSP/1000), strike, DTE, 0, currentIV) * 1000
            else:
                currentTheoPrice = 'n/a'

            
            
        elif tradeType == 'F':
            uTVBSPrice = 'n/a'
            ivTVBSPrice = 'n/a'
            currentUPrice = 'n/a'
            currentIVPrice = 'n/a'
            currentTheoPrice = 'n/a'
        
            
            for line in reversed(currentList): 
                if item[0] in line[0] and float(line[5]) != 0:
                    currentPrice = int(line[5])
                    break
        
        
        if riskBuy < 0:
            riskSide = "BUY"
        elif riskSell < 0:
            riskSide = "SELL"
        else:
            riskSide = "OTHER"
        
            
        
        for record in secondsAhead:
            midPriceList.append(getTimePrice(item[4], item[0], record, 0, currentDate, timeStamp))
        #if midPriceList[0] == midPriceList[6]:
      
        for (counter,record) in enumerate(midPriceList):    
            if tradeType == 'F':
                timePriceList.append(record[1])
                ivPriceTimeList = ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
                uPriceTimeList = ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
                theoPriceTimeList = ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
            elif tradeType == 'O':
                timePriceList.append(record[0])
                if not record[2] == -1 and not record[2] == 0:
#                    print "ivprice", uMSP, strike, DTE, record[2]
                    ivPriceTimeList.append(func.BS_Pricer(symbolCPF, (uMSP/1000), strike, DTE, 0, record[2]) * 1000)
                else:
                    ivPriceTimeList.append('n/a')  
                if not record[1] == -1 and not myIV == 0:
                    #print "uprice", uMSP, strike, DTE, record[1], myIV
                    uPriceTimeList.append(func.BS_Pricer(symbolCPF, (float(record[1])/1000), strike, DTE, 0, myIV) * 1000)
                else:
                    uPriceTimeList.append('n/a')
                if not record[1] == -1 and not record[2] == -1 and not record[2] == 0:
#                    print "uprice", uMSP, strike, DTE, record[1], myIV
                    theoPriceTimeList.append(func.BS_Pricer(symbolCPF, (float(record[1])/1000), strike, DTE, 0, record[2]) * 1000)
                else:
                    theoPriceTimeList.append('n/a')
        if tradeType == 'F':
            ivPnLList = ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
            uPnLList = ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
            theoPnLList = ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
        
            
        
        
        if buySell == 'BUY':
            BS = 1      
            orderSize = BS * int(item[6])  
            tradeDelta = delta * orderSize
            if not currentPrice == 'n/a':
                tradePnL = (currentPrice - orderPrice) * dollarizer

            else:
                tradePnL = 'n/a'
            for (counter, record) in enumerate(timePriceList):
                if record == -1:
                    timePnLList.append("N/A")
                else:
                    timePnLList.append((float(record) - orderPrice) * dollarizer)
            if tradeType == 'O':
                for record in ivPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        ivPnLList.append((float(record) - mspBSPrice) * dollarizer)
                    else:
                        ivPnLList.append('n/a')
                if not mspBSPrice == 'error':
                    xEdge  = (mspBSPrice - orderPrice) * dollarizer
                    TVEdge = (TVBSPrice - orderPrice) * dollarizer
                else:
                    xEdge = 'error'
                    TVEdge = 'error'
                    
                if not currentIVPrice == 'n/a'and mspBSPrice != 'error':
                    currentIVPnL = (currentIVPrice - mspBSPrice) * dollarizer
                else:
                    currentIVPnL = 'n/a'
                if not currentUPrice == 'n/a' and mspBSPrice != 'error':
                    currentUPnL = (currentUPrice - mspBSPrice) * dollarizer
                else:
                    currentUPnL = 'n/a'
                
                if not currentTheoPrice == 'n/a'and mspBSPrice != 'error':
                    currentTheoPnL = (currentTheoPrice - mspBSPrice) * dollarizer
                else:
                    currentTheoPnL = 'n/a'
                    
                for record in uPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        uPnLList.append((float(record) - mspBSPrice) * dollarizer)
                    else:
                        uPnLList.append('n/a')
                for record in theoPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        theoPnLList.append((float(record) - mspBSPrice) * dollarizer)
                    else:
                        theoPnLList.append('n/a')
                        
                        
                
#                    dataList.append([matchSymbol, matchType, matchSide, matchOrderID, matchTransTime, matchOrderPrice, matchOrderSize, matchMktBid, matchMktAsk, matchRiskBuy, matchRiskSell, matchKTBid, matchKTAsk, 'T', matchMyIV, matchTheoIV, matchuMSP, matchTheoValue, matchuTV, matchTimeStamp, matchDTE, matchDelta])
            
            elif tradeType == 'F':
                xEdge = (midpoint - orderPrice) * dollarizer
                TVEdge = (theoVal - orderPrice) * dollarizer
                currentIVPnL = 'n/a'
                currentUPnL = 'n/a'
                currentTheoPnL = 'n/a'
            if symbolCPF != 'F' and uTVBSPrice != 'error':
                uTVEdge =  (uTVBSPrice - mspBSPrice) * dollarizer
                ivTVEdge = (ivTVBSPrice - mspBSPrice) * dollarizer
                edgeCompare = ivTVEdge - uTVEdge
            else:
                uTVEdge = 'err'
                ivTVEdge = 'err'
                edgeCompare = 'err'
        elif buySell == 'SELL':
            BS = -1
            orderSize = BS * int(item[6])
            tradeDelta = orderSize * delta
            
            if not currentPrice == 'n/a':
                tradePnL = (orderPrice - currentPrice) * dollarizer
            else:
                tradePnL = 'n/a'
                    
            for (counter, record) in enumerate(timePriceList):
                if record == -1:
                    timePnLList.append("N/A")
                else:
                    timePnLList.append((orderPrice - float(record)) * dollarizer)
            if tradeType == 'O':
                for record in ivPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        ivPnLList.append((mspBSPrice - float(record)) * dollarizer)
                    else:
                        ivPnLList.append('n/a')
                if not mspBSPrice == 'error':
                    xEdge = (orderPrice - mspBSPrice) * dollarizer
                    TVEdge = (orderPrice - TVBSPrice) * dollarizer
                else:
                    xEdge = 'error'
                    TVEdge = 'error'
                for record in uPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        uPnLList.append((mspBSPrice - float(record)) * dollarizer)
                    else:
                        uPnLList.append('n/a')
                for record in theoPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        theoPnLList.append((mspBSPrice - float(record)) * dollarizer)
                    else:
                        theoPnLList.append('n/a')
                        
                
                if  currentIVPrice != 'n/a' and mspBSPrice != 'error': 
                    currentIVPnL = (mspBSPrice - currentIVPrice ) * dollarizer
                else:
                    currentIVPnL = 'n/a'    
                if currentUPrice != 'n/a' and mspBSPrice != 'error':
                    currentUPnL = (mspBSPrice - currentUPrice) * dollarizer
                else:
                    currentUPnL = 'n/a'
                if currentTheoPrice != 'n/a' and mspBSPrice != 'error':
                    currentTheoPnL = (mspBSPrice - currentTheoPrice) * dollarizer
                else:
                    currentTheoPnL = 'n/a'
                    
                    
            elif tradeType == 'F':
                xEdge = (orderPrice - midpoint) * dollarizer
                TVEdge = (orderPrice - theoVal) * dollarizer
                currentIVPnL = 'n/a'
                currentUPnL = 'n/a'
                currentTheoPnL = 'n/a'
            if symbolCPF != 'F' and uTVBSPrice != 'error':
                uTVEdge =  (mspBSPrice - uTVBSPrice) * dollarizer
                ivTVEdge =  (mspBSPrice - ivTVBSPrice) * dollarizer
                edgeCompare = (ivTVEdge - uTVEdge) * dollarizer
            else:
                uTVEdge = 'err'
                ivTVEdge = 'err'
                edgeCompare = 'err'
                    
        if symbolCPF == 'F':
            (uXTime, ivXTime, timeuMSP, timeMyIV) = getTVCross(executionTime, symbol, crossList, theoIV, theoVal, buySell, symbolCPF)
        else:
            (uXTime, ivXTime, timeuMSP, timeMyIV) = getTVCross(executionTime, symbol, crossList, theoIV, uTV, buySell, symbolCPF)
        
            
        if riskSide == item[2]:
             riskOnOff = "OFF"
        else:
             riskOnOff = "ON"
     
        
#        if tradeType == 'O' and orderType == 'F':
#            if 'LE' in symbol:
#                symbolMultiplier = 10
#            else:
#                symbolMultiplier = 1000
#            if currentDate != date.today():
#                if round(tradeDelta) >= 1:
#                    futMkt = getULMarket(xTime, symbol, currentDate)
#                    print "******* ", futMkt, uMSP, xTime
#                    dataList.append([futMkt[2], '', 'SELL', orderID, item[4], float(futMkt[0]) * symbolMultiplier, str(int(abs(round(tradeDelta)))), futMkt[0], futMkt[1], 0, 0, 0, 0, 'H', 0, 0, 0, 0, 0, item[19], 0, 0])
#                elif round(tradeDelta) <= -1:
#                    futMkt = getULMarket(xTime, symbol, currentDate)
#                    print "******* ", futMkt, uMSP, xTime
#                    dataList.append([futMkt[2], '', 'BUY', orderID, item[4], float(futMkt[1]) * symbolMultiplier, str(int(abs(round(tradeDelta)))), futMkt[0], futMkt[1], 0, 0, 0, 0, 'H', 0, 0, 0, 0, 0, item[19], 0, 0])
        
        
        if buySell == 'BUY':
            if riskSell < 0:
                riskTradeType = 1  # traded in spite of risk preference
            elif riskBuy < 0:
                if (ktBid + riskBuy) >= orderPrice:
                    riskTradeType = 2   #would have traded regardless
                elif (ktBid + riskBuy) < orderPrice:
                    riskTradeType = 3   # traded because of risk preference, would not have traded otherwise
                else:
                    riskTradeType = -1   # error
            elif riskBuy >= 0 and riskSell >= 0:
                riskTradeType = 4
            else:
                riskTradeType = -2   # error
                #print("risk buy: " + str(riskBuy) + " risk sell: " + str(riskSell) + " ktBid: " + str(ktBid) + " order price: " + str(orderPrice) + " " + str(buySell))
        elif buySell == 'SELL':
            if riskBuy < 0: 
                riskTradeType = 1
            elif riskSell < 0:
                if (ktAsk - riskSell) <= orderPrice:
                    riskTradeType = 2   #would have traded regardless
                elif (ktAsk - riskSell) > orderPrice:
                    riskTradeType = 3   # traded because of risk preference, would not have traded otherwise
                else:
                    riskTradeType = -1  # error
            elif riskBuy >= 0 and riskSell >= 0:
                riskTradeType = 4  # no or minimal risk adj
            else:
                riskTradeType = -2  # error       
                
        BADiff = ((int(item[8]) - int(item[7])) / 125)
        startTime = datetime.strptime(item[4], timeFormat1)
#        timeDiff = (endTime - startTime).microseconds
        timeDiff = 'n/a'
        
        
        
        if tradeType == 'F':
            if buySell == 'BUY':
                futBias = theoVal - midpoint
            elif buySell == 'SELL':
                futBias = midpoint - theoVal
            volBias = "fut"
                
        elif tradeType == 'O':
            if symbolCPF == 'C':
                if buySell == 'BUY':
                    futBias = uTV - uMSP
                    volBias = theoIV - myIV
                if buySell == 'SELL':
                    futBias = uMSP - uTV
                    volBias = myIV - theoIV
            elif symbolCPF == 'P':
                if buySell == 'BUY':
                    futBias = uMSP - uTV
                    volBias = theoIV - myIV
                if buySell == 'SELL':
                    futBias = uTV - uMSP
                    volBias = myIV - theoIV
        
           
        if orderType == 'F':
            if makerTaker == 'T':
                takerFills += 1
                if kicker == 1:
                    takerKickerHit += 1   
                    if tradeType == 'F':
                        takerKickerFutureHit += 1
                    elif tradeType == 'O':
                        takerKickerOptionHit += 1
            if tradeType == 'F':
                if makerTaker == 'M':
                    makerFuturesFills += 1
                    makerFuturesQty += size
                    futMakerKicker += 1
                elif makerTaker == 'T':
                    takerFuturesFills += 1
                    takerFuturesQty += size
                totalFuturesQty += size
            elif tradeType == 'O':   
                if makerTaker == 'M':
                    makerOptionsFills += 1
                    makerOptionsQty += size
                    optMakerKicker += 1
                elif makerTaker == 'T':
                    takerOptionsFills += 1
                    takerOptionsQty += size
                TotalOptionsQty += size
        elif orderType == 'C':
            if makerTaker == 'T':
                takerMiss += 1
            if kicker == 1: 
                takerKickerMiss += 1
                if tradeType == 'F':
                    takerKickerFutureMiss += 1
                elif tradeType == 'O':
                    takerKickerOptionMiss += 1
            if tradeType == 'F':
                takerFuturesMiss += 1
            elif tradeType == 'O':
                takerOptionsMiss += 1
    
        if makerTaker == "M":
            if orderType == "F":
                if uXTime != -1:
                    makeruXTime = makeruXTime + uXTime
                    makeruXCounter += 1
                if ivXTime != -1:
                    makerIVXTime = makerIVXTime + ivXTime
                    makerIVXCounter += 1
                if tradeType == 'O':
                    if uXTime != -1:    
                        optMakeruXTime = optMakeruXTime + uXTime
                        optMakeruXCounter += 1
                    if ivXTime != -1:
                        optMakerIVXTime = optMakerIVXTime + ivXTime
                        optMakerIVXCounter += 1
                elif tradeType == 'F':
                    if uXTime != -1:    
                        futMakeruXTime = futMakeruXTime + uXTime
                        futMakeruXCounter += 1

                for (counter, record) in enumerate(timePriceList):
                    if record != -1:
                        if len(makerAvePnLList) < 7: 
                            makerAvePnLList.append(timePnLList[counter]) 
                            makerAvePnLCounter.append(1)
                        else:
                            makerAvePnLList[counter] += timePnLList[counter]
                            makerAvePnLCounter[counter] += 1                        
                        
                        if tradeType == 'O':
                            if len(optMakerAvePnLList) < 7: 
                                optMakerAvePnLList.append(timePnLList[counter]) 
                                optMakerAvePnLCounter.append(1)
                            else:
                                optMakerAvePnLList[counter] += timePnLList[counter]
                                optMakerAvePnLCounter[counter] += 1
                            
                            
                        elif tradeType == 'F':
                            if len(futMakerAvePnLList) < 7: 
                                futMakerAvePnLList.append(timePnLList[counter]) 
                                futMakerAvePnLCounter.append(1)
                            else:
                                futMakerAvePnLList[counter] += timePnLList[counter]
                                futMakerAvePnLCounter[counter] += 1
                            
                            
        elif makerTaker == 'T':
            if orderType == "F":
                if uXTime != -1:
                    takerHituXTime = takerHituXTime + uXTime
                    takerHituXCounter += 1
                if ivXTime != -1:
                    takerHitIVXTime = takerHitIVXTime + ivXTime
                    takerHitIVXCounter += 1
                if tradeType == 'O':
                    if uXTime != -1:    
                        optTakerHituXTime = optTakerHituXTime + uXTime
                        optTakerHituXCounter += 1
                    if ivXTime != -1:
                        optTakerHitIVXTime = optTakerHitIVXTime + ivXTime
                        optTakerHitIVXCounter += 1
                elif tradeType == 'F':
                    if uXTime != -1:    
                        futTakerHituXTime = futTakerHituXTime + uXTime
                        futTakerHituXCounter += 1
                    
                for (counter, record) in enumerate(timePriceList):
                    if record != -1:
                        if len(takerAveHitPnLList) < 7: 
                            takerAveHitPnLList.append(timePnLList[counter])  
                            takerAveHitPnLCounter.append(1)
                        else:
                            takerAveHitPnLList[counter] += timePnLList[counter]
                            takerAveHitPnLCounter[counter] += 1

                            
                        if tradeType == 'O':
                            if len(optTakerAveHitPnLList) < 7: 
                                optTakerAveHitPnLList.append(timePnLList[counter]) 
                                optTakerAveHitPnLCounter.append(1)
                            else:
                                optTakerAveHitPnLList[counter] += timePnLList[counter]
                                optTakerAveHitPnLCounter[counter] += 1

                            
                        elif tradeType == 'F':
                            if len(futTakerAveHitPnLList) < 7: 
                                futTakerAveHitPnLList.append(timePnLList[counter]) 
                                futTakerAveHitPnLCounter.append(1)
                            else:
                                futTakerAveHitPnLList[counter] += timePnLList[counter]
                                futTakerAveHitPnLCounter[counter] += 1

                    
            if kicker == 1 and orderType == "F":
                if uXTime != -1:
                    kickerHituXTime = kickerHituXTime + uXTime
                    kickerHituXCounter += 1
                if ivXTime != -1:
                    kickerHitIVXTime = kickerHitIVXTime + ivXTime
                    kickerHitIVXCounter += 1
                if tradeType == 'O':
                    if uXTime != -1:    
                        optKickerHituXTime = optKickerHituXTime + uXTime
                        optKickerHituXCounter += 1
                    if ivXTime != -1:
                        optKickerHitIVXTime = optKickerHitIVXTime + ivXTime
                        optKickerHitIVXCounter += 1
                if tradeType == 'F':
                    if uXTime != -1:    
                        futKickerHituXTime = futKickerHituXTime + uXTime
                        futKickerHituXCounter += 1
                        
                for (counter, record) in enumerate(timePriceList):
                    if record != -1:
                        if len(kickerAveHitPnLList) < 7: 
                            kickerAveHitPnLList.append(timePnLList[counter])
                            kickerAveHitPnLCounter.append(1)
                        else:
                            kickerAveHitPnLList[counter] += timePnLList[counter]
                            kickerAveHitPnLCounter[counter] += 1
                        
                        if tradeType == 'O':
                            if len(optKickerAveHitPnLList) < 7: 
                                optKickerAveHitPnLList.append(timePnLList[counter]) 
                                optKickerAveHitPnLCounter.append(1)
                            else:
                                optKickerAveHitPnLList[counter] += timePnLList[counter]
                                optKickerAveHitPnLCounter[counter] += 1
                            
                        elif tradeType == 'F':
                            if len(futKickerAveHitPnLList) < 7: 
                                futKickerAveHitPnLList.append(timePnLList[counter]) 
                                futKickerAveHitPnLCounter.append(1)
                            else:
                                futKickerAveHitPnLList[counter] += timePnLList[counter]
                                futKickerAveHitPnLCounter[counter] += 1
                                              
            if orderType == "C":
                if uXTime != -1:
                    takerMissuXTime = takerMissuXTime + uXTime
                    takerMissuXCounter += 1
                if ivXTime != -1:
                    takerMissIVXTime = takerMissIVXTime + ivXTime
                    takerMissIVXCounter += 1
                if tradeType == 'O':
                    if uXTime != -1:    
                        optTakerMissuXTime = optTakerMissuXTime + uXTime
                        optTakerMissuXCounter += 1
                    if ivXTime != -1:
                        optTakerMissIVXTime = optTakerMissIVXTime + ivXTime
                        optTakerMissIVXCounter += 1
                elif tradeType == 'F':
                    if uXTime != -1:    
                        futTakerMissuXTime = futTakerMissuXTime + uXTime
                        futTakerMissuXCounter += 1 
                        
                for (counter, record) in enumerate(timePriceList):
                    if record != -1:
                        if len(takerAveMissPnLList) < 7: 
                            takerAveMissPnLList.append(timePnLList[counter]) 
                            takerAveMissPnLCounter.append(1)
                        else:
                            takerAveMissPnLList[counter] += timePnLList[counter]   
                            takerAveMissPnLCounter[counter] += 1
                            
                        if tradeType == 'O':
                            if len(optTakerAveMissPnLList) < 7: 
                                optTakerAveMissPnLList.append(timePnLList[counter]) 
                                optTakerAveMissPnLCounter.append(1)
                            else:
                                optTakerAveMissPnLList[counter] += timePnLList[counter]
                                optTakerAveMissPnLCounter[counter] += 1             
                            
                        elif tradeType == 'F':
                            if len(futTakerAveMissPnLList) < 7: 
                                futTakerAveMissPnLList.append(timePnLList[counter]) 
                                futTakerAveMissPnLCounter.append(1)
                            else:
                                futTakerAveMissPnLList[counter] += timePnLList[counter]
                                futTakerAveMissPnLCounter[counter] += 1

    
                    
            if kicker == 1 and orderType == "C":
                if uXTime != -1:
                    kickerMissuXTime = kickerMissuXTime + uXTime
                    kickerMissuXCounter += 1
                if ivXTime != -1:    
                    kickerMissIVXTime = kickerMissIVXTime + ivXTime
                    kickerMissIVXCounter += 1
                if tradeType == 'O':
                    if uXTime != -1:    
                        optKickerMissuXTime = optKickerMissuXTime + uXTime
                        optKickerMissuXCounter += 1
                    if ivXTime != -1:
                        optKickerMissIVXTime = optKickerMissIVXTime + ivXTime
                        optKickerMissIVXCounter += 1
                elif tradeType == 'F':
                    if uXTime != -1:     
                        futKickerMissuXTime = futKickerMissuXTime + uXTime
                        futKickerMissuXCounter += 1
                
                for (counter, record) in enumerate(timePriceList):
                    if record != -1:
                        
                        if len(kickerAveMissPnLList) < 7: 
                            kickerAveMissPnLList.append(timePnLList[counter]) 
                            kickerAveMissPnLCounter.append(1)
                        else:
                            kickerAveMissPnLList[counter] += timePnLList[counter]
                            kickerAveMissPnLCounter[counter] += 1
                    
                        if tradeType == 'O':
                            if len(optKickerAveMissPnLList) < 7: 
                                optKickerAveMissPnLList.append(timePnLList[counter]) 
                                optKickerAveMissPnLCounter.append(1)
                            else:
                                optKickerAveMissPnLList[counter] += timePnLList[counter]
                                optKickerAveMissPnLCounter[counter] += 1
                            
                        elif tradeType == 'F':
                            if len(futKickerAveMissPnLList) < 7: 
                                futKickerAveMissPnLList.append(timePnLList[counter]) 
                                futKickerAveMissPnLCounter.append(1)
                            else:
                                futKickerAveMissPnLList[counter] += timePnLList[counter]
                                futKickerAveMissPnLCounter[counter] += 1
                                
        if tradeType == 'F':
            uTV = theoVal
            uMSP = midpoint
            
#        print "1", theoPnLList
#        print "2", ivPnLList
#        print "3", uPnLList

        
        outputFile.write(str(orderDate) + '\t' + str(item[4]) + '\t' + str(item[0]) + '\t' + str(orderID) + '\t'  + str(tradeType) + "\t" + str(orderType) + '\t' + str(makerTaker) + '\t' + str(kicker) + '\t' + str(orderSize) \
                + '\t' + str(item[5]) + '\t' + str(currentPrice) + '\t' + str(tradePnL) + '\t' + str(currentTheoPnL) + '\t' + str(currentIVPnL) + '\t' + str(currentUPnL) + '\t' + str(timePnLList[0]) + "\t" + str(timePnLList[1]) + "\t" + str(timePnLList[2]) + "\t" \
                + str(timePnLList[3]) + "\t" + str(timePnLList[4]) + "\t" + str(timePnLList[5]) + "\t" + str(timePnLList[6]) + "\t" + str(xEdge) + '\t' + str(TVEdge) + '\t' + str(BADiff) + '\t' + str(timeDiff) + '\t' + str(cancelFill) \
                + '\t' + str(riskOnOff) +  '\t' + str(riskTradeType) +  '\t' + str(futBias) +  '\t' + str(volBias) + '\t' + str(uXTime) + '\t' + str(ivXTime) + '\t' + str(timeuMSP) + '\t' + str(timeMyIV) + '\t' + str(uMSP) + '\t' + str(uTV) \
                + '\t' + str(theoIV) + '\t' + str(myIV) + '\t' + str(midpoint) + '\t' + str(ivTVEdge) + '\t' + str(uTVEdge) + '\t' + str(edgeCompare) + '\t' + str(ivPnLList[0]) + '\t' + str(ivPnLList[1]) + '\t' + str(ivPnLList[2]) \
                + '\t' + str(ivPnLList[3]) + '\t' + str(ivPnLList[4]) + '\t' + str(ivPnLList[5]) + '\t' + str(ivPnLList[6]) + '\t' + str(uPnLList[0]) + '\t' + str(uPnLList[1]) + '\t' + str(uPnLList[2]) + '\t' + str(uPnLList[3]) + '\t' + str(uPnLList[4]) \
                + '\t' + str(uPnLList[5]) + '\t' + str(uPnLList[6]) + '\t' + str(theoPnLList[0]) + '\t'  + str(theoPnLList[1]) + '\t'  + str(theoPnLList[2]) + '\t'  + str(theoPnLList[3]) + '\t'  + str(theoPnLList[4]) + '\t'  + str(theoPnLList[5]) + '\t'  + str(theoPnLList[6]) + '\n')
        
        
        logFile.write(str(orderDate) + '\t' + str(item[4]) + '\t' + str(item[0]) + '\t' + str(orderID) + '\t'  + str(tradeType) + "\t" + str(orderType) + '\t' + str(makerTaker) + '\t' + str(kicker) + '\t' + str(orderSize) \
                + '\t' + str(item[5]) + '\t' + str(currentPrice) + '\t' + str(tradePnL) + '\t' + str(currentTheoPnL) + '\t' + str(currentIVPnL) + '\t' + str(currentUPnL) + '\t' + str(timePnLList[0]) + "\t" + str(timePnLList[1]) + "\t" + str(timePnLList[2]) + "\t" \
                + str(timePnLList[3]) + "\t" + str(timePnLList[4]) + "\t" + str(timePnLList[5]) + "\t" + str(timePnLList[6]) + "\t" + str(xEdge) + '\t' + str(TVEdge) + '\t' + str(BADiff) + '\t' + str(timeDiff) + '\t' \
                + str(cancelFill) + '\t' + str(riskOnOff) +  '\t' + str(riskTradeType) +  '\t' + str(futBias) +  '\t' + str(volBias) + '\t' + str(uXTime) + '\t' + str(ivXTime) + '\t' + str(timeuMSP) + '\t' + str(timeMyIV) \
                + '\t' + str(uMSP) + '\t' + str(uTV) + '\t' + str(theoIV) + '\t' + str(myIV) + '\t' + str(midpoint) + '\t' + str(ivTVEdge) + '\t' + str(uTVEdge) + '\t' + str(edgeCompare) + '\t' + str(ivPnLList[0]) + '\t' + str(ivPnLList[1]) \
                + '\t' + str(ivPnLList[2]) + '\t' + str(ivPnLList[3]) + '\t' + str(ivPnLList[4]) + '\t' + str(ivPnLList[5]) + '\t' + str(ivPnLList[6]) + '\t' + str(uPnLList[0]) + '\t' + str(uPnLList[1]) + '\t' + str(uPnLList[2]) + '\t' \
                + str(uPnLList[3]) + '\t' + str(uPnLList[4]) + '\t' + str(uPnLList[5]) + '\t' + str(uPnLList[6]) + '\t' + str(theoPnLList[0]) + '\t'  + str(theoPnLList[1]) + '\t'  + str(theoPnLList[2]) + '\t'  + str(theoPnLList[3]) + '\t'  + str(theoPnLList[4]) + '\t'  + str(theoPnLList[5]) + '\t'  + str(theoPnLList[6]) + '\n')
    timeFile.close()
    currentDate = currentDate + timedelta(1)
 
outputFile.close()  
logFile.close() 
    
    
print("\n")
print("Total Futures Traded: " + str(totalFuturesQty) + "  Total Options Traded: " + str(TotalOptionsQty) + '\n')
print("Taker Futures Qty: " + str(takerFuturesQty) + "  Taker Options Qty: " + str(takerOptionsQty))
print("Taker Futures Fills: " + str(takerFuturesFills) + "  Taker Options Fills: " + str(takerOptionsFills))
print("Taker Fills : " + str(takerFills) + "  Taker Cancels : " + str(takerMiss))
print("Taker Option Fills: " + str(takerOptionsFills) + " Taker Option Misses: " + str(takerOptionsMiss))
print("Taker Futures Fills: " + str(takerFuturesFills) + " Taker Futures Misses: " + str(takerFuturesMiss))
print("Taker Kick-In Fills: " + str(takerKickerHit) + "  Taker Kick-In Cancels: " + str(takerKickerMiss) + '\n')
print("Taker Kick-In Option Fills: " + str(takerKickerOptionHit) + "  Taker Kick-In Option Cancels: " + str(takerKickerOptionMiss) + '\n')
print("Taker Kick-In Future Fills: " + str(takerKickerFutureHit) + "  Taker Kick-In Future Cancels: " + str(takerKickerFutureMiss) + '\n')
print("Maker Futures Qty: " + str(makerFuturesQty) + "  Maker Options Qty: " + str(makerOptionsQty))
print("Maker Futures Fills: " + str(makerFuturesFills) + "  Maker Options Fills: " + str(makerOptionsFills) + '\n')
print("Maker Futures Kick-in Fills: " + str(futMakerKicker) + "  Maker Options Kick-in Fills: " + str(optMakerKicker) + '\n')



#print(str(makerAvePnLList[0] / makerAvePnLCounter[0]) + '\t' + str(makerAvePnLList[1] / makerAvePnLCounter[1]) + '\t' + str(makerAvePnLList[2] / makerAvePnLCounter[2]) + '\t' + str(makerAvePnLList[3] / makerAvePnLCounter[3])\
#        + '\t' + str(makerAvePnLList[4] / makerAvePnLCounter[4]) + '\t' + str(makerAvePnLList[5] / makerAvePnLCounter[5]) + '\t' + str(makerAvePnLList[6] / makerAvePnLCounter[6]) + '\t' + str(takerAveHitPnLList[0] / takerAveHitPnLCounter[0]) \
#        + '\t' + str(takerAveHitPnLList[1] / takerAveHitPnLCounter[1]) + '\t' + str(takerAveHitPnLList[2] / takerAveHitPnLCounter[2]) + '\t' + str(takerAveHitPnLList[3] / takerAveHitPnLCounter[3]) \
#        + '\t' + str(takerAveHitPnLList[4] / takerAveHitPnLCounter[4]) + '\t' + str(takerAveHitPnLList[5] / takerAveHitPnLCounter[5]) + '\t' + str(takerAveHitPnLList[6] / takerAveHitPnLCounter[6]) + '\t' + str(takerAveMissPnLList[0] / takerAveMissPnLCounter[0]) \
#        + '\t' + str(takerAveMissPnLList[1] / takerAveMissPnLCounter[1]) + '\t' + str(takerAveMissPnLList[2] / takerAveMissPnLCounter[2]) + '\t' + str(takerAveMissPnLList[3] / takerAveMissPnLCounter[3]) \
#        + '\t' + str(takerAveMissPnLList[4] / takerAveMissPnLCounter[4]) + '\t' + str(takerAveMissPnLList[5] / takerAveMissPnLCounter[5]) + '\t' + str(takerAveMissPnLList[6] / takerAveMissPnLCounter[6]) + '\t' + str(kickerAveHitPnLList[0] / kickerAveHitPnLCounter[0]) \
#        + '\t' + str(kickerAveHitPnLList[1] / kickerAveHitPnLCounter[1]) + '\t' + str(kickerAveHitPnLList[2] / kickerAveHitPnLCounter[2]) + '\t' + str(kickerAveHitPnLList[3] / kickerAveHitPnLCounter[3]) \
#        + '\t' + str(kickerAveHitPnLList[4] / kickerAveHitPnLCounter[4]) + '\t' + str(kickerAveHitPnLList[5] / kickerAveHitPnLCounter[5]) + '\t' + str(kickerAveHitPnLList[6] / kickerAveHitPnLCounter[6]) + '\t' + str(kickerAveMissPnLList[0] / kickerAveMissPnLCounter[0]) \
#        + '\t' + str(kickerAveMissPnLList[1] / kickerAveMissPnLCounter[1]) + '\t' + str(kickerAveMissPnLList[2] / kickerAveMissPnLCounter[2]) + '\t' + str(kickerAveMissPnLList[3] / kickerAveMissPnLCounter[3]) \
#        + '\t' + str(kickerAveMissPnLList[4] / kickerAveMissPnLCounter[4]) + '\t' + str(kickerAveMissPnLList[5] / kickerAveMissPnLCounter[5])  + '\t' + str(kickerAveMissPnLList[6] / kickerAveMissPnLCounter[6]))

sumOutputFile = open(path + "sumOutput.txt", "w")

for (i, item) in enumerate(makerAvePnLList):
    if makerAvePnLCounter[i] != 0:    
        sumOutputFile.write(str(item / makerAvePnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')        
if makeruXCounter != 0 and makerIVXCounter != 0: 
    sumOutputFile.write(str((makeruXTime / makeruXCounter)) + '\t' + str((makerIVXTime / makerIVXCounter)) + '\t' + str(makerAvePnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(makerAvePnLCounter[0]) + '\t')
    
for (i, item) in enumerate(optMakerAvePnLList):
    if optMakerAvePnLCounter[i] != 0:    
        sumOutputFile.write(str(item / optMakerAvePnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if optMakeruXCounter != 0 and optMakerIVXCounter != 0: 
    sumOutputFile.write(str((optMakeruXTime / optMakeruXCounter)) + '\t' + str((optMakerIVXTime / optMakerIVXCounter)) + '\t'+ str(optMakerAvePnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(optMakerAvePnLCounter[0]) + '\t')

for (i, item) in enumerate(futMakerAvePnLList):
    if futMakerAvePnLCounter[i] != 0:    
        sumOutputFile.write(str(item / futMakerAvePnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if futMakeruXCounter != 0: 
    sumOutputFile.write(str((futMakeruXTime / futMakeruXCounter)) + '\t' + str(0) + '\t'+ str(futMakerAvePnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(futMakerAvePnLCounter[0]) + '\t')
        
for (i, item) in enumerate(takerAveHitPnLList):
    if takerAveHitPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / takerAveHitPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if takerHituXCounter != 0 and takerHitIVXCounter != 0: 
    sumOutputFile.write(str((takerHituXTime / takerHituXCounter)) + '\t' + str((takerHitIVXTime / takerHitIVXCounter)) + '\t'+ str(takerAveHitPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(takerAveHitPnLCounter[0]) + '\t')
        
for (i, item) in enumerate(optTakerAveHitPnLList):
    if optTakerAveHitPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / optTakerAveHitPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if optTakerHituXCounter != 0 and optTakerHitIVXCounter != 0: 
    sumOutputFile.write(str((optTakerHituXTime / optTakerHituXCounter)) + '\t' + str((optTakerHitIVXTime / optTakerHitIVXCounter)) + '\t'+ str(optTakerAveHitPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(optTakerAveHitPnLCounter[0]) + '\t')
        
for (i, item) in enumerate(futTakerAveHitPnLList):
    if futTakerAveHitPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / futTakerAveHitPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if futTakerHituXCounter != 0: 
    sumOutputFile.write(str((futTakerHituXTime / futTakerHituXCounter)) + '\t' +str(0) + '\t'+ str(futTakerAveHitPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(futTakerAveHitPnLCounter[0]) + '\t')

for (i, item) in enumerate(takerAveMissPnLList):
    if takerAveMissPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / takerAveMissPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if takerMissuXCounter != 0 and takerMissIVXCounter != 0: 
    sumOutputFile.write(str((takerMissuXTime / takerMissuXCounter)) + '\t' + str((takerMissIVXTime / takerMissIVXCounter)) + '\t'+ str(takerAveMissPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(takerAveMissPnLCounter[0]) + '\t')
        
for (i, item) in enumerate(optTakerAveMissPnLList):
    if optTakerAveMissPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / optTakerAveMissPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if optTakerMissuXCounter != 0 and optTakerMissIVXCounter != 0: 
    sumOutputFile.write(str((optTakerMissuXTime / optTakerMissuXCounter)) + '\t' + str((optTakerMissIVXTime / optTakerMissIVXCounter)) + '\t'+ str(optTakerAveMissPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(optTakerAveMissPnLCounter[0]) + '\t')

for (i, item) in enumerate(futTakerAveMissPnLList):
    if futTakerAveMissPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / futTakerAveMissPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if futTakerMissuXCounter != 0: 
    sumOutputFile.write(str((futTakerMissuXTime / futTakerMissuXCounter)) + '\t' + str(0) + '\t'+ str(futTakerAveMissPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(futTakerAveMissPnLCounter[0]) + '\t')
        
for (i, item) in enumerate(kickerAveHitPnLList):
    if kickerAveHitPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / kickerAveHitPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if kickerHituXCounter != 0 and kickerHitIVXCounter != 0: 
    sumOutputFile.write(str((kickerHituXTime / kickerHituXCounter)) + '\t' + str((kickerHitIVXTime /kickerHitIVXCounter)) + '\t'+ str(kickerAveHitPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(kickerAveHitPnLCounter[0]) + '\t')
        
for (i, item) in enumerate(optKickerAveHitPnLList):
    if optKickerAveHitPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / optKickerAveHitPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if optKickerHituXCounter != 0 and optKickerHitIVXCounter != 0: 
    sumOutputFile.write(str((optKickerHituXTime / optKickerHituXCounter)) + '\t' + str((optKickerHitIVXTime / optKickerHitIVXCounter)) + '\t'+ str(optKickerAveHitPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(optKickerAveHitPnLCounter[0]) + '\t')

for (i, item) in enumerate(futKickerAveHitPnLList):
    if futKickerAveHitPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / futKickerAveHitPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if futKickerHituXCounter != 0: 
    sumOutputFile.write(str((futKickerHituXTime / futKickerHituXCounter)) + '\t' + str(0) + '\t'+ str(futKickerAveHitPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(futKickerAveHitPnLCounter[0]) + '\t')
        
for (i, item) in enumerate(kickerAveMissPnLList):
    if kickerAveMissPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / kickerAveMissPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if kickerMissuXCounter != 0 and kickerMissIVXCounter != 0: 
    sumOutputFile.write(str((kickerMissuXTime / kickerMissuXCounter)) + '\t' + str((kickerMissIVXTime / kickerMissIVXCounter)) + '\t'+ str(kickerAveMissPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(kickerAveMissPnLCounter[0]) + '\t')
        
for (i, item) in enumerate(optKickerAveMissPnLList):
    if optKickerAveMissPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / optKickerAveMissPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if optKickerMissuXCounter != 0 and optKickerMissIVXCounter != 0: 
    sumOutputFile.write(str((optKickerMissuXTime / optKickerMissuXCounter)) + '\t' + str((optKickerMissIVXTime / optKickerMissIVXCounter)) + '\t'+ str(optKickerAveMissPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(optKickerAveMissPnLCounter[0]) + '\t')

for (i, item) in enumerate(futKickerAveMissPnLList):
    if futKickerAveMissPnLCounter[i] != 0:    
        sumOutputFile.write(str(item / futKickerAveMissPnLCounter[i]) + '\t')
    else:
        sumOutputFile.write('0' + '\t')
if futKickerMissuXCounter != 0: 
    sumOutputFile.write(str((futKickerMissuXTime / futKickerMissuXCounter)) + '\t' + str(0) + '\t'+ str(futKickerAveMissPnLCounter[0]) + '\t')
else:
    sumOutputFile.write('0' + '\t' + '0' + '\t'+ str(futKickerAveMissPnLCounter[0]) + '\t')
    
#for (i, item) in enumerate(ivPnLList)
    
sumOutputFile.close()

print("Paste output file (/Public2/thansen/python/TradeAnalyzer/output.txt) into Excel.\n")

        
    
  
  
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

