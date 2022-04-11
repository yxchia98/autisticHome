from paho.mqtt import client as mqtt_client
from datetime import datetime
import json
import csv

broker = "192.168.0.100"
port = 1883
topic = "zigbee2mqtt/Mi Motion"
client_id = '112'

username = ""
password = ""


def connect_mqtt():
    def on_connect(client, userData, flags, rc):
        if rc == 0:
            print("Connected to mqtt server")
        else:
            print("Failed to connect to mqtt server")

    # setting client
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client        

def suscribe(client: mqtt_client):
    def on_message(client, userData, msg):
        
        data = msg.payload.decode()
        
        print(f"Received `{data}` from `{msg.topic}` topic")

        jsonObj = json.loads(data)
        motion = jsonObj["occupancy"]
         
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        output = str(motion) + "," + str(now) + "\n"
        print(output)
        check = False
        # write to text file
        with open("motion.txt", 'r') as checkFile:
            csv_reader = csv.reader(checkFile, delimiter=',')
            for line in csv_reader:
                pass
            lastLine = line
            checkDate = lastLine[1]
            checkTime  = datetime.strptime(checkDate, '%Y-%m-%d %H:%M')
            if(checkTime != now):
                check = True
        checkFile.close()
        if(check):
            with open("motion.txt", 'a') as file:
                file.writelines(output)
            file.close()

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    suscribe(client)
    client.loop_forever()

run()    
    