'''
@author: Christian
'''

import os, time
import threading, queue
import json
import config
import Item

class PlayerManagementThread(threading.Thread):

    def __init__(self, inputQ, outputQ, db):
        super(PlayerManagementThread, self).__init__()
        #Arguments 
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.db = db
        
        #Other class variables
        self.stoprequest = threading.Event()
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))


    def run(self):

        while not self.stoprequest.isSet(): 
            try:
                message = self.inputQ.get(True)                   
                authorId = message[0]
                jmessage = message[1]

                if jmessage['type'] in ['updateRequest']:
                    self.sendUserUpdate(authorId, jmessage['author'])
                elif jmessage['type'] in ['newUser']:
                    if not self.db.hasUser(jmessage['author']):
                        self.db.addUser(jmessage['author'])
                    self.sendUserUpdate(authorId, jmessage['author'])
                elif jmessage['type'] in ['changeUser']:
                    if not self.db.hasUser(jmessage['message']):
                        self.db.addUser(jmessage['message'])     
                    self.sendUserUpdate(authorId, jmessage['message'])                    
                elif jmessage['type'] in ['purchase']:
                    if self.db.hasUser(jmessage['author']):
                        purchase =  json.loads(jmessage['message'])
                        self.db.userPurchase(jmessage['author'], Item.Item(purchase['name'], purchase['cost']))
                        self.sendUserUpdate(authorId, jmessage['author'])
                elif jmessage['type'] in ['upvoteMsg']:
                    if self.db.hasUser(jmessage['author']):
                        self.db.modifyUserRep(jmessage['message'], config.upvoteModifier)
                        self.db.modifyUserInf(jmessage['message'], config.upvoteModifier)
                        self.sendUserUpdate(authorId, jmessage['message'])
                else:
                    print("ERROR: No such message type provided") 
                                
            except queue.Empty:
                continue
    def sendUserUpdate(self, id, username):
        self.outputQ.put([id,json.dumps({'type':'updateUser', 'message':'', 'author':'[SYSTEM]', 'reputation':self.db.getReputationByName(username), 'influence':self.db.getInfluenceByName(username)})])
        
    def join(self, timeout=None):
        self.stoprequest.set()
        super(PlayerManagementThread, self).join(timeout)
    

       
            
            
            

            
