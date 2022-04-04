import time
from paho.mqtt import client as mqtt_client
import random
import json


MQTT_BROKER = '192.168.0.100'
MQTT_PORT = 1883
MQTT_CLIENT_ID = f'python-mqtt-light-{random.randint(0, 1000)}'
MQTT_LIGHT_TOPIC = "zigbee2mqtt/Aqara Motion Sensor"
MQTT_SUBSCRIBE_TOPICS = [
    ("zigbee2mqtt/Aqara Motion Sensor", 1), ("tasmota/stat/tasmota-plug1/RESULT", 1), ("zigbee2mqtt/SLEEPSTATE", 1)]
MQTT_LIGHT_SWITCH_TOPIC = "tasmota/cmnd/tasmota-plug1/POWER"
sleepStatus = 'off'
lightState = 'ON'
lumens = 20
motion = False


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
    global lumens, lightState, sleepStatus, motion, temperature

    # SET CURRENT STATES
    msg = str(message.payload.decode("utf-8"))
    print(msg)
    obj = json.loads(msg)

    sleepStatus = str(
        obj['state']) if 'state' in obj and message.topic == 'zigbee2mqtt/SLEEPSTATE' else sleepStatus
    print('Sleep status:', sleepStatus)

    lumens = int(
        obj['illuminance']) if 'illuminance' in obj and message.topic == 'zigbee2mqtt/Aqara Motion Sensor' else lumens

    lightState = str(
        obj['POWER']) if 'POWER' in obj and message.topic == 'tasmota/stat/tasmota-plug1/RESULT' else lightState

    motion = obj['occupancy'] if 'occupancy' in obj and message.topic == 'zigbee2mqtt/Aqara Motion Sensor' else motion

    print('sleep:', sleepStatus, 'light:', lightState,
          'lumens:', lumens, 'motion:', motion)

    # EVENTS
    if sleepStatus == 'on':
        if lightState != 'OFF':
            publish(client, MQTT_LIGHT_SWITCH_TOPIC, 'OFF')
            print(
                'Entering sleep mode, turning off lights...')

    else:
        if not motion and lightState != 'OFF':
            publish(client, MQTT_LIGHT_SWITCH_TOPIC,
                    'OFF') if lightState != 'OFF' else ''
            print(
                'no motion detected or sleep state enabled, turning off lights and fans...')

        if lumens <= 10 and lightState != 'ON' and motion:
            publish(client, MQTT_LIGHT_SWITCH_TOPIC,
                    'ON') if lightState != 'ON' else ''
            print('turning on the lights...')

        if lumens > 10 and lightState != 'OFF' and motion:
            publish(client, MQTT_LIGHT_SWITCH_TOPIC,
                    'OFF') if lightState != 'OFF' else ''
            print('turning off the lights...')

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
