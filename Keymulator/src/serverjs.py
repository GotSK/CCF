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
import entities.PlayerManagementThread
import entities.LoggingThread
import entities.SimulatedPlayerThread
import CrowdAggregator
from threading import Thread
from CrowdAggregator import MajorityVoteCrowdAggregator,\
    CrowdWeightedVoteAggregator, ActiveAggregator, LeaderAggregator,\
    ExpertiseWeightedVote, ProletarianAggregator
define("port", default=8888, help="run on the given port", type=int)

clientId = 0
clients = []
clientById = {}
idByClient = {}

modeClasses = {"Mob":MajorityVoteCrowdAggregator, "Majority Vote":MajorityVoteCrowdAggregator, "Crowd Weighted Vote":CrowdWeightedVoteAggregator, "Active":ActiveAggregator, "Leader":LeaderAggregator, "Expertise Weighted Vote":ExpertiseWeightedVote, "Proletarian":ProletarianAggregator}

#initialize queues
clientUpdateQueue = queue.Queue()
communicationInputQueue = queue.Queue()
communicationOutputQueue = queue.Queue()

pManagementInputQueue = queue.Queue()
pManagementOutputQueue = communicationInputQueue

loggingInputQueue = queue.Queue()
loggingOutputQueue = communicationInputQueue

modeVotingQueue = queue.Queue()
controlInputQueue = queue.Queue()
controlOutputQueue = communicationInputQueue

simulationQueues = []

#initialize database

#modified start values for rep and influence for testing purposes
db = Database(90, 9)

#initialize and start thread entities
simulatedPlayers = []
simCount = 0
maxSimCount = 10
for name in config.randomNames:
    if simCount >= maxSimCount:
        break
    tqueue = queue.Queue()
    simulatedPlayers.append(entities.SimulatedPlayerThread.SimulatedPlayerThread(communicationInputQueue, name, False, tqueue))
    simulationQueues.append(tqueue)
    simCount +=1
if maxSimCount > 0 :
    tqueue = queue.Queue()
    simulationQueues.append(tqueue)
    simulatedPlayers.append(entities.SimulatedPlayerThread.SimulatedPlayerThread(communicationInputQueue, 'eventManager', True, tqueue))
    
communication = entities.CommunicationThread.CommunicationThread(communicationInputQueue, communicationOutputQueue, clientUpdateQueue, controlInputQueue, pManagementInputQueue, loggingInputQueue, modeVotingQueue, simulationQueues)
gameControl = entities.GameControlThread.GameControlThread(controlInputQueue, controlOutputQueue, modeVotingQueue, modeClasses, db)
playerManagement = entities.PlayerManagementThread.PlayerManagementThread(pManagementInputQueue, pManagementOutputQueue, db)
logging = entities.LoggingThread.LoggingThread(loggingInputQueue, loggingOutputQueue)


    
gameControl.start()
communication.start()
playerManagement.start()
logging.start()

for simulator in simulatedPlayers:
    simulator.start()

def updateClientsGameControl():
    clientUpdateQueue.put([clients, clientById, idByClient])
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
    self.write_message(json.dumps({'type':'chatMsg', 'message':"The following chat commands are available:", 'author':'[SYSTEM]'}))
    for c in config.commands.keys():
        if '!' in c:
            print("writing happens")
            self.write_message(json.dumps({'type':'chatMsg', 'message':c + ' --> ' + config.commandsToControl[config.commands[c]], 'author':'[SYSTEM]'})) 
    """
    """
    Transmitting the voting options on startup does not work at this point apparently
    for vote in votingOptions:
        self.write_message(json.dumps({'type':'voteOption', 'message':vote, 'author':'[SYSTEM]'}))
    """
  def on_message(self, message):
    #KeyCtl.test()
    #print (json.loads(message)['message'])
    #print ("Client ID:" + str(idByClient[self]) )
    if json.loads(message)['type']=='voteRequest':
        #print ('Not for communication thread:', message)
        self.write_message(json.dumps({'type':'refreshUpvotes', 'message':config.upvotesPerCycle, 'author':'[SYSTEM]'}))
        for vote in config.votingOptions:
            self.write_message(json.dumps({'type':'voteOption', 'message':vote, 'author':'[SYSTEM]'}))
    elif json.loads(message)['type']=='gamificationRequest':
        if config.gamification:
            self.write_message(json.dumps({'type':'enableGamification', 'message':'', 'author':'[SYSTEM]'}))
    else:
        #print ('Communication thread:', message)
        communicationInputQueue.put([idByClient[self],message])
    
    """
    if json.loads(message)['type']=='chatMsg':
        for client in clients:
            client.write_message(message)
    """      
        
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
