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
import GameControlThread
from threading import Thread
define("port", default=8888, help="run on the given port", type=int)

#30.02 konzept f�r mouse input

clientId = 0
clients = []
clientById = {}
idByClient = {}

votingOptions =["Mob", "Majority Vote", "Crowd Weighted Vote", "Active", "Leader", "Expertise Weighted Vote", "Proletarian"]
controlInputQueue = queue.Queue()
controlOutputQueue = queue.Queue()
clientUpdateQueue = queue.Queue()

gameControl = GameControlThread.GameControlThread(controlInputQueue, controlOutputQueue, clientUpdateQueue, Database(), votingOptions)
gameControl.start()

def updateClientsGameControl():
    clientUpdateQueue.put(clients)
    gameControl.updateClients()
    
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
    if json.loads(message)['type']=='chatMsg' or json.loads(message)['type'] == 'keystroke':
        jmessage = json.loads(message)
        controlInputQueue.put(jmessage)
    elif json.loads(message)['type']=='voteRequest':
        for vote in votingOptions:
              self.write_message(json.dumps({'type':'voteOption', 'message':vote, 'author':'[SYSTEM]'}))
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
