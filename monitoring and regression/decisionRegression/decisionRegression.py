from black import Line
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
import json
from matplotlib import pyplot as plt
import pandas as pd

CONSTANT = 3

xVar1 = "temperature"
xVar2 = "humidity"
xVar3 = "luminous"
yVar = "sleep hours"

# read data from file
# inputArr = []
# with open("data.txt", 'r') as inputFile:
#     for lines in inputFile:
#         lines = lines.rstrip('\n')
#         lines = json.loads(lines)
#         inputArr.append(lines)
# inputFile.close()

# # for element in inputArr:
# #     print(element)

# xVar1Arr = []
# xVar2Arr = []
# yVarArr = []

# for lines in inputArr:
#     status = lines["Status"]
#     if(status == "True"):
#         statusNo = 1
#     else:
#         statusNo = 0
#     yVarArr.append(statusNo)
#     xVar1Arr.append(float(lines["humidity"]))
#     xVar2Arr.append(float(lines["temperature"]))



# x = np.array([xVar1Arr, xVar2Arr])
# y = np.dot(x, np.array(yVarArr)) + CONSTANT
# reg = LinearRegression().fit(x, y)

# score = reg.score(x, y)
# print(reg.predict(np.array([[72.54,31.00]])))

# get input list
inputList = []
with open("inputList.txt", 'r') as inputFile:
    for lines in inputFile:
        line = lines.split(",")
        line[1] = line[1].replace("\n", "")
        inputList.append(line)

df = pd.read_csv("data2.txt")
X = df.drop(columns=["status", "date"])
y = df["status"]

model = DecisionTreeClassifier()
model.fit(X.values, y.values)

predictions = model.predict(inputList)

indexArr = []
for index, item in enumerate(predictions):
    if item == False:
        indexArr.append(index)

print(predictions)
print(inputList[444444])
targetTemp = inputList[444444][1]


# with open("outputList.txt", 'a') as outputFile:
#     for line in indexArr:
#         toWrite = str(inputList[line])
#         outputFile.writelines(toWrite + '\n')
# outputFile.close()

import publishMqtt as mqtt
mqtt.run(targetTemp)


