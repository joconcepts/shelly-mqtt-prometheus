#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json, time, threading, uuid, re, os
from prometheus_client import start_http_server, Gauge

CHANNEL_MAP = ["L1", "L2", "L3"]

class Client:
    def __init__(self, host, port, user, passwd):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.uuid = str(uuid.uuid4())
        self.metrics = {
                "power": Gauge('shelly_power', 'Measured power consumption', ['device', 'channel']),
                "current": Gauge('shelly_current', 'Measured current', ['device', 'channel']),
                "voltage": Gauge('shelly_voltage', 'Measured voltage', ['device', 'channel'])
                }

    def connect(self):
        c = mqtt.Client(client_id=self.uuid)
        c.username_pw_set(self.user, self.passwd)
        c.on_connect = self.on_connect
        c.on_message = self.on_message
        c.connect(self.host, self.port, 60)
        self.client = c

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("shellies/#")

    def on_message(self, client, userdata, msg):
        regex = re.compile("^shellies/(\S+)/emeter/(\d+)/(power|current|voltage)$")
        match = regex.match(msg.topic)
        if match:
            value = msg.payload.decode()
            print("Matched topic %s: %s" % (msg.topic, value))
            device = match.group(1)
            sensor = match.group(3)
            channel = CHANNEL_MAP[int(match.group(2))]
            self.metrics[sensor].labels(device, channel).set(value)

MQTT_HOST = os.environ.get('MQTT_HOST', "127.0.0.1")
MQTT_PORT = os.environ.get('MQTT_PORT', 1883)
MQTT_USER = os.environ.get('MQTT_USER', "")
MQTT_PASS = os.environ.get('MQTT_PASS' "")
PORT = os.environ.get('PORT', 8000)

start_http_server(PORT)

main_client = Client(MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASS)
main_client.connect()

main_client.client.loop_forever()

