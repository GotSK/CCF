'''
@author: Christian
'''
import os, time, random
import threading, queue
import json
import config, KeyCtl, CrowdAggregator
import win32ui

class GameControlThread(threading.Thread):

    def __init__(self, inputQ, outputQ, modeQ, modes, db):
        super(GameControlThread, self).__init__()
        self.db = db
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.modeQ = modeQ
        self.stoprequest = threading.Event()
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))
        self.modeClasses = modes
        self.currentMode = config.votingOptions[1]

    def run(self):
        aggregator = self.modeClasses[self.currentMode](config.modeTimeValues[self.currentMode], self.db)
        dueTime = aggregator.getTimeWindow() + self.currentTimeMillisec()
        #print("initialization complete, entering while", aggregator) 
        while not self.stoprequest.isSet():
            #time is up
            if self.currentTimeMillisec() >= dueTime:
                #print('time is up')
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
                #after result has been determined, check for change in desired game mode
                try:
                    modelist = self.modeQ.get(False)
                    #print('should not happen')
                    if not self.currentMode in modelist:
                        print('chosing randomly from', modelist)
                        self.currentMode = random.choice(modelist)
                        aggregator = self.modeClasses[self.currentMode](config.modeTimeValues[self.currentMode], self.db)
                        self.outputQ.put([-1,json.dumps({'type':'commandResult', 'message':'New game Mode beginning next round: '+ self.currentMode, 'author':'[SYSTEM]'})])
                        #print()
                except queue.Empty:
                    pass
                
                #think about message reduction
                #if ppl participated, broadcast the command vote result + mode vote result, then execute command 
                if result is not None:
                    if self.currentMode != 'Mob':
                        self.outputQ.put([-1,json.dumps({'type':'commandResult', 'message':'vote result is '+ config.commandsToControl[result], 'author':'[SYSTEM]'})])
                    else:
                        self.outputQ.put([-1,json.dumps({'type':'commandResult', 'message':'!noShow', 'author':'[SYSTEM]'})])
                    self.outputQ.put([-1,json.dumps({'type':'modeResult', 'message':self.currentMode, 'author':'[SYSTEM]'})])
                    self.executeCommandMessage(result)
                #else just broadcast mode vote result
                else:
                    self.outputQ.put([-1,json.dumps({'type':'modeResult', 'message':self.currentMode, 'author':'[SYSTEM]'})])
                    #print('No participants in this vote')
                    
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
            
            
            

            
