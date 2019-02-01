#!/bin/python3
# CODE not tested !!!!!!!!!!!!!!!!!!!!!!
# overall login is prepared : check the remoteNode file also
import sys
import json
import socket
import random
import time
import threading
from remoteNode import RemoteNode
from address import Address

class BackGroundProcess(threading.Thread):
	def __init__(self, obj, method):
		threading.Thread.__init__(self)
		self.obj_ = obj
		self.method_ = method

	def run(self):
		getattr(self.obj_, self.method_)()

class Node:
	def __init__(self):
		self._threads = {}

	def start(self):
		self._threads['someOther1'] = BackGroundProcess(self, 'someOther1')
		self._threads['someOther2'] = BackGroundProcess(self, 'someOther2')
		for key in self._threads:
			self._threads[key].start()

	def join(self):
		for key in self._threads:
			self._threads[key].join()

	def someOther1(self):
		i = 0
		while i < 10:
			print("Hello1")
			i = i  + 1
	def someOther2(self):
		print("Hello2")

if __name__ == "__main__":
	local = Node()
	local.start()
	local.join()
	x = Address("127.0.0.1","1111")
	print(x)