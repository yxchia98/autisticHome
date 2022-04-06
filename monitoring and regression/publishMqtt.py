from paho.mqtt import client as mqtt_client
import json

broker = "192.168.0.100"
port = 1883
client_id = '114'

username = ""
password = ""
topic = "user/preferredTemp"

humdity = 0

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

def publish(client, temperature):
    tempJson = {"temperature": round(temperature, 2)}
    temperatureSend = json.dumps(tempJson)
    client.publish(topic, temperatureSend, retain=True)
    print("Published:", temperatureSend, "to Topic: ", topic)

def run(temperature):
    client = connect_mqtt()
    # publish value
    publish(client, temperature)
    # client.loop_forever()