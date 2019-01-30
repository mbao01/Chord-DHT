#!/bin/python3
import sys
import json
import socket
import random
import time
from threading import Thread, Lock
from config import NBITS,SIZE

class Node:
    def __init__(self, localAdress, RemoteAddress = None):
        self.address = localAdress
        self.threads = {}
        self.finger  = {}   
        for idx in range(BITS):
            self.finger[0] = None
        self.join(RemoteAddress)
    
    def join(self,RemoteAddress = None):
        if RemoteAddress:
            
