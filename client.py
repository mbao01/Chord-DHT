#!/bin/python3
import sys
import json
import socket
import random
import time

import threading
from config import *
from network import *
from address import *

def requires_connection(func):
	def inner(self, *args, **kwargs):
		self.open_connection()
		ret = func(self, *args, **kwargs)
		self.close_connection()
		return ret
	return inner


class ClientNode(object):
	def __init__(self,RemoteAddress = None):
		if RemoteAddress == None:
			print("Please enter one chord Node address !")
			exit(-1)

		self._serverAddress = RemoteAddress
		self.client_running = True
		self.start()
	
	def open_connection(self):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.connect((self._serverAddress.ip, self._serverAddress.port))

	def close_connection(self):
		self._socket.close()
		self._socket = None
	
	def printPromt(self):
		print("Enter 1 to Lookup")
		print("Enter 2 to Insert")
		print("Enter 3 to FingerTable")
		#print("Enter 4 to ShowDB")
		print("Enter 4 to Exit")

	def send(self, msg):
		send_to_socket(self._socket,msg)
		self.last_msg_send_ = msg

	def recv(self):
		return read_from_socket(self._socket)
	
	@requires_connection
	def lookUpKey(self,key):
		self.send('lookUpKey '+key)
		return self.recv()

	@requires_connection
	def insertKeyVal(self,key,value):
		self.send('insertKeyVal '+key+' '+value)	
		return self.recv()

	@requires_connection
	def queryFingerTable(self):
		self.send('getFingerTable')
		return self.recv()
	
	def start(self):
		while self.client_running:
			self.printPromt()
			choice  = input("Enter your choice :")
			if choice=='1':
				key = input("Input Key :") #TODO check type
					
				returnvalue = self.lookUpKey(key)
				
				if returnvalue == '-1':
					print("Key :",key," not found !!")
				else:
					print("Key : ",key," :: Value : ",returnvalue)

				break
			if choice=='2':
				key = input("Input Key :") # TODO type check
				value = input("Input Value :") # TODO type check

				returnvalue = self.insertKeyVal(key,value)
					# key-value are always inserted !

				print("Key : ",key," :: Value : ",value," inserted")
				break

			if choice =='3':
				response = self.queryFingerTable()
				print(response)
				break

			if choice == '4':
				self.client_running = False

if __name__ == "__main__":
	import sys
	if len(sys.argv) == 3:
		local = ClientNode(Address(sys.argv[1], sys.argv[2]))
	else:
		print("Insufficient argumrnts")
	local.start()