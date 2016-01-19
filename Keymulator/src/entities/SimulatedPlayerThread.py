'''
@author: Christian
'''
import os, time, random
import threading, queue
import json
import config, KeyCtl, CrowdAggregator
import win32ui

simulateCommandsToControl = [
                     'w',
                     'a',
                     's',
                     'd'                   
                     ]
simulateButtonsToControl = [
                     'i',
                     'j' ]
directions = ["up", "down", "left", "right"]
orders = ["lets go ", "go ", "better ", "vote ", "lol, ", "noo ", "vote for ", "...", "!"]
utterances = ["lol", "haha", "helix is love, helix is life kappa", "when do we get the bike?", "lol, rekt", "impossible", "guys, focus pls", "pls no", "trolls again", "praise helix", "kappa", "mob vote or riot", "rekt"]


class SimulatedPlayerThread(threading.Thread):

    def __init__(self, outputQ, name = None, events = False):
        super(SimulatedPlayerThread, self).__init__()
        self.events = events
        self.outputQ = outputQ
        self.stoprequest = threading.Event()
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))
        self.currentMode = config.votingOptions[1]
        self.name = name
        
        

    def run(self):

        dueTime = random.randrange(1000,10000,2000) + self.currentTimeMillisec()
        #print("initialization complete, entering while", aggregator) 
        if not self.events:
            #self.outputQ.put([0,json.dumps({'type':'newUser', 'message':self.name, 'author':self.name})])
            pass
        
        while not self.stoprequest.isSet():
            if self.currentTimeMillisec() >= dueTime:
                #act again in...
                dueTime = random.randrange(1000,20000,4000) + self.currentTimeMillisec()
                
                if self.events:
                    choice = random.randrange(80)
                    if choice < 50:
                        message = ''
                        if choice < 10:
                            message =  'agendaFail'
                        elif choice > 10 and choice < 30:
                            message = 'agendaDeny'
                        else:
                            message = 'agendaSuccess'
                        self.outputQ.put([0,json.dumps({'type':message, 'message':message, 'author': self.name})])
                    elif choice > 50 and choice < 75:
                        message = 'silverkey'
                        self.outputQ.put([0,json.dumps({'type':'upvoteMsg', 'message':message, 'author': self.name})])

                else:
                    choice = random.randrange(100)
                    if choice < 50:
                        #vote publicly on something
                        message = ''
                        if choice < 10:
                            message =  random.choice(orders)+random.choice(directions)
                        else:
                            message = '!'+random.choice(simulateCommandsToControl)
                        self.outputQ.put([0,json.dumps({'type':'chatMsg', 'message':message, 'author': self.name})])
                    elif choice > 50 and choice < 75:
                        message = '!'+random.choice(simulateButtonsToControl)
                        self.outputQ.put([0,json.dumps({'type':'chatMsg', 'message':message, 'author': self.name})])
                    elif choice >= 90:
                        self.outputQ.put([0,json.dumps({'type':'chatMsg', 'message':random.choice(utterances), 'author': self.name})])



    def join(self, timeout=None):
        self.stoprequest.set()
        super(SimulatedPlayerThread, self).join(timeout)

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
            
            
            

            
