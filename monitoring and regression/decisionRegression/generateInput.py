humidity = 70.00
temperature = 26.00

arr = []
while(humidity < 90):
    temperature = 26.00
    while(temperature < 32):
        temp = [round(humidity, 2), round(temperature, 2)]
        arr.append(temp)
        temperature += 0.01

    humidity += 0.01    

with open("inputList.txt", "a") as inputFile:
    for items in arr:
        h = items[0]
        t = items[1]
        inputFile.writelines(str(h) + "," + str(t) + "\n")
inputFile.close()