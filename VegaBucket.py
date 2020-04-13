import re
import commands
import func
from datetime import datetime
from datetime import time
import MySQLdb
from optparse import OptionParser

def getContractInfo(host,db):
        c = db.cursor()
        c.execute("select Symbol, DollarNormalize, ContractSize from Instruments")

        dbRows = c.fetchall()

        poses = []
        for row in dbRows:
                poses.append(list(row))

        return poses

usage = "USAGE: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-u", "--user", dest="user", help="MySQL user name", metavar="USER NAME", default="ctsuser")
parser.add_option("-p", "--password", dest="password", help="MySQL password", metavar="PASSWORD", default="c9t8s2")
parser.add_option("-d", "--database", dest="database", help="MySQL database name", metavar="DB", default="Hull")
parser.add_option("-n", "--nototal", dest="nototal", help="Doesn't sum up positions", metavar="NOTOTAL")
parser.add_option("-o", "--outfile", dest="outfile", help="Writes to outfile instead of stdout", metavar="OUTFILE")

(options,args) = parser.parse_args()
if options.outfile:
        outfile = open(options.outfile,'w')
allPositions = []
contractInfoList = []
serverDB = []

with open("/Public2/config/hull_hosts.txt", 'r') as f:
    for line in f:
        (key, value) = line.split('\t')
        serverDB.append([key, value])

for host in serverDB:
        db = MySQLdb.connect(host=host[0].rstrip(), user=options.user, db = host[1].rstrip(), passwd=options.password)
        contractInfoList.extend(getContractInfo(host,db))


# this program must be run in UTIL
#  THIS VERSION IS USING THE GREEK VALUES FROM HULLMARKETDATA INSTEAD OF CALCULATING THEM

path = r"/Public2/thansen/python/VegaBucket/"
optClass = ""
Ketchum_SymbolDict = {}
strikeDict = {}
bucketList= [0,0,0,0,0,0,0,0,0,0]
positionList = [0,0,0,0,0,0,0,0,0,0]
volNormalizer = .01
dataList = []
thetaList = [0,0,0,0,0,0,0,0,0,0]
gammaList = [0,0,0,0,0,0,0,0,0,0]
deltaList = [0,0,0,0,0,0,0,0,0,0]
optFutDict = {}


qTime = ""
currentTime = datetime.time(datetime.now())
sec = ""
m = ""
if datetime.time(datetime.now()) >= time(13,15,0):
    qTime = "13:14:50"
else:
    if currentTime.second < 10:
        sec = "0"
    if currentTime.minute < 10:
        m = "0"
    qTime = str(currentTime.hour) + ":" + m + str(currentTime.minute) + ":" + sec + str(currentTime.second)
    

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
    RX_1 = re.match ("([0-9A-Z_]+)\s+([0-9-]+)", line, re.M)
    if RX_1:
        if not int(RX_1.group(2)) == 0:
            Ketchum_SymbolDict[RX_1.group(1)]=int(RX_1.group(2))


print('\n')
while not optFutDict.has_key(optClass):
    optClass = raw_input('Pick option class ' + str(optFutDict.keys()) + ': ')
    print('\n')

user = commands.getoutput('whoami')
print("Run these scripts in production: \n")
print("#1: grep " + optClass + " /var/cts/Logs/KODBData.log | grep " \
         + qTime + " | grep 'Type= T' > /home/" + user + "/opData.txt;scp /home/" + user + "/opData.txt " \
         # + qTime + " | grep KMarketsValid=1 | grep 'Type= T' > /home/" + user + "/opData.txt;scp /home/" + user + "/opData.txt " \
        + "eqctsutil02:/Public2/thansen/python/VegaBucket/opData.txt" )

print('\n')
raw_input("Press 'Enter' when done")
print('\n')    
opFile = open( path + "opData.txt",'r')

for line in opFile:
    RX_OptionMarket = re.match (".*Symbol=([0-9A-Z_]+).*Delta=([0-9.-]+).*Vega=([0-9.]+).*Gamma=([0-9-.]+).*Theta=([0-9-.]+).*", line, re.M)
    match = RX_OptionMarket
    if match:
        dataList.append([match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)])

