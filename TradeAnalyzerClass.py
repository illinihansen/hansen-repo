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


class Order():
    def __init__(self, datalist):
        self.symbol = datalist[0]        
        self.buySell = datalist[2]
        self.orderID = datalist[3]
        self.executionTime = datetime.strptime(datalist[4], "%H:%M:%S")
        self.orderPrice = float(datalist[5])  
        self.size = int(datalist[6])
        self.mktBid = float(datalist[7])
        self.mktAsk = float(datalist[8])
        self.ktBid = float(datalist[11])
        self.ktAsk = float(datalist[12])
        self.makerTaker = datalist[13]
        self.myIV = float(datalist[14])
        self.theoIV = float(datalist[15])
        self.uMSP = float(datalist[16])
        self.theoVal = float(datalist[17])
        self.uTV = float(datalist[18])
        self,timeStamp = datetime.strptime(datalist[19], "%H:%M:%S.%f")
        self.DTE = datalist[20]
        self.delta = float(datalist[21])
        self.orderDate = float(datalist[23])
        
        
        
        
        
      

timeFormat = "%H:%M:%S.%f"
timeFormat1 = "%H:%M:%S"
secondsAhead = [15,30,60,120,180,300, 600] 
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
        if endDate >= date(2013,7,29):
            serverID = raw_input("Are we analyzing ES trades? (y/n): ")
        else:
            serverID = 'n'
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
    serverID = raw_input("Are we analyzing ES trades? (y/n): ")


