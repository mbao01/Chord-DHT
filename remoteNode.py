#!/bin/python3
import sys
import json
import socket
import random
import time

import threading
from config import NBITS,SIZE

def requires_connection(func):
	def inner(self, *args, **kwargs):
		self._mutex.acquire()
		self.open_connection()
		ret = func(self, *args, **kwargs)
		self.close_connection()
		self._mutex.release()
		return ret
	return inner
# This class will help to invoke remote prodedure calls
# One remoteNode will simulate one remote node
# RemoteObject will call the remote machine/process usnig socker -invoke 
# someting on actual remote pc
# get reply and give it back to us (local machine) --  simulating RPC
class RemoteNode(object):
	def __init__(self, remoteAddress = None):
		self._address = remoteAddress
		# many node can create an RemoteNode with same IP,PORT
		# to safegurd the socket  open connectiona/send/close connection Ops
		self._mutex = threading.Lock()

	def open_connection(self):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.connect((self._address.ip, self._address.port))

	def close_connection(self):
		self._socket.close()
		self._socket = None

	def __str__(self):
		return "Remote %s" % self._address # this _address object has already 

	def id(self, offset = 0):
		return (self._address.__hash__() + offset) % SIZE

	def send(self, msg):
		self.socket_.sendall(msg + "\r\n")
		self.last_msg_send_ = msg

	def recv(self):
		# print "send: %s <%s>" % (msg, self._address)
		# we use to have more complicated logic here
		# and we might have again, so I'm not getting rid of this yet
		return read_from_socket(self.socket_)

	# This function is just to check whether is this remote machine is up or not
	def ping(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self._address.ip, self._address.port))
			s.sendall("\r\n") 	# this a dummy string:
								# we have used this all over the place
			s.close()
			return True
		except socket.error:
			return False

	@requires_connection
	def findSuccessor(self,id):
		self.send('findSuccessor %s' % id)
		response = self.recv()
		response = json.loads(response)
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def successor(self): # this is not findSuccessor
		self.send('get_successor')
		response = self.recv()
		response = json.loads(self.recv())
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def predecessor(self): # this is not findPredecessor
		self.send('predecessor')
		response = self.recv()
		response = json.loads(response)
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def findSuccessor(self, id):
		self.send('findSuccessor %s' % id)

		response = json.loads(self.recv())
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def closest_precedingFinger(self, id):
		self.send('closest_preceding_finger %s' % id)

		response = json.loads(self.recv())
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def notify(self, node):
		self.send('notify %s %s' % (node._address.ip, node._address.port))
