'''
@author: Christian
'''
import os, time
import threading, queue
import json
import commandConfig, KeyCtl, keyConfig, CrowdAggregator
import win32ui

class GameControlThread(threading.Thread):

    def __init__(self, inputQ, outputQ):
        super(GameControlThread, self).__init__()
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.stoprequest = threading.Event()
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))

    def run(self):
        aggregator = CrowdAggregator.MajorityVoteCrowdAggregator(10000)
        dueTime = aggregator.getTimeWindow() + self.currentTimeMillisec() 
        while not self.stoprequest.isSet():
            #time is up
            if self.currentTimeMillisec() >= dueTime:
                try:
                    jmessage = self.inputQ.get(True, max(float((dueTime - self.currentTimeMillisec())/1000), 0.001))
                    if json.loads(jmessage)['message'] in commandConfig.commands.keys():
                        aggregator.addVote(json.loads(jmessage)['message'], json.loads(jmessage)['author'])

                except queue.Empty:
                    pass
                result = aggregator.getVoteResult()
                if result is not None:
                    print('vote result is '+ result)
                    self.executeCommandMessage(result)
                else: 
                    print('No participants in this vote')
                    
                dueTime = aggregator.getTimeWindow() + self.currentTimeMillisec()
            else: 
                try:
                    jmessage = self.inputQ.get(True, float((dueTime - self.currentTimeMillisec())/1000))
                    if json.loads(jmessage)['message'] in commandConfig.commands.keys():
                        aggregator.addVote(json.loads(jmessage)['message'], json.loads(jmessage)['author'])
                        print('added  ' + json.loads(jmessage)['message'] + ' by ' + json.loads(jmessage)['author'] + '  to vote' )
                except queue.Empty:
                    continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(GameControlThread, self).join(timeout)

    def executeMessage(self, message):
        sm = json.loads(message)['message']
        if sm in commandConfig.commands.keys():
            KeyCtl.sendImmediateKeystroke(commandConfig.commands[sm])
            
    def executeCommandMessage(self, cm):
        if cm in commandConfig.commands.keys():
            try:
                KeyCtl.sendImmediateKeystroke(commandConfig.commands[cm])
            except win32ui.error:
                print ('Failed to select focus window!')            
            
            
            
            