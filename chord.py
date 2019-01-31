#!/bin/python3
# CODE not tested !!!!!!!!!!!!!!!!!!!!!!
# overall login is prepared : check the remoteNode file also
import sys
import json
import socket
import random
import time
from threading import Thread, Lock
from config import NBITS,SIZE,SLEEP_TIME
from remoteNode import RemoteNode

# This is a wrapper function
def LoopAndWait(func):
	def inner(self, *args, **kwargs):
		while 1:
			time.sleep(SLEEP_TIME)
			ret = func(self, *args, **kwargs)
			return ret
	return inner

class BackGroundProcess:
	def __init__(self, obj, method):
		threading.Thread.__init__(self)
		self.obj_ = obj
		self.method_ = method

	def run(self):
		getattr(self.obj_, self.method_)()

class Node:
    def __init__(self, localAdress, RemoteAddress = None):
        self._address = localAdress
        self._threads = {}
        self._finger  = {}   
        for idx in range(BITS):
            self._finger[0] = None
        self.join(RemoteAddress)
    
    def join(self,RemoteAddress = None):
        if RemoteAddress:
			remoteInstance = RemoteNode(RemoteAddress)
			self._seccessor = remoteInstance.find_successor(self.id())
		else:
			self._seccessor = self # fot the node-0
		
		self._finger[0] = self._seccessor
		self.log(self._address," joined.")
		
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
		self._threads['updateSuccessors'] = BackGroundProcess(self, 'updateSuccessors')
		for key in self._threads:
			self._threads[key].start()

		self.log("started")	

	
	@LoopAndWait
	def stabilize(self):
		self.log("stabilize")
		suc = self.successor()
		x = suc.predecessor()
		if x != None and (inrange(x.getIdentifier(), self.getIdentifier(1), suc.getIdentifier())) and (self.id(1) != suc.id()):
			self._successor = x
			self._finger[0] = x
		self._successor.notify(self)
		return True

	def notify(self, remote):
		self.log("notify")
		if self.predecessor() == None or (inrange(remote.id(), self.predecessor().id(1), self.id())):
			self._predecessor = remote

	@LoopAndWait
	def fixFingers(self):
		# we can use a static varible abstration instead of a random int
		self.log("fixFingers")
		i = random.randrange(NBITS - 1) + 1
		self.finger_[i] = self.findSuccessor(self.id(1<<i))
		return True

	@LoopAndWait
	def checkPredecessors(self):
		self.log("checkPredecessors")
		# check the predecessor is up or not
		if self._predecessor.ping() == False
			self._predecessor = None


	def id(self, offset = 0):
		return (self.address_.__hash__() + offset) % SIZE

	def findSuccessor(self, id):
		# check paper for implementation
		self.log("find_successor")
		if inrange(id, self.predecessor().id(1), self.id(1)): # TODO check the offsets
			return self
		node = self.find_predecessor(id)
		return node.successor()

	def closestPrecedingNode(self, id):
		# check paper for implementation
		self.log("closest_preceding_finger")
		for idx in reversed(range(NBITS)):
			if self._finger[idx] != None and inrange(self._finger[idx].id(1), self.id(1), id)
				return self._finger[idx]
		return self
			
	def run(self):

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.bind((self.address_.ip, int(self.address_.port)))
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
				result = json.dumps((successor.address_.ip, successor.address_.port))
			if command == 'get_predecessor':
				# we can only reply if we have a predecessor
				if self.predecessor_ != None:
					predecessor = self.predecessor_
					result = json.dumps((predecessor.address_.ip, predecessor.address_.port))
			if command == 'find_successor':
				successor = self.find_successor(int(request))
				result = json.dumps((successor.address_.ip, successor.address_.port))
			if command == 'closest_preceding_finger':
				closest = self.closest_preceding_finger(int(request))
				result = json.dumps((closest.address_.ip, closest.address_.port))
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
		local = Local(Address("127.0.0.1", sys.argv[1]))
	else:
		local = Local(Address("127.0.0.1", sys.argv[1]), Address("127.0.0.1", sys.argv[2]))
	local.start()