currentDate = startDate
outputFile = open(path + "output.txt", "w")
outputFile.write("Date\tTime\tSymbol\tOrderID\tTradeType\tF/C\tM/T\tKicker\tSize\tPrice\tCurrPrice\tPnLPerContract\tCurrTheoPnL\tCurrIVPnL\tCurrUPnL\txtraEdge\tTVEdge\tTTC\tSpeed(uSec)\tCancelFill\tRiskOnOff\tRiskTradeType\tFutBias\tVolBias\tuMSP\tuTV\tTheoIV\tMyIV\tuMidpoint\tivEdge$\tuEdge$\tEdgeCompare\n")
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
        pastPath = r"/Public2/Archive/AUPRODCTS17/"
        
    if serverID == 'y':
        pastPath = r"/Public2/Archive/AUPRODCTS13/"
    
    if currentDate != date.today():
        if not os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat() + ".gz"):
            if not os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat()):
                currentDate = currentDate + timedelta(1)
                continue

    if currentDate == date.today():
        
        currentTime = datetime.time(datetime.now())
        if serverID == 'y':
            if datetime.time(datetime.now()) >= time(15,14,45):
                qTime = " 15:1"
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
        else:
            if datetime.time(datetime.now()) >= time(13,14,45):
                qTime = " 13:1"
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

   
    cancelFillFile = open(path + "cancelFills.log") 
    for line in cancelFillFile:
        RX_OptionMarket = re.match (".*#:\s([0-9]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            cancelFillList.append([match.group(1)])
    cancelFillFile.close()    
    
    
    orderFile = open(path + "orders.txt") 
    for line in orderFile:
        RX_OptionMarket = re.match (".*\:\s([A-Z]+).*(\d{4}\-\d{2}\-\d{2}).*(\d{2}\:\d{2}\:\d{2}).*\):\s([A-Z]+)\s([0-9]+).*#:\s([0-9]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            orderList.append([match.group(1), match.group(3), match.group(6), match.group(4), match.group(2), match.group(5)])
    orderFile.close()   
                          
    takerFile = open( path + "takerData.txt",'r')
    
    for line in takerFile:
        RX_OptionMarket = re.match (".*(\d{4}\-\d{2}\-\d{2}).*(\d{2}\:\d{2}\:\d{2}\.\d{3}).*Symbol=([0-9A-Z_]+).*\sType=([A-Z ]+).*Side=([A-Z]+).*OrderID=([0-9]+).*TransTime=.*(\d{2}\:\d{2}\:\d{2}).*OrderPrice=([0-9]+).*OrderSize=([0-9]+).*uTV=([0-9]+).*MktBid=([0-9]+).*" \
                                    + "MktAsk=([0-9]+).*Delta=([0-9.-]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*DaysToExp=([0-9.]+).*RiskBuy=([0-9-]+).*RiskSell=([0-9-]+).*TheoValue=([0-9]+).*KTBid=([0-9]+).*KTAsk=([0-9]+).*", line, re.M)          
        #RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}).*Symbol=([0-9A-Z_]+).*\sType=([A-Z ]+).*Side=([A-Z]+).*OrderID=([0-9]+).*TransTime=.*(\d{2}\:\d{2}\:\d{2}).*OrderPrice=([0-9]+).*OrderSize=([0-9]+).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*DaysToExp=([0-9.]+).*RiskBuy=([0-9-]+).*RiskSell=([0-9-]+).*TheoValue=([0-9]+).*KTBid=([0-9]+).*KTAsk=([0-9]+).*", line, re.M)    
        match = RX_OptionMarket
        if match:
            matchDate = match.group(1)
            matchTimeStamp = match.group(2)            
            matchSymbol = match.group(3)
            matchType = match.group(4)
            matchSide = match.group(5)
            matchOrderID = match.group(6)
            matchTransTime =  match.group(7)
            matchOrderPrice =  match.group(8)
            matchOrderSize =  match.group(9)
            matchuTV =  match.group(10)
            matchMktBid =  match.group(11)
            matchMktAsk =  match.group(12)
            matchDelta = match.group(13)
            matchMyIV =  match.group(14)
            matchTheoIV =  float(match.group(15))
            matchuMSP =  match.group(16)
            matchDTE =  float(match.group(17)) / 252
            matchRiskBuy = match.group(18)
            matchRiskSell =  match.group(19)
            matchTheoValue =  match.group(20)
            matchKTBid =  match.group(21)
            matchKTAsk =  match.group(22)       
            
            dataList.append([matchSymbol, matchType, matchSide, matchOrderID, matchTransTime, matchOrderPrice, matchOrderSize, matchMktBid, matchMktAsk, matchRiskBuy, matchRiskSell, matchKTBid, matchKTAsk, 'T', matchMyIV, matchTheoIV, matchuMSP, matchTheoValue, matchuTV, matchTimeStamp, matchDTE, matchDelta, 0, matchDate])
    
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
        RX_OptionMarket = re.match (".*(\d{4}\-\d{2}\-\d{2}).*Symbol=([0-9A-Z_]+).*\sType=([A-Z ]+).*Side=([A-Z]+).*OrderID=([0-9]+).*OrderPrice=([0-9]+).*OrderSize=([0-9]+).*DaysToExp=([0-9.]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            matchDate = match.group(1)            
            matchSymbol = match.group(2)
            matchType = match.group(3)
            matchSide = match.group(4)
            matchOrderID = match.group(5)
            matchOrderPrice = match.group(6)
            matchOrderSize = match.group(7)
            matchDTE =  float(match.group(8)) / 252
    
            for item in makerList:
                if item[0] == matchOrderID:
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
                    
                    
                    dataList.append([matchSymbol, matchType, matchSide, matchOrderID, matchTransTime, matchOrderPrice, matchOrderSize, matchMktBid, matchMktAsk, matchRiskBuy, matchRiskSell, matchKMBid, matchKMAsk, 'M', matchMyIV, matchTheoIV, matchuMSP, matchTheoValue, matchuTV, matchTimeStamp, matchDTE, matchDelta, 0, matchDate])
             
                    
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
        
        sentOrder = Order(item)        
        
        
        # initialize loop variables
        ErrorTrade = ""
        riskTradeType = 0
        currentPrice = 'n/a'
        currentIV = 'n/a'
        currentuMSP = 'n/a'
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
        
        
        buySell = item[2]
        DTE = item[20]
        delta = float(item[21])
        executionTime = datetime.strptime(item[4], "%H:%M:%S")
        timeStamp = datetime.strptime(item[19], "%H:%M:%S.%f")
        size = int(item[6])


        midpoint = (mktAsk + mktBid) / 2
        futBias = 'error'
        volBias = 'error'
        orderSize = 0
        uTVBSPrice = 0
        ivTVBSPrice = 0
        tradePnL = 0
  
        
        recordNumber += 1
        
        if 'ES' in sentOrder.symbol:
            divider = 100
        else:
            divider = 1000

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
                    if orderType == 'FILL':
                        fillQty = line[5]
                    break
            if orderType == 'FILL':
                orderType = 'F'
            else:
                orderType = 'C'
        elif makerTaker == 'M':
            for line in orderList:
                if line[2] == item[3]:
                    orderType = 'F'
                    endTime = datetime.strptime(line[1], timeFormat1)
                    logFile.write("orderList: " + str(line))
                    fillQty = line[5]
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
                uTVBSPrice = func.BS_Pricer(symbolCPF, (uTV/divider), strike, DTE, 0, myIV) * divider
                mspBSPrice = func.BS_Pricer(symbolCPF, (uMSP/divider), strike, DTE, 0, myIV) * divider

            else:
                uTVBSPrice = 'error'
                mspBSPrice = 'error'
                
            if theoIV != 0:
                ivTVBSPrice = func.BS_Pricer(symbolCPF, (uMSP/divider), strike, DTE, 0, theoIV) * divider
                TVBSPrice = func.BS_Pricer(symbolCPF, (uTV/divider), strike, DTE, 0, theoIV) * divider
            else:
                ivTVBSPrice = 'error'
                TVBSPrice = 'error'
            
#            print "IV", uMSP/1000, strike, currentIV
#            print "U", currentuMSP/1000, strike, myIV
            if currentIV != 0 and currentIV != 'n/a':
                currentIVPrice = func.BS_Pricer(symbolCPF, (uMSP/divider), strike, DTE, 0, currentIV) * divider
            else:
                currentIVPrice = 'n/a'
            if not myIV == 0 and currentuMSP != 'n/a':
                currentUPrice = func.BS_Pricer(symbolCPF, (currentuMSP/divider), strike, DTE, 0, myIV) * divider
            else:
                currentUPrice = 'n/a'
            if currentIV !=0 and currentIV != 'n/a' and currentuMSP != 'n/a':
                currentTheoPrice = func.BS_Pricer(symbolCPF, (currentuMSP/divider), strike, DTE, 0, currentIV) * divider
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
        
        if orderType == 'F':
            orderQty = int(fillQty)
        else:
            orderQty = int(item[6])
        
        
        if buySell == 'BUY':
            BS = 1      
            orderSize = BS * orderQty 
            tradeDelta = delta * orderSize
            if not currentPrice == 'n/a':
                tradePnL = (currentPrice - sentOrder.orderPrice) * dollarizer

            else:
                tradePnL = 'n/a'
            for (counter, record) in enumerate(timePriceList):
                if record == -1:
                    timePnLList.append("N/A")
                else:
                    timePnLList.append((float(record) - sentOrder.orderPrice) * dollarizer)
            if tradeType == 'O':
                for record in ivPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        ivPnLList.append((float(record) - mspBSPrice) * dollarizer)
                    else:
                        ivPnLList.append('n/a')
                if not mspBSPrice == 'error':
                    xEdge  = (mspBSPrice - sentOrder.orderPrice) * dollarizer
                    TVEdge = (TVBSPrice - sentOrder.orderPrice) * dollarizer
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
                xEdge = (midpoint - sentOrder.orderPrice) * dollarizer
                TVEdge = (theoVal - sentOrder.orderPrice) * dollarizer
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
            orderSize = BS * orderQty
            tradeDelta = orderSize * delta
            
            if not currentPrice == 'n/a':
                tradePnL = (sentOrder.orderPrice - currentPrice) * dollarizer
            else:
                tradePnL = 'n/a'
                    
            for (counter, record) in enumerate(timePriceList):
                if record == -1:
                    timePnLList.append("N/A")
                else:
                    timePnLList.append((sentOrder.orderPrice - float(record)) * dollarizer)
            if tradeType == 'O':
                for record in ivPriceTimeList:
                    if record != 'n/a' and mspBSPrice != 'error':
                        ivPnLList.append((mspBSPrice - float(record)) * dollarizer)
                    else:
                        ivPnLList.append('n/a')
                if not mspBSPrice == 'error':
                    xEdge = (sentOrder.orderPrice - mspBSPrice) * dollarizer
                    TVEdge = (sentOrder.orderPrice - TVBSPrice) * dollarizer
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
                xEdge = (sentOrder.orderPrice - midpoint) * dollarizer
                TVEdge = (sentOrder.orderPrice - theoVal) * dollarizer
                currentIVPnL = 'n/a'
                currentUPnL = 'n/a'
                currentTheoPnL = 'n/a'
            if symbolCPF != 'F' and uTVBSPrice != 'error':
                uTVEdge =  (mspBSPrice - uTVBSPrice) * dollarizer
                ivTVEdge =  (mspBSPrice - ivTVBSPrice) * dollarizer
                edgeCompare = (ivTVEdge - uTVEdge)
            else:
                uTVEdge = 'err'
                ivTVEdge = 'err'
                edgeCompare = 'err'

        
            
        if riskSide == item[2]:
             riskOnOff = "OFF"
        else:
             riskOnOff = "ON"
        
        
        if buySell == 'BUY':
            if riskSell < 0:
                riskTradeType = 1  # traded in spite of risk preference
            elif riskBuy < 0:
                if (sentOrder.ktBid + riskBuy) >= sentOrder.orderPrice:
                    riskTradeType = 2   #would have traded regardless
                elif (sentOrder.ktBid + riskBuy) < sentOrder.orderPrice:
                    riskTradeType = 3   # traded because of risk preference, would not have traded otherwise
                else:
                    riskTradeType = -1   # error
            elif riskBuy >= 0 and riskSell >= 0:
                riskTradeType = 4
            else:
                riskTradeType = -2   # error
               
        elif buySell == 'SELL':
            if riskBuy < 0: 
                riskTradeType = 1
            elif riskSell < 0:
                if (sentOrder.ktAsk - riskSell) <= sentOrder.orderPrice:
                    riskTradeType = 2   #would have traded regardless
                elif (sentOrder.ktAsk - riskSell) > sentOrder.orderPrice:
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
    
      
                                
        if tradeType == 'F':
            uTV = theoVal
            uMSP = midpoint
            
#        print "1", theoPnLList
#        print "2", ivPnLList
#        print "3", uPnLList

        
        outputFile.write(str(sentOrder.orderDate) + '\t' + str(sentOrder.executionTime) + '\t' + str(sentOrder.symbol) + '\t' + str(orderID) + '\t'  + str(tradeType) + "\t" + str(orderType) + '\t' + str(makerTaker) + '\t' + str(kicker) + '\t' + str(orderSize) \
                + '\t' + str(sentOrder.orderPrice) + '\t' + str(currentPrice) + '\t' + str(tradePnL) + '\t' + str(currentTheoPnL) + '\t' + str(currentIVPnL) + '\t' + str(currentUPnL) \
                + '\t' + str(xEdge) + '\t' + str(TVEdge) + '\t' + str(BADiff) + '\t' + str(timeDiff) + '\t' + str(cancelFill) \
                + '\t' + str(riskOnOff) +  '\t' + str(riskTradeType) +  '\t' + str(futBias) +  '\t' + str(volBias)  + '\t' +  str(uMSP) + '\t' + str(uTV) \
                + '\t' + str(theoIV) + '\t' + str(myIV) + '\t' + str(midpoint) + '\t' + str(ivTVEdge) + '\t' + str(uTVEdge) + '\t' + str(edgeCompare) \
                + '\n')
        

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




print("Paste output file (/Public2/thansen/python/TradeAnalyzer/output.txt) into Excel.\n")

        
    
  
  
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

