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
        self.clients = []
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))


    def run(self):
        """
        SERVERJS:
        From:
        [all messages]
        To:
        nothing
        
        GAME CONTROL THREAD:
        From:
        result
        To:
        modeVote
        keystroke
        command
        
        PLAYER MANAGEMENT THREAD:
        From:
        update
        To:
        newUser
        updateRequest
        upvote
        buy
        
        LOGGING THREAD
        
        """
        while not self.stoprequest.isSet():
            if self.updaterequest.isSet():
                try:
                    self.clients = self.clientQ.get(False)
                except queue.Empty:
                    print("Tried to access/get from empty client queue.")
                finally:
                    self.updaterequest.clear()
 
            try:
                message = self.inputQ.get(True)
                jmessage = json.loads(message)

                if jmessage['type'] in config.toGameCtl:
                    self.outputGameCtlQ.put(jmessage)
                elif jmessage['type'] in config.toPlayerMng:
                    self.outputPlayerMngQ.put(jmessage)
                elif jmessage['type'] in config.toServer:
                    self.outputQ.put(jmessage)                
                elif jmessage['type'] in config.toBroadcast:
                    for client in self.clients:
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
       
            
            
            

            
