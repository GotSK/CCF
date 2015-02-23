#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: Christian
'''
import KeyCtl

import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
from Database import Database
from tornado.options import define, options, parse_command_line
import config
import queue
import entities.CommunicationThread
import entities.GameControlThread
from threading import Thread
define("port", default=8888, help="run on the given port", type=int)

#30.02 konzept f�r mouse input

clientId = 0
clients = []
clientById = {}
idByClient = {}

votingOptions =["Mob", "Majority Vote", "Crowd Weighted Vote", "Active", "Leader", "Expertise Weighted Vote", "Proletarian"]

#initialize queues
clientUpdateQueue = queue.Queue()
communicationInputQueue = queue.Queue()
communicationOutputQueue = queue.Queue()
pManagementInputQueue = queue.Queue()
pManagementOutputQueue = queue.Queue()
loggingInputQueue = queue.Queue()
loggingOutputQueue = queue.Queue()
controlInputQueue = queue.Queue()
controlOutputQueue = communicationInputQueue

#initialize and start thread entities
communication = entities.CommunicationThread.CommunicationThread(communicationInputQueue, communicationOutputQueue, clientUpdateQueue, controlInputQueue, pManagementInputQueue, loggingInputQueue)
gameControl = entities.GameControlThread.GameControlThread(controlInputQueue, controlOutputQueue, Database(), votingOptions)


gameControl.start()
communication.start()

def updateClientsGameControl():
    clientUpdateQueue.put(clients)
    communication.updateClients()
    
class IndexHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):
      #debug
    self.render(settings['static_path'] + "/web/index.html")
  def check_origin(self, origin):
    return True

class WebSocketChatHandler(tornado.websocket.WebSocketHandler):
    
    
  def open(self, *args):
    global clientId
    print("open", "WebSocketChatHandler")
    clients.append(self)
    clientById[clientId] = self
    idByClient[self] = clientId
    clientId += 1
    updateClientsGameControl()
    self.write_message(json.dumps({'type':'chatMsg', 'message':"Welcome! Please select your Username before you start.", 'author':'[SYSTEM]'}))
    
    """
    Transmitting the voting options on startup does not work at this point apparently
    for vote in votingOptions:
        self.write_message(json.dumps({'type':'voteOption', 'message':vote, 'author':'[SYSTEM]'}))
    """
  def on_message(self, message):        
    print (message)
    #KeyCtl.test()
    print (json.loads(message)['message'])
    print ("Client ID:" + str(idByClient[self]) )
    if json.loads(message)['type']=='voteRequest':
        for vote in votingOptions:
            self.write_message(json.dumps({'type':'voteOption', 'message':vote, 'author':'[SYSTEM]'}))         
    else:
        communicationInputQueue.put(message)
    
    if json.loads(message)['type']=='chatMsg':
        for client in clients:
            client.write_message(message)
          
        
  def on_close(self):
      clients.remove(self)
      updateClientsGameControl()
  def check_origin(self, origin):
    return True

#app = tornado.web.Application([(r'/chat', WebSocketChatHandler), (r'/', IndexHandler)])

settings = {"static_path": os.path.dirname(__file__)}



app = tornado.web.Application([
(r'/', IndexHandler),
(r'/ws', WebSocketChatHandler),
(r"/(.*)", tornado.web.StaticFileHandler, {"path":os.path.dirname(__file__)})
], **settings)

#print(os.path.join(os.path.dirname(__file__), "static"))
      
app.listen(options.port)
tornado.ioloop.IOLoop.instance().start()
