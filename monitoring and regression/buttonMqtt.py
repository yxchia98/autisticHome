from paho.mqtt import client as mqtt_client
from datetime import datetime
import json

broker = "192.168.0.100"
port = 1883
topic = "zigbee2mqtt/Mi Button"
client_id = '111'

username = ""
password = ""

sleepStatus = False

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
        global lightStatus
        data = msg.payload.decode()
        
        print(f"Received `{data}` from `{msg.topic}` topic")

        jsonObj = json.loads(data)
        action = jsonObj["action"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if(action == "triple"):
            sleep = not(sleepStatus)
            output = str(action) + "," + str(sleepStatus) + "," + str(now) + "\n"
            print(output)
             # write to text file
            with open("button.txt", 'a') as file:
                file.writelines(output)
            file.close()
            

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    suscribe(client)
    client.loop_forever()

run()    
    