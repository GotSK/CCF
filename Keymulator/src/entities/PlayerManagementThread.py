'''
@author: Christian
'''

import os, time
import threading, queue
import json
import config
import Item
import random


class PlayerManagementThread(threading.Thread):

    def __init__(self, inputQ, outputQ, db):
        super(PlayerManagementThread, self).__init__()
        #Arguments 
        self.inputQ = inputQ
        self.outputQ = outputQ
        self.db = db
        
        self.agendaBallot = {'agendaSuccess':0, 'agendaFail':0, 'agendaDeny':0}
        self.agendaSet = False
        #Other class variables
        self.stoprequest = threading.Event()
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))


    def run(self):

        while not self.stoprequest.isSet(): 
            try:
                message = self.inputQ.get(True)                   
                authorId = message[0]
                jmessage = message[1]
                dataList = [] # dataList: clientByUsername, idByClient
                if jmessage['type'] in config.dataAppended:
                    dataList = message[2]

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
                        item = config.itemObjectDict[purchase['name']](purchase['name'], purchase['cost'], jmessage['author'], purchase['description'], self)
                        self.db.userPurchase(jmessage['author'], item)
                        
                        item.useItem(dataList)
                        self.sendUserUpdate(authorId, jmessage['author'])
                elif jmessage['type'] in ['agendaSuccess', 'agendaDeny', 'agendaFail']:
                    totalUsers = len(dataList[0].keys())
                    self.agendaBallot[jmessage['type']] += 1
                    agenda= {'success': int((self.agendaBallot['agendaSuccess'] / totalUsers) * 100), 'fail': int((self.agendaBallot['agendaFail'] / totalUsers) * 100), 'deny': int((self.agendaBallot['agendaDeny'] / totalUsers) * 100)}
                    self.sendAgendaUpdate(id, agenda)
                    
                    #check if agenda is resolved
                    #agenda successful
                    if ( (self.getPositiveAgendaVotes() / totalUsers ) > 0.5):
                        self.outputQ.put([id,json.dumps({'type':'finishAgenda', 'message':'Agenda was successful!', 'author':'[SYSTEM]'})])
                        self.resetAgendaBallot()
                    #agenda unsuccessful
                    elif ( (self.getNegativeAgendaVotes() / totalUsers ) > 0.5):
                        self.outputQ.put([id,json.dumps({'type':'finishAgenda', 'message':'Agenda was not successful!', 'author':'[SYSTEM]'})])
                        self.resetAgendaBallot()
                    
                    #agenda undecided, but finished    
                    elif ( self.getTotalAgendaVotes() == totalUsers):
                        self.outputQ.put([id,json.dumps({'type':'finishAgenda', 'message':'Agenda was undecided!', 'author':'[SYSTEM]'})])
                        self.resetAgendaBallot()
                        
                elif jmessage['type'] in ['upvoteMsg']:
                    if self.db.hasUser(jmessage['message']):
                        self.db.modifyUserRep(jmessage['message'], config.upvoteModifier)
                        self.db.modifyUserInf(jmessage['message'], config.upvoteModifier)
                        self.sendUserUpdate(authorId, jmessage['message'])
                else:
                    print("ERROR: No such message type provided") 
                                
            except queue.Empty:
                continue
    def sendUserUpdate(self, id, username):
        self.outputQ.put([id,json.dumps({'type':'updateUser', 'message':'', 'author':'[SYSTEM]', 'reputation':self.db.getReputationByName(username), 'influence':self.db.getInfluenceByName(username)})])
        
    def sendAgendaUpdate(self, id, agenda):
        self.outputQ.put([id,json.dumps({'type':'updateAgenda', 'message':json.dumps(agenda), 'author':'[SYSTEM]'})])
        
    def resetAgendaBallot(self):
        self.agendaBallot = {'agendaSuccess':0, 'agendaFail':0, 'agendaDeny':0}
        self.agendaSet = False
    
    def getTotalAgendaVotes(self):
        total = 0
        for k in self.agendaBallot.keys():
            total += self.agendaBallot[k]
        return total
    def getPositiveAgendaVotes(self):
        return self.agendaBallot['agendaSuccess']
    def getNegativeAgendaVotes(self):
        return self.agendaBallot['agendaFail'] + self.agendaBallot['agendaDeny']
        
    def join(self, timeout=None):
        self.stoprequest.set()
        super(PlayerManagementThread, self).join(timeout)
    


            
            

        