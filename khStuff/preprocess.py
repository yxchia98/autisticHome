import csv
from datetime import datetime, timedelta
from ssl import ALERT_DESCRIPTION_ILLEGAL_PARAMETER
from tracemalloc import start
from pyparsing import delimited_list
import json

# read data from files
motionArr = []
with open("motion.txt") as motionFile:
    csv_reader = csv.reader(motionFile, delimiter=',')
    for line in csv_reader:
        # print(line)
        motionArr.append(line)
motionFile.close()

tempHumidArr = []
with open("tempHumid.txt") as csv_file:
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

# preprocess data

print("Motion Count: ", len(motionArr))
print("Temperature Humidity Count: ", len(tempHumidArr))


# get button start stop
for items in buttonArr:
    if(items[1] == "True"):
        startSleepTime = items[2]
    elif(items[1] == "False"):
        endSleepTime = items[2]
# get time of sleep
startTime = datetime.strptime(startSleepTime, '%Y-%m-%d %H:%M')
endTime = datetime.strptime(endSleepTime, '%Y-%m-%d %H:%M')
print(endTime - startTime)

# manually remove duplicate values
# get relevant values
targetMotionArr = []
for items in motionArr:
    currentTime = datetime.strptime(items[1], '%Y-%m-%d %H:%M')
    if(currentTime >= startTime and currentTime<=endTime):
        motion = [items[0], currentTime]
        targetMotionArr.append(motion)


targetTempHumidArr = []
for items in tempHumidArr:
    currentTime = datetime.strptime(items[2], '%Y-%m-%d %H:%M')
    if(currentTime > startTime and currentTime<endTime):
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
            

# set constant intervals
currentTime = startTime
globalIndex = 0

print("starting:", currentTime)
while (currentTime < endTime):
    if (globalIndex<len(matchArr)):
        if(currentTime == matchArr[globalIndex][1]):
            # print("Match", currentTime)
            globalIndex += 1
        elif(matchArr[globalIndex][1]> currentTime):
            # print("ADD", currentTime)
            target = [matchArr[globalIndex-1][0], currentTime, matchArr[globalIndex-1][2], matchArr[globalIndex-1][3]]
            matchArr.insert(globalIndex, target)
            globalIndex += 1
    currentTime = currentTime + timedelta(minutes=1)

outputArr = []
for items in matchArr:
    status = items[0]
    date = str(items[1])
    humidity = items[2]
    temperature = items[3]
    item = [status, date, humidity, temperature]
    outputArr.append(item)

# save preprocessed data to data.txt
# with open("data.txt", "a") as dataFile:
#     dataFile.writelines("status," + "date," + "humidity," + "temperature\n")
#     for lines in outputArr:
#         status = lines[0]
#         date = lines[1]
#         humidity = lines[2]
#         temperature = lines[3]
#         row = status + "," + date + "," + humidity + "," + temperature + "\n"
#         dataFile.writelines(row)
# dataFile.close()

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
sleepRatio = sleeping/totalSleep
avgHumid = round((totalHumid/count), 2)
avgTemp = round((totalTemp/count), 2)
print(round(sleepRatio, 3))
print(avgHumid, avgTemp)

with open("sleepRatio.txt", 'a') as sleepFile:
    sleepFile.writelines(sleepRatio + "," + avgTemp)
sleepFile.close()