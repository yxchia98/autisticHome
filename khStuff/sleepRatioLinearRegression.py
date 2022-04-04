import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
import publishMqtt as mqtt 

df =pd.read_csv("sleepRatio.txt")
print(df)

plt.xlabel("temperature")
plt.ylabel("sleep ratio")
plt.scatter(df.temperature, df.sleepRatio)

tempArr = []
for items in df["temperature"]:
    tempArr.append(items)

sleepRatioArr=[]
for items in df["sleepRatio"]:
    sleepRatioArr.append(items)

x = np.array(tempArr)
y = np.array(sleepRatioArr)
reg = linear_model.LinearRegression()
reg.fit(y.reshape(-1,1), df.temperature)

prediction = reg.predict([[0.8]])
print(prediction[0])

# mqtt.run(prediction[0])