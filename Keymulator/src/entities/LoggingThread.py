'''
@author: Christian
'''
import os, time
import threading, queue
import json
import config
import Item

class LoggingThread(threading.Thread):

    def __init__(self, inputQ, outputQ):
        super(LoggingThread, self).__init__()
        #Arguments 
        self.inputQ = inputQ
        self.outputQ = outputQ
        
        #Other class variables
        self.stoprequest = threading.Event()
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))
        self.logFile = config.DATA_OUTPUT
        
        with open(self.logFile, 'w') as f:
            f.write(json.dumps({'type':'initializeLog', 'message':'Log initialized', 'author':'[SYSTEM]', 'time':str(self.currentTimeMillisec())}) + '\n')


    def run(self):
        lastMode = ''
        while not self.stoprequest.isSet(): 
            try:
                message = self.inputQ.get(True)                   
                if json.loads(message[1])['type'] == 'modeResult':
                    if json.loads(message[1])['message'] != lastMode:
                        lastMode = json.loads(message[1])['message']
                        self.logJsonToFile(message)
                else:
                    self.logJsonToFile(message)
                                
            except queue.Empty:
                continue
            
    def logJsonToFile(self, message):
        logmsg = json.loads(message[1])
        print(logmsg)
        logmsg['time'] = str(self.currentTimeMillisec())
        logmsg['authorId'] = str(message[0])
        with open(self.logFile, 'a') as f:
            f.write(json.dumps(logmsg)+'\n')
            
        
        
    def join(self, timeout=None):
        self.stoprequest.set()
        super(LoggingThread, self).join(timeout)
    
