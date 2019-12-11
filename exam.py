#!/usr/bin/python3
import time,RPi.GPIO as GPIO
import urllib
import http.client as http
import sys
import json
deviceId="DGfq6Z75"
deviceKey="hj52Fg9lXrkVS5aX"
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_UP)

def post_to_mcs(payload):
	headers = {"Content-type": "application/json", "deviceKey":deviceKey} 
	not_connected = 1 
	while (not_connected):
		try:
			conn = http.HTTPConnection("api.mediatek.com:80")
			conn.connect() 
			not_connected = 0 
		except (http.HTTPException, socket.error) as ex: 
			print ("Error: %s" % ex)
	conn.request("POST", "/mcs/v2/devices/" + deviceId + "/datapoints", json.dumps(payload), headers) 
	response = conn.getresponse() 
	print( response.status, response.reason, json.dumps(payload), time.strftime("%c")) 
	data = response.read() 
	conn.close() 

while True:
	ss=GPIO.input(27)
	if (ss==1):
		ss=0
		print("放")
		payload = {"datapoints":[{"dataChnId":"Switch","values":{"value":ss}}]}
		post_to_mcs(payload)
	else:
		ss=1
		print("壓")
		payload = {"datapoints":[{"dataChnId":"Switch","values":{"value":ss}}]}
		post_to_mcs(payload)
	time.sleep(5)
