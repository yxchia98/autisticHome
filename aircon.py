import time
from paho.mqtt import client as mqtt_client
import random
import json


MQTT_BROKER = '192.168.0.100'
MQTT_PORT = 1883
MQTT_CLIENT_ID = f'python-mqtt-light-{random.randint(0, 1000)}'
MQTT_LIGHT_TOPIC = "zigbee2mqtt/Aqara Motion Sensor"
MQTT_SUBSCRIBE_TOPICS = [
    ("user/preferredTemp", 1), ("tasmota/stat/tasmota-aoycocr1/RESULT", 1), ("zigbee2mqtt/SLEEPSTATE", 1)]
MQTT_AIRCON_SWITCH_TOPIC = "tasmota/cmnd/tasmota-aoycocr1/POWER"
MQTT_AIRCON_STATE_TOPIC = "aircon/TEMPERATURE"
TEMP_THRESHOLD = 28.0
sleepStatus = 'off'
airconState = 'OFF'
temperature = 0.0


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)


def connect_mqtt() -> mqtt_client:
    client = mqtt_client.Client(MQTT_CLIENT_ID)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client


def on_message(client, userdata, message):
    global airconState, sleepStatus, temperature

    # SET CURRENT STATES
    obj = json.loads(str(message.payload.decode("utf-8")))
    sleepStatus = str(
        obj['state']) if 'state' in obj and message.topic == 'zigbee2mqtt/SLEEPSTATE' else sleepStatus
    print('Sleep status:', sleepStatus)

    airconState = str(
        obj['POWER']) if 'POWER' in obj and message.topic == 'tasmota/stat/tasmota-aoycocr1/RESULT' else airconState
    print('Aircon State:', airconState)

    temperature = float(
        obj['temperature']) if 'temperature' in obj and message.topic == 'user/preferredTemp' else temperature

    # EVENTS
    if sleepStatus == 'on':
        if airconState != 'ON':
            publish(client, MQTT_AIRCON_SWITCH_TOPIC, 'ON')
            print(
                'Entering sleep mode, turning on aircon...')
            publish(client, MQTT_AIRCON_STATE_TOPIC, temperature)
            print(
                f'Setting aircon to user preferred temperature of {temperature}...'
            )

    else:
        if airconState != 'OFF':
            publish(client, MQTT_AIRCON_SWITCH_TOPIC,
                    'OFF') if airconState != 'OFF' else ''
            print(
                'not in sleep mode, turning off aircon...')

    print("received message: ", str(
        message.payload.decode("utf-8")), "topic: ", message.topic)


def subscribe(client: mqtt_client):
    client.subscribe(MQTT_SUBSCRIBE_TOPICS)
    client.on_message = on_message


def publish(client, topic, message):
    msg = f"{message}"
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


if __name__ == '__main__':
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()
