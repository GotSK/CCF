'''
@author: Christian
'''
import os, time
import threading, queue
import json
import config, KeyCtl, CrowdAggregator


class DataControl():
    def __init__(self):
        self.clients = []
        self.usernameByClient = {}
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))