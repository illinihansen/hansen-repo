# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 14:25:10 2012

@author: thansen
"""

import re
import commands
from datetime import datetime, time
import func
from optparse import OptionParser


usage = "USAGE: %prog [options] [FILE]"
parser = OptionParser(usage=usage)
(options, args) = parser.parse_args()
usr = commands.getoutput('whoami')
boxsymbol = str(args[0].upper())



timeFormat = "%H:%M:%S.%f"
timeFormat1 = "%H:%M:%S" 
uPath = r"/Public2/thansen/python/TradeAnalyzer/"
winPath = '\\\\eqprodnas01\\vg01.vol01.Public2\\thansen\\python\\TradeAnalyzer\\'
path = r"/Public2/thansen/python/TradeAnalyzer/"
pathChoice = 'U'
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


outputFile = open(path + "output.txt", "w")
outputFile.write("Date\tTime\tSymbol\tOrderID\tTradeType\tF/C\tM/T\tKicker\tSize\tPrice\tCurrPrice\tPnLPerContract\tCurrTheoPnL\tCurrIVPnL\tCurrUPnL\txtraEdge\tTVEdge\tTTC\tSpeed(uSec)\tCancelFill\tRiskOnOff\tRiskTradeType\tFutBias\tVolBias\tuMSP\tuTV\tTheoIV\tMyIV\tuMidpoint\tivEdge$\tuEdge$\tEdgeCompare\tTotalDelta\n")

recordNumber = 0
orderType = ''
buySell = ''
endTime = datetime.now()

    
orderList = []
currentList = []
cancelFillList = []
makerList = []
dataList = []
crossList = []    


#    if date.weekday(date.today()) in (0,1,2):
#        unzipDate = date.today() - timedelta(5)
#    elif date.weekday(date.today()) in (3,4):
#        unzipDate = date.today() - timedelta(3)
#    else:
#        print "****WEEKEND?****"


if "ES" in boxsymbol.upper(): boxPath = "AUPRODCTS13"
else: boxPath = "AUPRODCTS17"
    
   
currentTime = datetime.time(datetime.now())
if 'ES' in boxsymbol:
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

user = commands.getoutput('whoami')    
#commands.getoutput ("cp /var/cts/Logs/KODBData.log  /home/" + user + "/KODBData.log; egrep 'FILL|ORDER CANCELLED' /var/cts/Logs/Orders.log > /home/" + user + "/orders.txt; " \
#        "grep 'CANCEL REJECTED' /var/cts/Logs/Orders.log > /home/" + user + "/cancelFills.log;scp " + Path + ":/var/cts/Logs/ /home/" + user + "/KODBData.log /home/" + user + "/orders.txt /home/" + user + "/cancelFills.log")
        
commands.getoutput("scp thansen@" + boxPath + ":/var/cts/Logs/KODBData.log /Public2/thansen/python/TradeAnalyzer/KODBData.log; scp thansen@" + boxPath + ":/var/cts/Logs/Orders.log /Public2/thansen/python/TradeAnalyzer/Orders.log;" \
                   + " egrep 'FILL|ORDER CANCELLED' /Public2/thansen/python/TradeAnalyzer/Orders.log > /Public2/thansen/python/TradeAnalyzer/orders.txt;" \
                   + " grep 'CANCEL REJECTED' /Public2/thansen/python/TradeAnalyzer/Orders.log > /Public2/thansen/python/TradeAnalyzer/cancelFills.log" )
                   

commands.getoutput("grep 'MType=.*FILL' /Public2/thansen/python/TradeAnalyzer/KODBData.log > /Public2/thansen/python/TradeAnalyzer/makerData.txt; " + \
                    "grep ' Type= SENT' /Public2/thansen/python/TradeAnalyzer/KODBData.log  > /Public2/thansen/python/TradeAnalyzer/takerData.txt; " + \
                    "grep 'MType=.*SENT' /Public2/thansen/python/TradeAnalyzer/KODBData.log > /Public2/thansen/python/TradeAnalyzer/makerSentData.txt; " + \
                    "grep 'Type= T' /Public2/thansen/python/TradeAnalyzer/KODBData.log | grep MyVValid=1 | grep KMarketsValid=1 | grep -v ' MSP=0.0' > /Public2/thansen/python/TradeAnalyzer/PriceData.txt; " + \
                    "grep '" + str(qTime) + ".*INFO' /Public2/thansen/python/TradeAnalyzer/KODBData.log | grep MyVValid=1 > /Public2/thansen/python/TradeAnalyzer/currentData.txt")  
print "grep '" + str(qTime) + ".*INFO' /Public2/thansen/python/TradeAnalyzer/KODBData.log | grep MyVValid=1 > /Public2/thansen/python/TradeAnalyzer/currentData.txt"


priceFile = open( path + "PriceData.txt",'r')
timeFile = open(path + "timeFile.txt", 'w')

   
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

currentFile.close()


print("Processing " + str(len(dataList)) + " records @ " + str(datetime.now()))    

timeFile = open(path + "timeFile.txt", 'r')
dataList = sorted(dataList, key=lambda data: data[3])
   
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
    
    
    symbol = item[0]
    orderDate = item[23]
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
    
    
    buySell = item[2]
    executionTime = datetime.strptime(item[4], "%H:%M:%S")
    timeStamp = datetime.strptime(item[19], "%H:%M:%S.%f")
    DTE = item[20]
    delta = float(item[21])
    midpoint = (mktAsk + mktBid) / 2
    futBias = 'error'
    volBias = 'error'
    orderSize = 0
    uTVBSPrice = 0
    ivTVBSPrice = 0
    tradePnL = 0
    size = int(item[6])
    
    recordNumber += 1
    
    if 'ES' in symbol:
        divider = 100
    else:
        divider = 1000


    
    if '_' in item[0]:    
        symbolCPF = item[0].split("_")[1][0]
        strike = int(item[0].split("_")[1][1:])
    else:
        symbolCPF = 'F'
   
    
    if "KIST" in item[1].split(" ") or "KIBT" in item[1].split(" "):
        kicker = 1
    elif "KISM" in item[1].split(" ") or "KIBM" in item[1].split(" "):
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
                fillQty = line[5]
                break
            
            
    for record in cancelFillList:
        if item[3] == record[0]:
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
            tradePnL = round((currentPrice - orderPrice) * dollarizer,2)

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
                xEdge  = round((mspBSPrice - orderPrice) * dollarizer,2)
                TVEdge = round((TVBSPrice - orderPrice) * dollarizer,2)
            else:
                xEdge = 'error'
                TVEdge = 'error'
                
            if not currentIVPrice == 'n/a'and mspBSPrice != 'error':
                currentIVPnL = round((currentIVPrice - mspBSPrice) * dollarizer,2)
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
            xEdge = round((midpoint - orderPrice) * dollarizer,2)
            TVEdge = round((theoVal - orderPrice) * dollarizer,2)
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
            tradePnL = round((orderPrice - currentPrice) * dollarizer,2)
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
                xEdge = round((orderPrice - mspBSPrice) * dollarizer,2)
                TVEdge = round((orderPrice - TVBSPrice) * dollarizer,2)
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
                currentIVPnL = round((mspBSPrice - currentIVPrice ) * dollarizer,2)
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
            xEdge = round((orderPrice - midpoint) * dollarizer,2)
            TVEdge = round((orderPrice - theoVal) * dollarizer,2)
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
                            
    if tradeType == 'F':
        uTV = theoVal
        uMSP = midpoint
    

    if '_' in item[0]:
        symbol = item[0]
    else:
        symbol = item[0]  + '      '
    
    outputFile.write(str(orderDate) + '\t' + str(item[4]) + '\t' + symbol + '\t' + str(orderID) + '\t'  + str(tradeType) + "\t" + str(orderType) + '\t' + str(makerTaker) + '\t' + str(kicker) + '\t' + str(orderSize) \
            + '\t' + str(item[5]) + '\t' + str(currentPrice) + '\t' + str(tradePnL) + '\t' + str(currentTheoPnL) + '\t' + str(currentIVPnL) + '\t' + str(currentUPnL) \
            + '\t' + str(xEdge) + '\t' + str(TVEdge) + '\t' + str(BADiff) + '\t' + str(timeDiff) + '\t' + str(cancelFill) \
            + '\t' + str(riskOnOff) +  '\t' + str(riskTradeType) +  '\t' + str(futBias) +  '\t' + str(volBias)  + '\t' +  str(uMSP) + '\t' + str(uTV) \
            + '\t' + str(theoIV) + '\t' + str(myIV) + '\t' + str(midpoint) + '\t' + str(ivTVEdge) + '\t' + str(uTVEdge) + '\t' + str(edgeCompare) + '\t' + str(delta * orderSize)\
            + '\n')
    if orderType == 'F':
        print(str(item[4]) + '\t' + symbol + '\t' + str(orderSize) + '\t' + str(item[5]) + '\t' + str(orderID)  + '\t' + str(int(uTV)) + '\t' + str(abs((delta * orderSize))))
            

timeFile.close()
outputFile.close()  



        
    
  
  
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

