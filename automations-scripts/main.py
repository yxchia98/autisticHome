import time
from paho.mqtt import client as mqtt_client
import random
import json


MQTT_BROKER = '192.168.0.100'
MQTT_PORT = 1883
MQTT_CLIENT_ID = f'python-mqtt-light-{random.randint(0, 1000)}'
MQTT_LIGHT_TOPIC = "zigbee2mqtt/Aqara Motion Sensor"
MQTT_SUBSCRIBE_TOPICS = [
    ("zigbee2mqtt/Aqara Motion Sensor", 0), ("zigbee2mqtt/Aqara Temperature Sensor", 0), ("tasmota/stat/tasmota-plug1/RESULT",
                                                                                          0), ("tasmota/stat/tasmota-plug2/RESULT", 0), ("tasmota/stat/tasmota-aoycocr1/RESULT", 0),
    ("zigbee2mqtt/Mi Button", 0)]
MQTT_LIGHT_SWITCH_TOPIC = "tasmota/cmnd/tasmota-plug1/POWER"
MQTT_FAN_SWITCH_TOPIC = "tasmota/cmnd/tasmota-plug2/POWER"
MQTT_AIRCON_SWITCH_TOPIC = "tasmota/cmnd/tasmota-aoycocr1/POWER"
MQTT_AIRCON_STATE_TOPIC = "aircon/TEMPERATURE"
TEMP_THRESHOLD = 28.0
sleepStatus = False
lightState = 'ON'
fanState = 'ON'
airconState = 'ON'
lumens = 20
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
    global lumens, lightState, fanState, airconState, sleepStatus, motion, temperature

    # SET CURRENT STATES
    obj = json.loads(str(message.payload.decode("utf-8")))
    sleepStatus = not sleepStatus if 'action' in obj and message.topic == 'zigbee2mqtt/Mi Button' and obj[
        'action'] == 'triple' else sleepStatus
    print('Sleep status:', sleepStatus)

    lumens = int(obj['illuminance']) if 'illuminance' in obj else lumens

    lightState = str(
        obj['POWER']) if 'POWER' in obj and message.topic == 'tasmota/stat/tasmota-plug1/RESULT' else lightState

    fanState = str(
        obj['POWER']) if 'POWER' in obj and message.topic == 'tasmota/stat/tasmota-plug2/RESULT' else fanState

    airconState = str(
        obj['POWER']) if 'POWER' in obj and message.topic == 'tasmota/stat/tasmota-aoycocr1/RESULT' else airconState

    motion = obj['occupancy'] if 'occupancy' in obj else motion

    temperature = float(
        obj['temperature']) if 'temperature' in obj and message.topic == 'zigbee2mqtt/Aqara Temperature Sensor' else temperature

    # EVENTS
    if sleepStatus:
        print('Entered sleep mode...')
        if lightState != 'OFF' or fanState != 'OFF' or airconState != 'OFF':
            publish(client, MQTT_LIGHT_SWITCH_TOPIC, 'OFF')
            publish(client, MQTT_FAN_SWITCH_TOPIC, 'OFF')
            publish(client, MQTT_AIRCON_SWITCH_TOPIC, 'OFF')
            print(
                'no motion detected or sleep state enabled, turning off lights and fans...')

    else:
        if not motion and (lightState != 'OFF' or fanState != 'OFF' or airconState != 'OFF'):
            publish(client, MQTT_LIGHT_SWITCH_TOPIC, 'OFF')
            publish(client, MQTT_FAN_SWITCH_TOPIC, 'OFF')
            publish(client, MQTT_AIRCON_SWITCH_TOPIC, 'OFF')
            print(
                'no motion detected or sleep state enabled, turning off lights and fans...')

        if lumens <= 10 and lightState != 'ON' and motion and not sleepStatus:
            publish(client, MQTT_LIGHT_SWITCH_TOPIC, 'ON')
            print('turning on the lights...')

        if lumens > 10 and lightState != 'OFF' and motion and not sleepStatus:
            publish(client, MQTT_LIGHT_SWITCH_TOPIC, 'OFF')
            print('turning off the lights...')

        if temperature > TEMP_THRESHOLD and fanState != 'ON' and motion and not sleepStatus:
            publish(client, MQTT_FAN_SWITCH_TOPIC, 'ON')
            print('turning on the fan...')

        if temperature <= TEMP_THRESHOLD and fanState != 'OFF' and motion and not sleepStatus:
            publish(client, MQTT_FAN_SWITCH_TOPIC, 'OFF')
            print('turning on the fan...')

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
