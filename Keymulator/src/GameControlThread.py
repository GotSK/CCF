'''
@author: Christian
'''
import os, time
import threading, queue
import json
import config, KeyCtl, CrowdAggregator
import win32ui

class GameControlThread(threading.Thread):

    def __init__(self, inputQ, outputQ, clientQ):
        super(GameControlThread, self).__init__()
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.clientQ = clientQ
        self.stoprequest = threading.Event()
        self.updaterequest = threading.Event()
        self.clients = []
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))

    def run(self):
        aggregator = CrowdAggregator.MajorityVoteCrowdAggregator(10000)
        dueTime = aggregator.getTimeWindow() + self.currentTimeMillisec() 
        while not self.stoprequest.isSet():
            if self.updaterequest.isSet():
                try:
                    self.clients = self.clientQ.get(False)
                except queue.Empty:
                    print("Tried to access/get from empty client queue.")
                finally:
                    self.updaterequest.clear()
            #time is up
            if self.currentTimeMillisec() >= dueTime:
                try:
                    jmessage = self.inputQ.get(True, max(float((dueTime - self.currentTimeMillisec())/1000), 0.001))
                    if json.loads(jmessage)['message'] in config.commands.keys():
                        aggregator.addVote(json.loads(jmessage)['message'], json.loads(jmessage)['author'])

                except queue.Empty:
                    pass
                result = aggregator.getVoteResult()
                if result is not None:
                    #print('vote result is '+ result)
                    for client in self.clients:
                        client.write_message(json.dumps({'type':'chatMsg', 'message':'vote result is '+ result, 'author':'[SYSTEM]'}))
                    self.executeCommandMessage(result)
                else: 
                    print('No participants in this vote')
                    
                dueTime = aggregator.getTimeWindow() + self.currentTimeMillisec()
            else: 
                try:
                    jmessage = self.inputQ.get(True, float((dueTime - self.currentTimeMillisec())/1000))
                    if json.loads(jmessage)['message'] in config.commands.keys():
                        aggregator.addVote(json.loads(jmessage)['message'], json.loads(jmessage)['author'])
                        print('added  ' + json.loads(jmessage)['message'] + ' by ' + json.loads(jmessage)['author'] + '  to vote' )
                except queue.Empty:
                    continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(GameControlThread, self).join(timeout)
    
    def updateClients(self):
        self.updaterequest.set()

    def executeMessage(self, message):
        sm = json.loads(message)['message']
        if sm in config.commands.keys():
            KeyCtl.sendImmediateKeystroke(config.commands[sm])
            
    def executeCommandMessage(self, cm):
        if cm in config.commands.keys():
            try:
                KeyCtl.sendImmediateKeystroke(config.commands[cm])
            except win32ui.error:
                print ('Failed to select focus window!')            
            
            
            
            