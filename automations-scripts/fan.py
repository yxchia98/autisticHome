import time
from paho.mqtt import client as mqtt_client
import random
import json


MQTT_BROKER = '192.168.0.100'
MQTT_PORT = 1883
MQTT_CLIENT_ID = f'python-mqtt-light-{random.randint(0, 1000)}'
MQTT_LIGHT_TOPIC = "zigbee2mqtt/Aqara Motion Sensor"
MQTT_SUBSCRIBE_TOPICS = [
    ("zigbee2mqtt/Aqara Temperature Sensor", 1), ("zigbee2mqtt/Aqara Motion Sensor", 1), ("tasmota/stat/tasmota-plug2/RESULT", 1), ("zigbee2mqtt/SLEEPSTATE", 1)]
MQTT_FAN_SWITCH_TOPIC = "tasmota/cmnd/tasmota-plug2/POWER"
TEMP_THRESHOLD = 25.0
fanState = 'OFF'
sleepStatus = 'off'
motion = False
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
    global fanState, sleepStatus, motion, temperature

    # SET CURRENT STATES
    msg = str(message.payload.decode("utf-8"))
    print(msg)
    obj = json.loads(msg)

    sleepStatus = str(
        obj['state']) if 'state' in obj and message.topic == 'zigbee2mqtt/SLEEPSTATE' else sleepStatus
    print('Sleep status:', sleepStatus)

    fanState = str(
        obj['POWER']) if 'POWER' in obj and message.topic == 'tasmota/stat/tasmota-plug2/RESULT' else fanState

    motion = obj['occupancy'] if 'occupancy' in obj and message.topic == 'zigbee2mqtt/Aqara Motion Sensor' else motion

    temperature = float(
        obj['temperature']) if 'temperature' in obj and message.topic == 'zigbee2mqtt/Aqara Temperature Sensor' else temperature

    # EVENTS
    if sleepStatus == 'on':
        if fanState != 'OFF':
            publish(client, MQTT_FAN_SWITCH_TOPIC, 'OFF')
            print(
                'Entering sleep mode, turning off fans...')

    else:
        if not motion and fanState != 'OFF':
            publish(client, MQTT_FAN_SWITCH_TOPIC,
                    'OFF') if fanState != 'OFF' else ''
            print(
                'no motion detected or sleep state enabled, turning off fans')

        if temperature >= TEMP_THRESHOLD and fanState != 'ON' and motion:
            publish(client, MQTT_FAN_SWITCH_TOPIC,
                    'ON') if fanState != 'ON' else ''
            print('turning on the fans...')

        if temperature < TEMP_THRESHOLD and fanState != 'OFF' and motion:
            publish(client, MQTT_FAN_SWITCH_TOPIC,
                    'OFF') if fanState != 'OFF' else ''
            print('turning off the fans...')

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
