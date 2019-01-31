#!/bin/python3
import sys
import json
import socket
import random
import time
from threading import Thread, Lock
from config import NBITS,SIZE

def requires_connection(func):
	def inner(self, *args, **kwargs):
		self.mutex_.acquire()
		self.open_connection()
		ret = func(self, *args, **kwargs)
		self.close_connection()
		self.mutex_.release()
		return ret
	return inner
# This class will help to invoke remote prodedure calls
# One remoteNode will simulate one remote node
# RemoteObject will call the remote machine/process usnig socker -invoke 
# someting on actual remote pc
# get reply and give it back to us (local machine) --  simulating RPC
class RemoteNode(object):
	def __init__(self, remote_address = None):
		self.address_ = remote_address
        # many node can create an RemoteNode with same IP,PORT
        # to safegurd the socket  open connectiona/send/close connection Ops
	    self.mutex_ = threading.Lock()

	def open_connection(self):
		self.socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket_.connect((self.address_.ip, self.address_.port))

	def close_connection(self):
		self.socket_.close()
		self.socket_ = None

	def __str__(self):
		return "Remote %s" % self.address_

	def id(self, offset = 0):
		return (self.address_.__hash__() + offset) % SIZE

	def send(self, msg):
		self.socket_.sendall(msg + "\r\n")
		self.last_msg_send_ = msg
		# print "send: %s <%s>" % (msg, self.address_)

	def recv(self):
		# we use to have more complicated logic here
		# and we might have again, so I'm not getting rid of this yet
		return read_from_socket(self.socket_)

	# This function is just to check whether is this remote machine is up or not
	def ping(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.address_.ip, self.address_.port))
			s.sendall("\r\n") 	# this a dummy string:
								# we have used this all over the place
			s.close()
			return True
		except socket.error:
			return False


	@requires_connection
	def getSuccessors(self):
		self.send('getSuccessors')

		response = self.recv()
		# if our next guy doesn't have successors, return empty list
		if response == "":
			return []
		response = json.loads(response)
		return map(lambda address: Remote(Address(address[0], address[1])) ,response)

	@requires_connection
	def successor(self):
		self.send('get_successor')

		response = json.loads(self.recv())
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def predecessor(self):
		self.send('get_predecessor')

		response = self.recv()
		if response == "":
			return None
		response = json.loads(response)
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def find_successor(self, id):
		self.send('find_successor %s' % id)

		response = json.loads(self.recv())
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def closest_preceding_finger(self, id):
		self.send('closest_preceding_finger %s' % id)

		response = json.loads(self.recv())
		return Remote(Address(response[0], response[1]))

	@requires_connection
	def notify(self, node):
		self.send('notify %s %s' % (node.address_.ip, node.address_.port))
