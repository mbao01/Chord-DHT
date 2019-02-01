#!/bin/python3
# CODE not tested !!!!!!!!!!!!!!!!!!!!!!
# overall login is prepared : check the remoteNode file also
import sys
import json
import socket
import random
import time
import threading
from address import *
from network import *
from remoteNode import *

system_running = True

class BackGroundProcess(threading.Thread):
	def __init__(self, obj, method):
		threading.Thread.__init__(self)
		self.obj_ = obj
		self.method_ = method

	def run(self):
		getattr(self.obj_, self.method_)()

class Node(object):
	def __init__(self, localAdress, RemoteAddress = None):
		self._address = localAdress
		self._threads = {}
		self._finger  = {}
		self._successor = self
		self._predecessor = None   
		for idx in range(NBITS):
			self._finger[idx] = None
		self.join(RemoteAddress)
    
	def join(self,RemoteAddress = None):
		if RemoteAddress:
			remoteInstance = RemoteNode(RemoteAddress)
			self._seccessor = remoteInstance.findSuccessor(self.id())
		else:
			self._seccessor = self # fot the node-0

		self._finger[0] = self._seccessor
		self.log(self._address.__str__() + " joined.")
		
	def getIdentifier(self, offset = 0):
		return (self._address.__hash__() + offset) % SIZE
	
	def log(self, infoData):
	    file_ = open("./logs/chord.log", "a+")
	    file_.write(str(self.id()) + " : " +  infoData + "\n")
	    file_.close()

	def start(self):
		self._threads['run'] = BackGroundProcess(self, 'run')
		self._threads['fixFingers'] = BackGroundProcess(self, 'fixFingers')
		self._threads['stabilize'] = BackGroundProcess(self, 'stabilize')
		self._threads['checkPredecessor'] = BackGroundProcess(self, 'checkPredecessor')
		for key in self._threads:
			self._threads[key].start()

		self.log(self._address.__str__() + " started")	

	# fixes the successor and predecessor 
	def stabilize(self):
		while system_running:
			self.log("stabilize")
			suc = self.successor()
			x = suc.predecessor()
			if x != None and (inrange(x.getIdentifier(), self.getIdentifier(1), suc.getIdentifier())) and (self.id(1) != suc.id()):
				self._successor = x
				self._finger[0] = x
			self._successor.notify(self)
			time.sleep(1)

	# returns the first remote node object
	def successor(self):
		return self._finger[0]

	# fixes predecesor 
	def notify(self, remote):
		self.log("notify")
		if self.predecessor() == None or (inrange(remote.id(), self.predecessor().id(1), self.id())):
			self._predecessor = remote
		print("\n\n")
		print(self._predecessor._address)
		print("\n\n")
	def predecessor(self):
		return self._predecessor

	def fixFingers(self):
		nxt = 0
		while system_running:
			self.log("fixFingers")
			nxt = nxt + 1
			if nxt > NBITS:
				nxt = 1
			self._finger[nxt - 1] = self.findSuccessor(self.id(1<<(nxt - 1)))
			self.printFingerable()
			time.sleep(1)
	def printFingerable(self):
		for idx in range(NBITS):
			if self._finger[idx] != None:
				print(self._finger[idx]._address)
			else:
				print("None")
		print("\n\n")
	def checkPredecessor(self):
		while system_running:
			self.log("checkPredecessor")
			# check the predecessor is up or not
			if self.predecessor() != None:
				if self.predecessor()._address.__hash__() != self._address.__hash__():
					if self.predecessor().ping() == False:
						self._predecessor = None
			time.sleep(1)


	def id(self, offset = 0):
		return (self._address.__hash__() + offset) % SIZE

	def findSuccessor(self, id):
		# check paper for implementation
		self.log("findSuccessor")
 
		remote = self.closestPrecedingNode(id)
		if self._address.__hash__() != remote._address.__hash__():
			return remote.findSuccessor(id)
		else:
			return self
	def closestPrecedingNode(self, id):
		# check paper for implementation
		self.log("closest_preceding_finger")
		for idx in reversed(range(NBITS)):
			if self._finger[idx] != None and inrange(self._finger[idx].id(1), self.id(1), id):
				return self._finger[idx]
		
		return self
			
	def run(self):

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind((self._address.ip, int(self._address.port)))
		self._socket.listen(10)

		while 1:
			self.log("run loop...")
	
			conn, addr = self._socket.accept()


			request = read_from_socket(conn)
			command = request.split(' ')[0]

			# we take the command out
			request = request[len(command) + 1:]

			# defaul : "" = not respond anything
			result = json.dumps("")
			if command == 'get_successor':
				successor = self.successor()
				result = json.dumps((successor._address.ip, successor._address.port))
			if command == 'get_predecessor':
				# we can only reply if we have a predecessor
				if self.predecessor_ != None:
					predecessor = self.predecessor_
					result = json.dumps((predecessor._address.ip, predecessor._address.port))
			
			if command == 'findSuccessor':
				successor = self.findSuccessor(int(request))
				result = json.dumps((successor._address.ip, successor._address.port))
			

			if command == 'closest_preceding_finger':
				closest = self.closest_preceding_finger(int(request))
				result = json.dumps((closest._address.ip, closest._address.port))
			if command == 'notify':
				npredecessor = Address(request.split(' ')[0], int(request.split(' ')[1]))
				self.notify(Remote(npredecessor))
			if command == 'get_successors':
				result = json.dumps(self.get_successors())

			# or it could be a user specified operation
			for t in self.command_:
				if command == t[0]:
					result = t[1](request)

			send_to_socket(conn, result)
			conn.close()

			if command == 'shutdown':
				self.socket_.close()
				self.shutdown_ = True
				self.log("shutdown started")
				break
		self.log("execution terminated")            


if __name__ == "__main__":
	import sys
	if len(sys.argv) == 2:
		local = Node(Address("127.0.0.1", sys.argv[1]))
	else:
		local = Node(Address("127.0.0.1", sys.argv[1]), Address("127.0.0.1", sys.argv[2]))
	local.start()