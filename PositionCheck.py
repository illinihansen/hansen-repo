import sys
import csv
import re
import commands
import time

SymDict = {
  "CBT BEAN MEAL(0106)":"ZM",
  "CBT BEAN OIL(0107)":"ZL",
  "CBT CORN(01C)":"ZC",
  "CBT SOYBEANS(01S)":"ZS",
  "CBT WHEAT(01W)":"ZW",
  "CATTLE(0248)":"LE",
  "LIVE CATTLE(0248)":"LE",
  "CME LEAN HOGS(0253)":"HE",
  "CME FEEDERS(0262)":"GF",
  "EMINI S&P 500(03ES)":"ES"
}

MonthDict = {
  "01":"F",
  "02":"G",
  "03":"H",
  "04":"J",
  "05":"K",
  "06":"M",
  "07":"N",
  "08":"Q",
  "09":"U",
  "10":"V",
  "11":"X",
  "12":"Z",
}

YearDict = {
  "2012":"2",
  "2013":"3",
  "2014":"4",
}

#ABNpositionfile = "P:\ABN_33014.csv"            #Windows
ABNpositionfile = "/Public2/ABN_33014.csv"     
print ""
print ABNpositionfile
print ""

myABNFile = list(csv.reader(open(ABNpositionfile,'r'),delimiter=','))
ABN_Leftovers = []
ABN_SymbolList = []
Ketchum_SymbolList = []
fourmatt = ""
for line in myABNFile:
    Option = ""
    PC = ""
    dash = ""
    spacer = ""
    strike = ""

##    line[0] = Underlying
##    line[1] = Long
##    line[2] = Short
##    line[3] = Expiration
##    line[4] = Strike 
##    line[5] = P/C 

    if line[1] =="":
        if line[2]=="":
            quantity = 0
        else:
            quantity = int(line[2]) * -1
    else:
        quantity = line[1]
    if not line[5]=="":
        if line[0] == 'CATTLE(0248)':
            Option = ""
            strike = int(round(float(line[4])*10))
        elif line[0] == 'EMINI S&P 500(03ES)':
        if not line[0] == 'CATTLE(0248)' and not line[0] == 'EMINI S&P 500(03ES)' :
            Option = "O"
            if float(line[4]) < 10:
                spacer = "0"
            strike = int(round(float(line[4])*100))
        elif not line[0] == 'EMINI S&P 500(03ES)':
        
        PC = line[5]
        dash = "_"

    symbol = Option+SymDict[line[0]]+MonthDict[line[3][4:6]]+YearDict[line[3][:4]]+dash+PC+spacer+str(strike)
    if not quantity == 0:
        ABN_SymbolList.append([symbol,quantity])

ABN_SymbolList.sort()
 
dbStuff = commands.getoutput('hull_getcombinedpos --password=c9t8s2')

newfile = open("newfile.txt",'w')
newfile.writelines(dbStuff)
newfile.close()

newfile = open("newfile.txt",'r')
Ketchum_SymbolDict = {}

for line in newfile:
    RX_1 = re.match ("([0-9A-Z_]+)\s+([0-9-]+)", line, re.M)
    if RX_1:
        if not int(RX_1.group(2)) == 0:
            Ketchum_SymbolDict[RX_1.group(1)]=int(RX_1.group(2))

print "\t"+"ABN"+"\t"+"SYMBOL"+"\t\t"+"Ketchum"+"\t\t"+"Difference"

for item in ABN_SymbolList:
    if len(item[0]) < 10:
        fourmatt = "\t"
    if item[0] in Ketchum_SymbolDict:
        print "\t",item[1],"\t",item[0],"\t",fourmatt,Ketchum_SymbolDict[item[0]],"\t\t",(int(Ketchum_SymbolDict[item[0]])-int(item[1]))
        del Ketchum_SymbolDict[item[0]]
    else:
        ABN_Leftovers.append(item)
    fourmatt = ""

print ""
print "\tABN Leftovers"
if len(ABN_Leftovers) == 0:
    print "\tNONE"
for item in ABN_Leftovers:
    print "\t",item[0]," ",item[1]
print ""
print "\tKetchum Leftovers"
if len(Ketchum_SymbolDict) == 0:
    print "\tNONE"
for key in Ketchum_SymbolDict:
    print "\t",key," ",Ketchum_SymbolDict[key]
print ""