opFile.close()
div = 0
sum = 0

for optionKey in Ketchum_SymbolDict:
    if optionKey.find(optClass) != -1:
        for item in dataList: 
            if item[0] == optionKey:
                for line in contractInfoList:
                    print item[0], line[0]
                    if item[0].split("_")[0] == line[0].split('^')[0]:
                        dollarnormalizer = float(line[1])
                        multiplier = float(line[2])
                        #print dollarnormalizer, multiplier
                        break
                delta = float(item[1])
                unitDelta = float(item[1]) * Ketchum_SymbolDict[optionKey]
                unitVega = float(item[2]) * Ketchum_SymbolDict[optionKey] * dollarnormalizer * multiplier * volNormalizer
                unitTheta = float(item[4]) * Ketchum_SymbolDict[optionKey] * dollarnormalizer * multiplier   
                unitGamma = float(item[3]) * Ketchum_SymbolDict[optionKey] / dollarnormalizer * volNormalizer
                strikeDict[optionKey] = [delta, unitVega, Ketchum_SymbolDict[optionKey], unitGamma, unitTheta, unitDelta]

totalvega = 0
totalDelta = 0
 
for optionKey in strikeDict:
    totalvega += strikeDict[optionKey][1]
    if strikeDict[optionKey][0] > 0: 
        bucketdelta = int((1- strikeDict[optionKey][0]) * 10)  
    elif strikeDict[optionKey][0] >= 1 or strikeDict[optionKey][0] <= -1:
        bucketdelta = 9
    else:
        bucketdelta = int(-1 * strikeDict[optionKey][0] * 10)
    bucketList[bucketdelta] +=  strikeDict[optionKey][1]
    positionList[bucketdelta] += strikeDict[optionKey][2]
    thetaList[bucketdelta] += strikeDict[optionKey][4]
    gammaList[bucketdelta] += strikeDict[optionKey][3]
    deltaList[bucketdelta] += strikeDict[optionKey][5]

totalvega = 0

print('Unsmoothed Vega\n')
for index, line in enumerate(bucketList):    
    
    print((str(index * 10)) + "-" + str(index * 10 + 9) + '\t' + str(int(line)))
    totalvega += line
print("\nTotal Vega = " + str(int(totalvega))+'\n')
print ("Smoothed Vega\n")

data = func.smooth_list_gaussian(bucketList)


newList = func.smoothListGaussian(data)
finalList = newList[5:15]

totalvega = 0
for index, line in enumerate(finalList):   
    print((str(index * 10)) + "-" + str(index * 10 + 9) + '\t' + str(int(line)))
    totalvega += line
print("\nTotal Smoothed Vega = " + str(int(totalvega))+'\n')

totalposition = 0
print ("Position\n")
for index, line in enumerate(positionList):   
    print((str(index * 10)) + "-" + str(index * 10 + 9) + '\t' + str(int(line)))
    totalposition += line
print("\nTotal Position = " + str(int(totalposition))+'\n')
print("\n")

totaltheta = 0
print ("Theta\n")
for index, line in enumerate(thetaList):   
    print((str(index * 10)) + "-" + str(index * 10 + 9) + '\t' + str(int(line)))
    totaltheta += line
print("\nTotal Theta = " + str(int(totaltheta))+'\n')

totalgamma = 0
print ("Gamma\n")
for index, line in enumerate(gammaList):   
    print((str(index * 10)) + "-" + str(index * 10 + 9) + '\t' + str(line))
    totalgamma += line
print("\nTotal Gamma = " + str(totalgamma)+'\n')

totaldelta = 0
print ("Delta\n")
for index, line in enumerate(deltaList):   
    print((str(index * 10)) + "-" + str(index * 10 + 9) + '\t' + str(line))
    totaldelta += line
print("\nTotal Delta = " + str(totaldelta)+'\n')




              
