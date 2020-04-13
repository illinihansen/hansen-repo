# -*- coding: utf-8 -*-
"""
Created on Tue May 07 10:53:02 2013

@author: thansen
"""

import re
import commands
import pdb


from datetime import date, timedelta, datetime

timeFormat = "%H:%M:%S.%f"
timeformat1 = '%H%M%S%f'
futDataList = []
optDataList = []
finalList = []
futIndex = 0


futpath= '/Public2/thansen/MSPData/secdata.txt'
optpath = '/Public2/thansen/MSPData/LEM3.MSP.log'


futMSPfile = open(futpath, "r")
futMSPList= futMSPfile.readlines()
futMSPfile.close()

optMSPFile = open(optpath, 'r')
optMSPList = optMSPFile.readlines()
optMSPFile.close()

j = 0
for line in futMSPList:
    templist = line.split(' ')
    if j == 0:
        for i, item in enumerate(templist):    
            if item == 'LEM3':
                futIndex = i

                j = 1
    else:
        #print datetime.strptime(templist[1], timeformat1)# - timedelta(0,18000)
        futDataList.append([templist[0], datetime.strptime(templist[1], timeformat1) - timedelta(0,18000), float(templist[26])])
#        print templist[47]

for line in optMSPList:
    templist = line.split(' ')
    optDataList.append([templist[0], datetime.strptime(templist[1], timeFormat), float(templist[13][:-2])]) 
    #print templist[13][:-2]

outputFile = open("/Public2/thansen/python/MSPAnalyzer/output.txt", "w")
outputFile.write('Time\tOptMSP\tFutMSP\n')
lastTime = 0   
index = 0 
for line in optDataList:
    if line[1] == lastTime:
        continue
    else:
       # pdb.set_trace()
        lastTime = line[1]
#        for i, item in enumerate(futDataList[index:(len(futDataList))]):
        for item in futDataList:
            if item[1] <= line[1]:
                futMSP = item[2]
                lastFutTime = item[1]
            if item[1] > line[1]:
                print lastTime, lastFutTime
#                pdb.set_trace()
#                finalList.append([lastTime.strftime(timeFormat), line[2], futMSP])
                outputFile.write(str(lastTime) + "\t" +  str(line[2]) + '\t' + str(lastFutTime) + '\t' + str(futMSP) + '\n')
                break

print("Paste output file into Excel")

    