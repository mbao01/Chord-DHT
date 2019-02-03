#!/bin/python3
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
		self._predecessor = None
		self._databse = {}
		for idx in range(NBITS):
			self._finger[idx] = None
		self.join(RemoteAddress)
    
	def join(self,RemoteAddress = None):
		if RemoteAddress:
			remoteInstance = RemoteNode(RemoteAddress)
			self._finger[0] = remoteInstance.findSuccessor(self.getIdentifier())
		else:
			self._finger[0] = self # fot the node-0

		self.log(self._address.__str__() + " joined.")
		
	def getIdentifier(self, offset = 0):
		return (self._address.__hash__() + offset) % SIZE

	def __str__(self):
		return "Node %s" % self._address
	
	def log(self, infoData):
	    file_ = open("./logs/chord.log", "a+")
	    file_.write(str(self.getIdentifier()) + " : " +  infoData + "\n")
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
			#print(str(self.getIdentifier()) + " :: " + "stabilize called")
			
			if self.predecessor() != None:
				print(str(self.getIdentifier()) + " :: " + "predecessor addr : ", self.predecessor().__str__(),"predecessor id : ",self.predecessor().getIdentifier())
			if self.successor() != None:
				print(str(self.getIdentifier()) + " :: " + "successor addr : ", self.successor().__str__(),"successor id : ",self.successor().getIdentifier())
			
			print("\n\n\n")
			self.log("stabilize")
			suc = self.successor()

			# this if case added to handle two node case, when the system is starting up
			if suc == self  and self.predecessor() != None:
				self._finger[0] = self.predecessor()

			else :			
				x = suc.predecessor()
				if x != None and \
					inrange(x.getIdentifier(), self.getIdentifier(), suc.getIdentifier()) and \
					(self.getIdentifier() != suc.getIdentifier() ) and \
					(x.getIdentifier() != self.getIdentifier() ) and \
					(x.getIdentifier() != suc.getIdentifier()):
					
					self._finger[0] = x
			self.successor().notify(self)
			time.sleep(SLEEP_TIME)

	# returns the first remote node object
	def successor(self):
		return self._finger[0]

	# fixes predecesor 
	def notify(self, remote):
		#print(str(self.getIdentifier()) + " :: " + "notify called ", remote.__str__())
		self.log("notify")
		if (self.predecessor() == None or self.predecessor() == self ) or \
			( (inrange(remote.getIdentifier(), self.predecessor().getIdentifier(), self.getIdentifier())) and \
			(self.predecessor().getIdentifier() != self.getIdentifier()) and \
			(remote.getIdentifier() != self.predecessor().getIdentifier()) and \
			(remote.getIdentifier() != self.getIdentifier()) ): 
			
			self._predecessor = remote


	def predecessor(self):
		return self._predecessor

	def fixFingers(self):
		nxt = 0
		while system_running:
			#print(str(self.getIdentifier()) + " :: " + "called fixFingers")
			self.log("fixFingers")
			nxt = nxt + 1
			if nxt > NBITS:
				self.printFingerable()
				nxt = 1
			self._finger[nxt - 1] = self.findSuccessor(self.getIdentifier(1<<(nxt - 1)))
			
			time.sleep(SLEEP_TIME)
	def printFingerable(self):
		for idx in range(NBITS):
			if self._finger[idx] != None:
				print(str(self.getIdentifier()) + " :: " + self._finger[idx]._address.__str__() +" : "+ str(self._finger[idx].getIdentifier()) )
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
						print("<><><><><><><><><><><><><><>")
						self._predecessor = None
			time.sleep(SLEEP_TIME)

	def findSuccessor(self, id):
		# check paper for implementation
		self.log("findSuccessor")
		if ( inrange(id,self.getIdentifier(),self.successor().getIdentifier()) and \
			(self.getIdentifier() != self.successor().getIdentifier() ) and \
			(id != self.getIdentifier()) ):

			return self.successor()
		else:
			remote = self.closestPrecedingNode(id)
			if self._address.__hash__() != remote._address.__hash__():
				return remote.findSuccessor(id)
			else:
				return self
	def closestPrecedingNode(self, id):
		# check paper for implementation
		self.log("closestPrecedingNode")
		for idx in reversed(range(NBITS)):
			if self._finger[idx] != None and \
				( inrange(self._finger[idx].getIdentifier(), self.getIdentifier(), id) and \
				(self.getIdentifier() != id) and \
				(self._finger[idx].getIdentifier() != self.getIdentifier()) and \
				(self._finger[idx].getIdentifier() != id) ):

				return self._finger[idx]

		return self
			
	def run(self):

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._socket.bind((self._address.ip, int(self._address.port)))
		self._socket.listen(10)

		while 1:
			self.log("run loop...")
			try:
				conn, addr = self._socket.accept()
			except socket.error:
				print("accept failed")

			request = read_from_socket(conn)


			#print("Request ",request)
			#print(addr[0],addr[1])

			msg = request.split()

			#print("Command ",command)
			command = msg[0]
			key = msg[0]
			value = " ".join(msg[2:])
			# we take the command out
			request = request[len(command) + 1:]

			# defaul : "" = not respond anything
			result = json.dumps("")

			if command == 'INSERT':
				print(request)
				print("PERFORM INSERT")
				result = "INSERTED"

			if command == 'LOOKUP':
				print(request)
				print("PERFORM LOOKUP")
				# if found return value else NOT FOUND
				result = "NOT FOUND"

			if command == 'successor':
				#time.sleep(SLEEP_TIME)
				successor = self.successor()
				result = json.dumps((successor._address.ip, successor._address.port))
			
			if command == 'getPredecessor':
				#print("getPredecessor requset called")
				#time.sleep(SLEEP_TIME)
				if self._predecessor != None:
					predecessor = self.predecessor()
					result = json.dumps((predecessor._address.ip, predecessor._address.port))
			
			if command == 'findSuccessor':
				#print("findSuccessor requset called")
				#time.sleep(SLEEP_TIME)
				successor = self.findSuccessor(int(request))
				result = json.dumps((successor._address.ip, successor._address.port))
			
			if command == 'closestPrecedingNode':
				#print("closestPrecedingNode requset called")
				#time.sleep(SLEEP_TIME)
				closest = self.closestPrecedingNode(int(request))
				result = json.dumps((closest._address.ip, closest._address.port))
			
			if command == 'notify':
				#print("notify requset called")
				#time.sleep(SLEEP_TIME)
				npredecessor = Address(request.split(' ')[0], int(request.split(' ')[1]))
				self.notify(RemoteNode(npredecessor))

			# or it could be a user specified operation
			# for t in self.command_:
			# 	if command == t[0]:
			# 		result = t[1](request)
			#print(type(result))
			#print("result : ",result)
			send_to_socket(conn, result)




		self.log("execution terminated")            


if __name__ == "__main__":
	import sys
	if len(sys.argv) == 2:
		local = Node(Address("127.0.0.1", sys.argv[1]))
	else:
		local = Node(Address("127.0.0.1", sys.argv[1]), Address("127.0.0.1", sys.argv[2]))
	local.start()