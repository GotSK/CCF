'''
@author: Christian
'''
import os, time
import threading, queue
import json
import config, KeyCtl, CrowdAggregator
import win32ui

class GameControlThread(threading.Thread):

    def __init__(self, inputQ, outputQ, clientQ, db, modes):
        super(GameControlThread, self).__init__()
        self.db = db
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.clientQ = clientQ
        self.stoprequest = threading.Event()
        self.updaterequest = threading.Event()
        self.clients = []
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))
        self.modes = modes
        self.currentMode = modes[1]

    def run(self):
        aggregator = CrowdAggregator.MajorityVoteCrowdAggregator(3000, self.db)
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
                    #get last minute input
                    jmessage = self.inputQ.get(True, max(float((dueTime - self.currentTimeMillisec())/1000), 0.001))
                    if jmessage['message'] in config.commands.keys():
                        jmessage['message'] = config.commands[jmessage['message']]
                        aggregator.addVote(jmessage['message'], jmessage['author'])

                except queue.Empty:
                    pass
                #handle the result
                result = aggregator.getVoteResult()
                #if ppl participated, boradcast the command vote result + mode vote result, then execute command 
                if result is not None:
                    for client in self.clients:
                        client.write_message(json.dumps({'type':'commandResult', 'message':'vote result is '+ result, 'author':'[SYSTEM]'}))
                        client.write_message(json.dumps({'type':'modeResult', 'message':self.currentMode, 'author':'[SYSTEM]'}))
                    self.executeCommandMessage(result)
                #else just broadcast mode vote result
                else:
                    for client in self.clients:
                        client.write_message(json.dumps({'type':'modeResult', 'message':self.currentMode, 'author':'[SYSTEM]'})) 
                    print('No participants in this vote')
                    
                dueTime = aggregator.getTimeWindow() + self.currentTimeMillisec()
            #there is still time left to vote
            else: 
                try:
                    jmessage = self.inputQ.get(True, float((dueTime - self.currentTimeMillisec())/1000))
                    if jmessage['message'] in config.commands.keys():
                        jmessage['message'] = config.commands[jmessage['message']]
                        aggregator.addVote(jmessage['message'], jmessage['author'])
                        print('added  ' + jmessage['message'] + ' by ' + jmessage['author'] + '  to vote' )
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
        if cm in config.inputMap.keys():
            try:
                KeyCtl.sendImmediateKeystroke(cm)
            except win32ui.error:
                print ('Failed to select focus window!')            
            
            
            

            
