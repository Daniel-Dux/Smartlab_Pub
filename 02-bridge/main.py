#!/usr/bin/env python3

"""A MQTT to InfluxDB Bridge
This script receives MQTT data and saves those to InfluxDB.
"""

import re
from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient

import time


MQTT_ADDRESS = '{URL}'
MQTT_USER = '{MQTTUser}'
MQTT_PASSWORD = '{MQTTPass}'
MQTT_TOPIC = '+/+/+'
MQTT_REGEX = '([^/]+)/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'MQTTInfluxDBBridge'

influxdb_client = InfluxDBClient(
    url='{URL}:8086', token='{Token}', org='{OrgName}')


class SensorData(NamedTuple):
    experiment: str
    device: str
    measurement: str
    value: float


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + ' ' + str(msg.payload))
    sensor_data = _parse_mqtt_message(msg.topic, msg.payload.decode('utf-8'))
    _send_sensor_data_to_influxdb(sensor_data)
    print(sensor_data)


def _parse_mqtt_message(topic, payload):
    match = re.match(MQTT_REGEX, topic)

    experiment = match.group(1)
    device = match.group(2)
    measurement = match.group(3)
    return SensorData(experiment, device, measurement, float(payload))


def _send_sensor_data_to_influxdb(sensor_data):
    json_body = [
        {
            'measurement': sensor_data.measurement,
            'tags': {
                'experiment': sensor_data.experiment,
                'device': sensor_data.device
            },
            'fields': {
                'value': sensor_data.value
            }
        }
    ]
    write_api = influxdb_client.write_api()
    write_api.write('data', 'ultracold', json_body)


def main():
    time.sleep(10)

    print('Connecting to the database')
    # _init_influxdb_database()

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('MQTT to InfluxDB bridge')
    main()
