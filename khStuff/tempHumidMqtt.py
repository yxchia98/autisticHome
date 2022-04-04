from paho.mqtt import client as mqtt_client
from datetime import datetime
import json

broker = "192.168.0.100"
port = 1883
topic = "zigbee2mqtt/Aqara Temperature Sensor"
client_id = '111'

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
        humidity = jsonObj["humidity"]
        temperature = jsonObj["temperature"] 
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        output = str(humidity) + "," + str(temperature) + "," + str(now) + "\n"
        print(output)
        # write to text file
        with open("tempHumid.txt", 'a') as file:
            file.writelines(output)
        file.close()

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    suscribe(client)
    client.loop_forever()

run()    
    