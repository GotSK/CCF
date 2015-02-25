'''
@author: Christian
'''

import os, time
import threading, queue
import json
import config, KeyCtl, CrowdAggregator
import win32ui

class CommunicationThread(threading.Thread):

    def __init__(self, inputQ, outputQ, clientQ, outputGameCtlQ, outputPlayerMngQ, outputLoggingQ):
        super(CommunicationThread, self).__init__()
        #Arguments 
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.clientQ = clientQ
        self.outputGameCtlQ = outputGameCtlQ
        self.outputPlayerMngQ = outputPlayerMngQ
        self.outputLoggingQ = outputLoggingQ
        
        #Other class variables
        self.stoprequest = threading.Event()
        self.updaterequest = threading.Event()
        self.clientinfolist = []
        self.clients = []
        self.clientById = {}
        self.idByClient = {}
        self.clientByUsername = {}
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))


    def run(self):
        while not self.stoprequest.isSet():
            self.__updateSelf__()
 
            try:
                message = self.inputQ.get(True)
                self.__updateSelf__()                       
                authorId = message[0]
                jmessage = json.loads(message[1])

                if jmessage['type'] in config.toGameCtl:
                    self.outputGameCtlQ.put(jmessage)
                elif jmessage['type'] in config.toPlayerMng:
                    if jmessage['type'] in ['newUser']:
                        self.clientByUsername[jmessage['author']] = self.clientById[authorId]
                    elif jmessage['type'] in ['changeUser']:
                        self.clientByUsername.pop(jmessage['author'], None)
                        self.clientByUsername[jmessage['message']] = self.clientById[authorId]
                    elif jmessage['type'] in ['upvoteMsg']:
                        #replace the original author id with the upvote-target id
                        authorId = self.idByClient[self.clientByUsername[jmessage['message']]]
                    self.outputPlayerMngQ.put([authorId, jmessage])
                    #debug
                    #print("Registered Users: ", self.clientByUsername)
                elif jmessage['type'] in config.toServer:
                    self.outputQ.put(jmessage)                
                elif jmessage['type'] in config.toBroadcast:
                    for client in self.clients:
                        client.write_message(jmessage)
                elif jmessage['type'] in config.toClient:
                    client = self.clientById[authorId]
                    client.write_message(jmessage)
                else:
                    print("ERROR: No such message type provided") 
                                
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(CommunicationThread, self).join(timeout)
    
    def updateClients(self):
        self.updaterequest.set()
    
    def __updateSelf__(self):
        if self.updaterequest.isSet():
                #print('updating....')
                try:
                    self.clientinfolist = self.clientQ.get(False)
                    self.clients = self.clientinfolist[0]
                    self.clientById = self.clientinfolist[1]
                    self.idByClient = self.clientinfolist[2]
                    
                except queue.Empty:
                    print("Tried to access/get from empty client queue.")
                finally:
                    self.updaterequest.clear()
       
            
            
            

            
