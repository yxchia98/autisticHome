import csv
from datetime import datetime, timedelta
from ssl import ALERT_DESCRIPTION_ILLEGAL_PARAMETER
from tracemalloc import start
from pyparsing import delimited_list
import json

def preprocessData(): 
    # read data from files
    motionArr = []
    with open("motion2.txt") as motionFile:
        csv_reader = csv.reader(motionFile, delimiter=',')
        for line in csv_reader:
            # print(line)
            motionArr.append(line)
    motionFile.close()

    tempHumidArr = []
    with open("tempHumid2.txt") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line in csv_reader:
            # print(line)
            tempHumidArr.append(line)
    csv_file.close()

    buttonArr = []
    with open("button.txt") as buttonFile:
        csv_reader = csv.reader(buttonFile, delimiter=',')
        for line in csv_reader:
            # print(line)
            buttonArr.append(line)

    print("Motion Count: ", len(motionArr))
    print("Temperature Humidity Count: ", len(tempHumidArr))

    # preprocess data
    sleepTimes = []
    startSleepTimeArr = []
    endSleepTimeArr = []
    # get button start stop
    for items in buttonArr:
        if(items[1] == "True"):
            startSleepTime = datetime.strptime(items[2], '%Y-%m-%d %H:%M')
            startSleepTimeArr.append(startSleepTime)
        elif(items[1] == "False"):
            endSleepTime = datetime.strptime(items[2], '%Y-%m-%d %H:%M')
            endSleepTimeArr.append(endSleepTime)
    
    if(len(startSleepTimeArr) == len(endSleepTimeArr)):
        for i in range(len(startSleepTimeArr)):
            sleepTimes.append([startSleepTimeArr[i], endSleepTimeArr[i]])

    # get time of sleep
    # startTime = datetime.strptime(sleepTimes[0][0], '%Y-%m-%d %H:%M')
    # endTime = datetime.strptime(sleepTimes[0][1], '%Y-%m-%d %H:%M')
    # print("START TIME: ", startTime)
    # print("END TIME: ", endTime)

    # get relevant values
    targetMotionArr = []
    for items in motionArr:
        currentTime = datetime.strptime(items[1], '%Y-%m-%d %H:%M')
        for times in sleepTimes:
            if(currentTime >= times[0] and currentTime<=times[1]):
                motion = [items[0], currentTime]
                targetMotionArr.append(motion)


    targetTempHumidArr = []
    for items in tempHumidArr:
        currentTime = datetime.strptime(items[2], '%Y-%m-%d %H:%M')
        for times in sleepTimes:
            if(currentTime >= times[0] and currentTime <= times[1]):
                tempHumid = [items[0], items[1], currentTime]
                targetTempHumidArr.append(tempHumid)


    # match motion with temp
    matchArr = []
    for index1, i in enumerate(targetMotionArr):
        for index2, j in enumerate(targetTempHumidArr):

            # get motion time
            motionTime = i[1]
            # get tempTime
            tempTime = j[2]

            # if(tempTime == motionTime and index2 == 0):
            #     humidity = targetTempHumidArr[index2][0]
            #     temperature = targetTempHumidArr[index2][1]
            #     match = [i[0], i[1], humidity, temperature] 
            #     matchArr.append(match)
            if(tempTime > motionTime and index2>0):
                # get prev time variables 
                humidity = targetTempHumidArr[index2-1][0]
                temperature = targetTempHumidArr[index2-1][1]
                match = [i[0], i[1], humidity, temperature]
                matchArr.append(match)
                break          

    # set constant intervals, and insert back into matchArr
    globalIndex = 0
    for times in sleepTimes:
        currentTime = times[0]
        endTime = times[1]
        # print("starting:", currentTime)
        while (currentTime < endTime):
            if (globalIndex<len(matchArr)):
                # print("passed first if")
                # print("checking:", currentTime, matchArr[globalIndex][1])
                if(currentTime == matchArr[globalIndex][1]):
                    # print("Match", currentTime)
                    globalIndex += 1
                elif(matchArr[globalIndex][1]> currentTime):
                    # print("ADD")
                    target = [matchArr[globalIndex-1][0], currentTime, matchArr[globalIndex-1][2], matchArr[globalIndex-1][3]]
                    matchArr.insert(globalIndex, target)
                    globalIndex += 1
            currentTime = currentTime + timedelta(minutes=1)
        globalIndex +=1


    # outputArr contains all information with 1 min intervals
    outputArr = []
    for items in matchArr:
        status = items[0]
        date = str(items[1])
        humidity = items[2]
        temperature = items[3]
        item = [status, date, humidity, temperature]
        outputArr.append(item)

    # caculating averages for a sleep cycle

    sleeping = 0
    awake = 0
    count = 0
    totalTemp = 0
    totalHumid = 0
    # extra check hours per day
    for items in outputArr:
        flag = items[0]
        if(flag == "True"):
            awake += 1
        else:
            sleeping += 1
        totalHumid += float(items[2])
        totalTemp += float(items[3])
        count += 1

    totalSleep = awake + sleeping
    sleepRatio = round(sleeping/totalSleep, 3)
    avgHumid = round((totalHumid/count), 2)
    avgTemp = round((totalTemp/count), 2)
    print("Ratio: ", sleepRatio)
    print("H & T: ", avgHumid, avgTemp)

    with open("sleepRatio.txt", 'a') as sleepFile:
        sleepFile.writelines(str(sleepRatio) + "," + str(avgTemp) + "\n")
        sleepFile.close()
