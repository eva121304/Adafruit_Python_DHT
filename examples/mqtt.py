#!/usr/bin/python3

import http.client as http
import paho.mqtt.client as mqtt
import time
import sys
import urllib
import json
import Adafruit_DHT

deviceId = "DWC50qSX"
deviceKey="i9X6Pky0S7bgpjS5"
dataChnId1="Humidity"
dataChnId2="Temperature"

MQTT_SERVER="mqtt.mcs.mediatek.com"
MQTT_PORT=1883
MQTT_ALIVE=60
MQTT_TOPIC1="mcs/" + deviceId + "/" + deviceKey + "/"+dataChnId1
MQTT_TOPIC2="mcs/" + deviceId + "/" + deviceKey + "/"+dataChnId2


def on_publish(client,userdata,result):
	print("success")
	pass
mqtt_client=mqtt.Client()
mqtt_client.on_publish=on_publish
mqtt_client.connect(MQTT_SERVER, MQTT_PORT)
ret=mqtt_client.publish(MQTT_TOPIC1)
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>')
    print('Example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')
    sys.exit(1)

while True:
	
	h0, t0= Adafruit_DHT.read_retry(sensor, pin)
	print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(t0,h0))
	payload = {"datapoints":[{"dataChnId":"Humidity","values":{"value":h0}}]}
	mqtt_client.publish(MQTT_TOPIC1,json.dumps(payload),qos=1)
	print(ret)
	payload = {"datapoints":[
{"dataChnId":"Temperature","values":{"value":t0}}]}
	mqtt_client.publish(MQTT_TOPIC2,json.dumps(payload),qos=2)
	print(ret)
	mqtt_client.on_publish
	time.sleep(1)
