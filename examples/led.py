#!/usr/bin/python3
import RPi.GPIO as GPIO
import requests
import socket
import threading
import logging
import time

# change this to the values from MCS web console
DEVICE_INFO = {
    'device_id' : 'DWC50qSX',
    'device_key' : 'i9X6Pky0S7bgpjS5'
}
# change 'INFO' to 'WARNING' to filter info messages
logging.basicConfig(level='INFO')
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.OUT)
heartBeatTask = None

def establishCommandChannel():
    # Query command server's IP & port
	connectionAPI = 'https://api.mediatek.com/mcs/v2/devices/%(device_id)s/connections.csv'
	r = requests.get(connectionAPI % DEVICE_INFO,headers = {'deviceKey' : DEVICE_INFO['device_key'],'Content-Type' : 'text/csv'})
	logging.info("Command Channel IP,port=" + r.text)
	(ip, port) = r.text.split(',')

	# Connect to command server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, int(port)))
	s.settimeout(None)

    # Heartbeat for command server to keep the channel alive
	def sendHeartBeat(commandChannel):
		keepAliveMessage = '%(device_id)s,%(device_key)s,0' % DEVICE_INFO
		s=keepAliveMessage.encode('utf-8')
		commandChannel.sendall(s)
		logging.info("beat:%s" % s)

	def heartBeat(commandChannel):
		sendHeartBeat(commandChannel)
		# Re-start the timer periodically
		global heartBeatTask
		heartBeatTask = threading.Timer(40, heartBeat, [commandChannel]).start()
	heartBeat(s)
	return s

def waitAndExecuteCommand(commandChannel):
	while True:
		command = commandChannel.recv(1024)
		command = command.decode('utf-8')
		logging.info("recv:" + command)
		# command can be a response of heart beat or an update of the LED_control,
		# so we split by ',' and drop device id and device key and check length
		fields = command.split(',')[2:]
		if len(fields) > 1:
			timeStamp, dataChannelId, commandString = fields
			if dataChannelId == 'led':
				# check the value - it's either 0 or 1
				commandValue = int(commandString)
				#logging.info("led :%d" % commandValue)
				setLED(commandValue)
		time.sleep(0.1)
def setLED(state):
	if state:
		GPIO.output(4,1)
	else:
		GPIO.output(4,0)

if __name__ == '__main__':
    	channel = establishCommandChannel()
    	waitAndExecuteCommand(channel)
