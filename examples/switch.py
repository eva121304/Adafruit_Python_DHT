#!/usr/bin/python3

import RPi.GPIO as GPIO
import sys
import time
import Adafruit_DHT
import http.client as http
import urllib
import json

GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

#MCS client

deviceid = "DWC50qSX"

deviceKey = "i9X6Pky0S7bgpjS5"

def post_to_mcs(payload):
	headers = {"Content-type":"application/json","deviceKey":deviceKey}
	not_connected = 1
	while(not_connected):
		try:
			conn = http.HTTPConnection("api.mediatek.com:80")
			conn.connect()
			not_connected = 0
		except(http.HTTPException) as ex:
			print("Error:%s"%ex)
			time.sleep(10)
	conn.request("POST","/mcs/v2/devices/"+deviceid+"/datapoints",json.dumps(payload),headers)

	response = conn.getresponse()
	print(response.status,response.reason,json.dumps(payload),time.strftime("%c"))
	data = response.read()
	conn.close()	

# Parse command line parameters.

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

# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

while True:
	h0,t0 = Adafruit_DHT.read_retry(sensor,pin)
	Switch = GPIO.input(24)

	if h0 is not None and t0 is not None:
		print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(t0, h0))
		print(Switch)
		payload = {"datapoints":[{"dataChnId":"Humidity","values":{"value":h0}},{"dataChnId":"Temperature","values":{"value":t0}},{"dataChnId":"Switch","values":{"value":Switch}}]} 

		post_to_mcs(payload)
	else:
		 print('Failed to get reading. Try again')
		 sys.exit(1)
