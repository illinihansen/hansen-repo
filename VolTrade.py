# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 11:45:54 2013

@author: thansen

This script will parse option trades, and simulate a vol trading environment by hedging the delta risk with a future trade done at the uMSP price.
CANNOT run on current day since we have to get the dump of the underlying tick file at the EOD ******
"""

import re, commands
from datetime import datetime, timedelta, time, date
import os, os.path
from operator import itemgetter
import func, gzip, numpy
from KHelperBook import *


timeFormat = "%H:%M:%S.%f"
timeFormat1 = "%H:%M:%S"
uPath = r"/Public2/thansen/python/VolTrade/"
winPath = '\\\\eqprodnas01\\vg01.vol01.Public2\\thansen\\python\\TradeAnalyzer\\'
path = r"/Public2/thansen/python/VolTrade/"
pathChoice = 'U'
inputStr = ""
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


def getULMarket(orderTime, symbol, orderDate):
    
    bidPrice = 0
    askPrice = 0
    last = 0
    ULDate = datetime.strftime(orderDate, "%Y%m%d")
    ULSymbol = optFutLookupDict[symbol.split("_")[0]]
    
    if not ULFinderDict.has_key(ULSymbol):
        inputFile = '/CBOT2/data/analytics/book/DATACAPTURE4/' + ULDate + '/' + ULSymbol + "_" + ULDate  + "_bookL2Ct.npy.gz"
        unzipFile = gzip.open(inputFile, 'rb')
        ULFile = numpy.load(unzipFile)
        unzipFile.close()      
        ULFinderDict[ULSymbol] = ULFile
    for index, line in enumerate(ULFinderDict[ULSymbol]):
#        formatTime = datetime.strftime(line[8].format('d'), 'yyyymmddHHMMSSffffff')
#        print datetime.fromtimestamp(line[8]),  orderTime
        if datetime.fromtimestamp(line[8]) < orderTime:
            last = index
            continue
        else:
#            bidPrice = line[11]
            bidPrice = ULFinderDict[ULSymbol][last][11]
#            askPrice = line[13]
            askPrice = ULFinderDict[ULSymbol][last][13]
            ULFinderDict[ULSymbol] = ULFinderDict[ULSymbol][last:]
            break
    if bidPrice == 0: bidPrice = 'error'
    if askPrice == 0: askPrice = 'error'
   
    return (bidPrice, askPrice, ULSymbol, datetime.fromtimestamp(line[8]) )

 
#    inputFile = '/CBOT2/data/analytics/book/DATACAPTURE4/' + ULDate + '/' + ULSymbol + "_" + ULDate  + "_bookL2Ct.npy.gz"
#    unzipFile = gzip.open(inputFile, 'rb')
#    ULFile = numpy.load(unzipFile)
#    unzipFile.close()      
#    for line in reversed(ULFile):
#        if datetime.fromtimestamp(line[8]) > orderTime:
#            continue
#        else:
#            bidPrice = line[11]
#            askPrice = line[13]
#            break
#    if bidPrice == 0: bidPrice = 'error'
#    if askPrice == 0: askPrice = 'error'
#   
#    return (bidPrice, askPrice, ULSymbol, datetime.fromtimestamp(line[8]) )
    
    
with open(r"/Public2/thansen/python/symbolDollarizer.txt") as f:
    for line in f:
        (key, val) = line.split('\t')
        dollarizerDict[key] = float(val)



while True:
    print '\n'
    print "Cannot run on current day, choose a date range that ends on a previous day."
    startDateRaw = raw_input('Enter start date (yyyy-mm-dd):')
    endDateRaw = raw_input('Enter end date (yyyy-mm-dd):')
    startDate = datetime.strptime(startDateRaw, "%Y-%m-%d").date()
    endDate = datetime.strptime(endDateRaw, "%Y-%m-%d").date()
    if startDate > endDate:
        print "Error in Date Range"
        continue
    if startDate >= date.today():
        print "Error in Date Range"
        continue
    if endDate >= date.today():
        print "Error in Date Range"
        continue
    break
   
symbolES = raw_input('Analyzing ES trades? (y/n): ')

currentDate = startDate
outputFile = open(path + "output.txt", "w")
outputFile.write("Date\tTime\tSymbol\tOrderID\tTradeType\tF/C\tM/T\tSize\tPrice\tCurrPrice\tPnLPerContract\tDelta\tTradePnL\tTotalDelta\tuMSP\tuTV\tFutBid\tFutAsk\toptPnL\tOptOrderSize\n")

                

while currentDate <= endDate:
    
    orderList = []
    currentList = []
    makerList = []
    dataList = []
    currentDict = {}
    ULFinderDict = {}
    
    
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
    
    if currentDate < date(2013,3,13): pastPath = r"/Public2/Archive/AUPRODCTS09/"         
    elif currentDate >= date(2013,3,13) and currentDate < date(2013,4,26): pastPath = r"/Public2/Archive/AUPRODCTS17/"
    elif currentDate >= date(2013,4,26) and currentDate < date(2013,5,14): pastPath = r"/Public2/Archive/AUPRODCTS16/"
    elif currentDate >= date(2013,5,14): pastPath = r"/Public2/Archive/AUPRODCTS17/"
        
    if symbolES == 'y': pastPath = r"/Public2/Archive/AUPRODCTS17/"
    else: pastPath = r"/Public2/Archive/AUPRODCTS13/"
                
    if currentDate != date.today():
        if not os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat() + ".gz"):
            if not os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat()):
                currentDate = currentDate + timedelta(1)
                continue

    if currentDate == date.today():
        currentTime = datetime.time(datetime.now())
        if datetime.time(datetime.now()) >= time(13,14,45): qTime = " 13:1"
        else:
            if currentTime.second < 10: sec = "0"
            else: sec = ""
                
            if currentTime.minute < 10: m = "0"
            else: m = ""
    
            qTime = str(currentTime.hour) + ":" + m + str(currentTime.minute) + ":"
    
    elif currentDate < date(2013,4,8): qTime = " 13:5"
    else: qTime = ' 13:1'
         
        
    if symbolES == 'y': qTime = " 15:1"
    
    print("\nAccessing all relevant files for " + str(currentDate) + " @ " + str(datetime.now()) + "\n")
    
    
    
    
    if currentDate == date.today():
        user = commands.getoutput('whoami')    
        print('\n')
        print("Run this script in production: \n")
        print("#1: cp /var/cts/Logs/KODBData.log  /home/" + user + "/KODBData.log; egrep 'FILL|ORDER CANCELLED' /var/cts/Logs/Orders.log > /home/" + user + "/orders.txt; " \
                "grep 'CANCEL REJECTED' /var/cts/Logs/Orders.log > /home/" + user + "/cancelFills.log; " \
                "scp /home/" + user + "/KODBData.log /home/" + user + "/orders.txt /home/" + user + "/cancelFills.log eqctsutil02:/Public2/thansen/python/VolTrade;")
        print('\n')
        raw_input("Press 'Enter' when done")
        print('\n') 
        
  
    elif os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat()):
        commands.getoutput("cp " + pastPath + "KODBData.log." + currentDate.isoformat() + "  /Public2/thansen/python/VolTrade/KODBData.log; egrep 'FILL|ORDER CANCELLED' " \
                            + pastPath + "Orders.log." + currentDate.isoformat() + " > /Public2/thansen/python/VolTrade/orders.txt")
        
    elif os.path.isfile(pastPath + "KODBData.log." + currentDate.isoformat() + ".gz"):
        commands.getoutput("zcat " + pastPath + "KODBData.log." + currentDate.isoformat() + ".gz > /Public2/thansen/python/VolTrade/KODBData.log; " \
                            + "zcat " + pastPath + "Orders.log." + currentDate.isoformat() + ".gz |  egrep 'FILL|ORDER CANCELLED' > /Public2/thansen/python/VolTrade/orders.txt")
                               
    print("Creating helper files @ " + str(datetime.now()) + "\n")
    commands.getoutput("grep 'MType=.*FILL' /Public2/thansen/python/VolTrade/KODBData.log > /Public2/thansen/python/VolTrade/makerData.txt; " + \
                        "grep ' Type= SENT' /Public2/thansen/python/VolTrade/KODBData.log  > /Public2/thansen/python/VolTrade/takerData.txt; " + \
                        "grep 'MType=.*SENT' /Public2/thansen/python/VolTrade/KODBData.log > /Public2/thansen/python/VolTrade/makerSentData.txt; " + \
                        "grep '" + str(qTime) + ".*INFO' /Public2/thansen/python/VolTrade/KODBData.log | grep MyVValid=1> /Public2/thansen/python/VolTrade/currentData.txt")  

                        
    print("Processing KODBData records @ " + str(datetime.now()) + "\n")
    
    orderFile = open(path + "orders.txt") 
    for line in orderFile:
        RX_OptionMarket = re.match (".*\:\s([A-Z]+).*(\d{4}\-\d{2}\-\d{2}).*(\d{2}\:\d{2}\:\d{2}).*\):\s([A-Z]+)\s([0-9]+).*#:\s([0-9]+).*", line, re.M)
        match = RX_OptionMarket
        if match:
            orderList.append([match.group(1), match.group(3), match.group(6), match.group(4), match.group(2), match.group(5)])
    orderFile.close()   
    
    print("Done with order file @ " + str(datetime.now()) + "\n")                      
    takerFile = open( path + "takerData.txt",'r')
    
    for line in takerFile:
        RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}\.\d{3}).*Symbol=([0-9A-Z_]+).*\sType=([A-Z ]+).*Side=([A-Z]+).*OrderID=([0-9]+).*TransTime=.*(\d{2}\:\d{2}\:\d{2}\.\d{3}).*OrderPrice=([0-9]+).*OrderSize=([0-9]+).*uTV=([0-9]+).*MktBid=([0-9]+).*" \
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
    
    print("Done with taker file @ " + str(datetime.now()) + "\n") 
    takerFile.close() 
    
    makerFile = open( path + "makerData.txt",'r')
    
    for line in makerFile:
        RX_OptionMarket = re.match (".*(\d{2}\:\d{2}\:\d{2}\.\d{3}).*OrderID=([0-9]+).*TransTime=.*(\d{2}\:\d{2}\:\d{2}\.\d{3}).*uTV=([0-9]+).*MktBid=([0-9]+).*MktAsk=([0-9]+).*Delta=([0-9.-]+).*MyIV=([0-9.]+).*TheoIV=([0-9.]+).*uMSP=([0-9]+).*RiskBuy=([0-9-]+).*RiskSell=([0-9-]+).*TheoValue=([0-9]+).*KMBid=([0-9-]+).*KMAsk=([0-9-]+).*", line, re.M)
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
    
    print("Done with maker file 1 @ " + str(datetime.now()) + "\n") 
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
             
    print("Done with maker file 2 @ " + str(datetime.now()) + "\n")                 
    makerSentFile.close()
    
    currentFile = open( path + "currentData.txt",'r')

    currentRawList = currentFile.readlines()    
    
    if currentDate >= date(2013,4,8): 
        
        for line in reversed(currentRawList):
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
                if not currentDict.has_key(matchSymbol):
                    currentDict[matchSymbol] = matchMSP
                    currentList.append([matchSymbol, matchuTV, matchMktBid, matchMktAsk, matchMSP, matchuMSP, matchTheoVal, currentIV])
    else:     
        for line in reversed(currentRawList):
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
                    
                if not currentDict.has_key(matchSymbol):
                    currentDict[matchSymbol] = matchMSP
                    currentList.append([matchSymbol, matchuTV, matchMktBid, matchMktAsk, matchMSP, matchuMSP, matchTheoVal, currentIV])
        
    currentFile.close()
    
    print("Processing " + str(len(dataList)) + " records @ " + str(datetime.now()))    
    
    dataList = sorted(dataList, key=itemgetter(4))
    
    for item in dataList:
        currentPrice = 'n/a'
        currentIV = 'n/a'
        currentuMSP = 'n/a'
        dollarizer = dollarizerDict[item[0].split("_")[0]]
        
                
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
        executionTime = datetime.strptime(item[4], "%H:%M:%S.%f")
        timeStamp = datetime.strptime(item[19], "%H:%M:%S.%f")
        xTime = datetime.combine(currentDate, time(timeStamp.hour, timeStamp.minute, timeStamp.second, timeStamp.microsecond))
        DTE = item[20]
        delta = float(item[21])
        orderDate = ""
        orderSize = 0
        tradePnL = 0
        size = int(item[6])
        buySell = item[2]
        
        if not item[5] == 'error':
            orderPrice = float(item[5])
        else:
            orderPrice = item[5]
        
        
        if '_' in item[0]:
            tradeType = 'O'
        else:
            tradeType = 'F'   
            
        if item[1] == 'H':
            tradeType = 'H'
            orderType = 'F'
        
        if '_' in item[0]:    
            symbolCPF = item[0].split("_")[1][0]
            strike = int(item[0].split("_")[1][1:])
        else:
            symbolCPF = 'F'
        
        orderType = 'C'  
        fillQty = 0
        
        if makerTaker == 'T':    
            for line in orderList:
                if line[2] == item[3]:
                    orderType = 'F'
                    endTime = datetime.strptime(line[1], timeFormat1)   
                    orderDate = line[4] 
                    fillQty = line[5]
                    break
                
        elif makerTaker == 'M':
            for line in orderList:
                if line[2] == item[3]:
                    orderType = 'F'
                    endTime = datetime.strptime(line[1], timeFormat1)
                    orderDate = line[4]
                    fillQty = line[5]
                    break              
    
                
        if tradeType == 'O':
            for line in reversed(currentList):
                if line[0] == item[0]:
                    if line[4] != 0 and currentPrice == 'n/a':
                        currentPrice = line[4]
                    if line[7] != 0 and currentIV == 'n/a':
                        currentIV = line[7]
                    if line[5] != 0 and currentuMSP == 'n/a':
                        currentuMSP = line[5]
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
            else:
                ivTVBSPrice = 'error'
            
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

            
            
        elif tradeType == 'F' or tradeType == 'H':
            uTVBSPrice = 'n/a'
            ivTVBSPrice = 'n/a'
            currentUPrice = 'n/a'
            currentIVPrice = 'n/a'
            currentTheoPrice = 'n/a'
        
            
            for line in reversed(currentList): 
                if item[0] in line[0] and float(line[5]) != 0:
                    currentPrice = int(line[5])
                    break
                
        if orderType == 'F' and tradeType != 'H':
            orderQty = int(fillQty)
        else:
            orderQty = int(item[6])
               
        if buySell == 'BUY':
            BS = 1      
            orderSize = BS * orderQty  
            tradeDelta = delta * orderSize
            if not currentPrice == 'n/a' and not orderPrice == 'error':
                tradePnL = (currentPrice - orderPrice) * dollarizer

            else:
                tradePnL = 'n/a'
        
        elif buySell == 'SELL':
            BS = -1
            orderSize = BS * orderQty
            tradeDelta = orderSize * delta
            
            if not currentPrice == 'n/a' and not orderPrice == 'error':
                tradePnL = (orderPrice - currentPrice) * dollarizer
            else:
                tradePnL = 'n/a'
        
              
        if tradeType == 'O':
            #if tradeType == 'O' and orderType == 'F':
            if 'LE' in symbol:
                symbolMultiplier = 10
            elif 'ES' in symbol:
                symbolMultiplier = 1
            else:
                symbolMultiplier = 1000
            if currentDate < date.today():
                futMkt = getULMarket(xTime, symbol, currentDate) 
                if not futMkt[0] == 'error' and not futMkt[1] == 'error':
                    futBid = float(futMkt[0]) * symbolMultiplier
                    futAsk = float(futMkt[1]) * symbolMultiplier
                else:
                    futBid = 'error'
                    futAsk = 'error'
                    
                if 'ES' in symbol:
                    temp1 = (uTV % 100) * 10
                else:
                    temp1 = uTV % 1000                
                    
                if round(tradeDelta) >= 1:
                    if temp1 >= 750:
                        temp2 = 750
                    elif temp1 >= 500 and temp1 < 750:
                        temp2 = 500
                    elif temp1 >= 250 and temp1 < 500:
                        temp2 = 250
                    elif temp1 >=0 and temp1 < 250:
                        temp2 = 000
                    if 'ES' in symbol:
                        rounduTV = (uTV // 100) * 100 + (temp2/10)
                    else:
                        rounduTV = (uTV // 1000) * 1000 + temp2
                    
                    if futBid != 'error':                        
                        if rounduTV < futBid:
                            futPrice = futBid
                        else:
                            futPrice = rounduTV                        
                        
#                        if uTV >= futAsk:
#                            futPrice = futAsk
#                        else:
#                            futPrice = futBid
#                        futPrice = uTV
                    else:
                        futPrice = rounduTV
                    dataList.append([futMkt[2], 'H', 'SELL', orderID, item[4], futPrice, abs(round(tradeDelta)), 0, 0, 0, 0, 0, 0, makerTaker, 0, 0, uMSP, 0, uTV, item[19], 0, 1, futBid, futAsk, tradePnL * abs(orderSize), orderSize])
                elif round(tradeDelta) <= -1:
                    if temp1 > 750:
                        temp2 = 1000
                    elif temp1 > 500 and temp1 <= 750:
                        temp2 = 750
                    elif temp1 > 250 and temp1 <= 500:
                        temp2 = 500
                    elif temp1 > 0 and temp1 <= 250:
                        temp2 = 250
                    if 'ES' in symbol:
                        rounduTV = (uTV // 100) * 100 + (temp2/10)
                    else:
                        rounduTV = (uTV // 1000) * 1000 + temp2
                    
                    if futAsk != 'error':
                        if rounduTV > futAsk:
                            futPrice = futAsk
                        else:
                            futPrice = rounduTV
#                        if uTV <= futBid:
#                            futPrice = futBid
#                        else:
#                            futPrice = futAsk
#                        futPrice = uTV
                    else:
                        futPrice = rounduTV
                    dataList.append([futMkt[2], 'H', 'BUY', orderID, item[4], futPrice, abs(round(tradeDelta)), 0, 0, 0, 0, 0, 0, makerTaker, 0, 0, uMSP, 0, uTV, item[19], 0, 1, futBid, futAsk, tradePnL * abs(orderSize), orderSize])
        
        if orderDate == "":
            orderDate = currentDate
            
        if tradeType != 'H':
            outputFile.write(str(orderDate) + '\t' + str(item[4]) + '\t' + str(item[0]) + '\t' + str(orderID) + '\t'  + str(tradeType) + "\t" + str(orderType) + '\t' + str(makerTaker)  + '\t' + str(orderSize) \
                    + '\t' + str(item[5]) + '\t' + str(currentPrice) + '\t' + str(tradePnL) + '\t' + str(delta) + '\t' + str(tradePnL * abs(orderSize)) + '\t' + str(delta * orderSize) + '\t' + str(uMSP) + '\t' + str(uTV) + '\n')
        else:
            outputFile.write(str(orderDate) + '\t' + str(item[4]) + '\t' + str(item[0]) + '\t' + str(orderID) + '\t'  + str(tradeType) + "\t" + str(orderType) + '\t' + str(makerTaker)  + '\t' + str(orderSize) \
                    + '\t' + str(item[5]) + '\t' + str(currentPrice) + '\t' + str(tradePnL) + '\t' + str(delta) + '\t' + str(tradePnL * abs(orderSize)) + '\t' + str(delta * orderSize) + '\t' + str(uMSP) + '\t' + str(uTV) + '\t'+  str(item[22]) + '\t' + str(item[23]) + '\t' + str(item[24]) + '\t' + str(item[25]) + '\n')
    
    
    currentDate = currentDate + timedelta(1)       
                
                
            
