from paho.mqtt import client as mqtt_client
import json

broker = '192.168.0.100'
port = 1883
subscribetopic = "zigbee2mqtt/Aqara Temperature Sensor"
publishAirconToggleTopic = "tasmota/cmnd/tasmota-aoycocr1/POWER"
publishAirconTempTopic = "aircon/TEMPERATURE"
client_id = '112'

sleepStatus = True

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_message(client, userdata, msg):
    json_data = json.loads(msg.payload.decode())
    pref_temp_json_data = str(json_data["temperature"])

    publish(client, pref_temp_json_data)

def subscribe(client: mqtt_client):
    client.subscribe(subscribetopic)
    client.on_message = on_message

def publish(client, pref_temp_json_data):
    client.publish(publishAirconToggleTopic, "on")
    client.publish(publishAirconTempTopic, pref_temp_json_data)

def run():
    client = connect_mqtt()

    if sleepStatus:
        subscribe(client)

    client.loop_forever()

if __name__ == '__main__':
    run()