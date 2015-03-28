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
        
        #Control variables
        self.agendaBallot = {'agendaSuccess':0, 'agendaFail':0, 'agendaDeny':0}
        self.agendaSet = False
        self.agendaText = ''
        self.spotlightDict = {}
        
        #Other class variables
        self.stoprequest = threading.Event()
        self.currentTimeMillisec = lambda: int(round(time.time() * 1000))


    def run(self):
        upvoteDueTime = self.currentTimeMillisec() + config.upvoteCycleDuration
        while not self.stoprequest.isSet(): 
            try:
                message = self.inputQ.get(True, max(float((upvoteDueTime - self.currentTimeMillisec())/1000), 0.001))       
                if self.currentTimeMillisec() >= upvoteDueTime:
                    self.outputQ.put([-1,json.dumps({'type':'refreshUpvotes', 'message':config.upvotesPerCycle, 'author':'[SYSTEM]'})])
                    upvoteDueTime = self.currentTimeMillisec() + config.upvoteCycleDuration
                    self.featureUser()
                              
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
                    if not jmessage['author'] in self.spotlightDict.keys():
                        self.spotlightDict[jmessage['author']] = 1
                    self.sendUserUpdate(authorId, jmessage['author'])
                    if self.agendaSet:
                        self.sendAgendaUpdate(authorId, len(dataList[0].keys()))
                elif jmessage['type'] in ['changeUser']:
                    if not self.db.hasUser(jmessage['message']):
                        self.db.addUser(jmessage['message'])
                    
                    if jmessage['author'] in self.spotlightDict.keys():
                        self.spotlightDict[jmessage['message']] = self.spotlightDict[jmessage['author']]
                        try:
                            del self.spotlightDict[jmessage['author']]
                        except KeyError:
                            pass
                         
                    self.sendUserUpdate(authorId, jmessage['message'])                    
                elif jmessage['type'] in ['purchase']:
                    if self.db.hasUser(jmessage['author']):
                        purchase =  json.loads(jmessage['message'])
                        item = config.itemObjectDict[purchase['name']](purchase['name'], purchase['cost'], jmessage['author'], purchase['description'], self)
                        self.db.userPurchase(jmessage['author'], item)
                        
                        item.useItem(dataList)
                        self.sendUserUpdate(authorId, jmessage['author'])
                elif jmessage['type'] in ['agendaSuccess', 'agendaDeny', 'agendaFail']:
                    

                    if self.db.hasUser(jmessage['author']):
                        self.db.modifyUserRep(jmessage['author'], config.agendaParticipationModifier)
                        self.db.modifyUserInf(jmessage['author'], config.agendaParticipationModifier)
                        self.sendUserUpdate(authorId, jmessage['author'])
                        
                    totalUsers = len(dataList[0].keys())
                    self.agendaBallot[jmessage['type']] += 1
                    self.sendAgendaUpdate(authorId, totalUsers)
                    
                    #check if agenda is resolved
                    #agenda successful
                    if ( (self.getPositiveAgendaVotes() / totalUsers ) > 0.5):
                        alert = {'type':'success', 'msg':'Agenda was successful!'}
                        self.outputQ.put([id,json.dumps({'type':'finishAgenda', 'message':json.dumps(alert), 'author':'[SYSTEM]'})])
                        self.resetAgendaBallot()
                    #agenda unsuccessful
                    elif ( (self.getNegativeAgendaVotes() / totalUsers ) > 0.5):
                        alert = {'type':'danger', 'msg':'Agenda was not successful!'}
                        self.outputQ.put([id,json.dumps({'type':'finishAgenda', 'message':json.dumps(alert), 'author':'[SYSTEM]'})])
                        self.resetAgendaBallot()
                    
                    #agenda undecided, but finished    
                    elif ( self.getTotalAgendaVotes() == totalUsers):
                        alert = {'type':'warning', 'msg':'Agenda was undecided!'}
                        self.outputQ.put([id,json.dumps({'type':'finishAgenda', 'message':json.dumps(alert), 'author':'[SYSTEM]'})])
                        self.resetAgendaBallot()
                        
                elif jmessage['type'] in ['upvoteMsg']:
                    if self.db.hasUser(jmessage['message']):
                        self.db.modifyUserRep(jmessage['message'], config.upvoteModifier)
                        self.db.modifyUserInf(jmessage['message'], config.upvoteModifier)
                        self.sendUserUpdate(authorId, jmessage['message'])
                else:
                    print("ERROR: No such message type provided") 
                                
            except queue.Empty:
                if self.currentTimeMillisec() >= upvoteDueTime:
                    self.outputQ.put([-1,json.dumps({'type':'refreshUpvotes', 'message':config.upvotesPerCycle, 'author':'[SYSTEM]'})])
                    upvoteDueTime = self.currentTimeMillisec() + config.upvoteCycleDuration
                    self.featureUser()
                continue
    def sendUserUpdate(self, id, username):
        self.outputQ.put([id,json.dumps({'type':'updateUser', 'message':'', 'author':'[SYSTEM]', 'reputation':self.db.getReputationByName(username), 'influence':self.db.getInfluenceByName(username)})])
        
    def sendAgendaUpdate(self, id, totalUsers):
        agenda= {'success': int((self.agendaBallot['agendaSuccess'] / totalUsers) * 100), 'fail': int((self.agendaBallot['agendaFail'] / totalUsers) * 100), 'deny': int((self.agendaBallot['agendaDeny'] / totalUsers) * 100), 'text':self.agendaText}
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
    
    def featureUser(self):
        randlist = []
        for user in self.spotlightDict.keys():
            for t in range(self.spotlightDict[user]):
                randlist.append(user)
        if len(randlist) > 0:
            spot = random.choice(randlist)
            self.outputQ.put([-1,json.dumps({'type':'featureUser', 'message':spot, 'author':'[SYSTEM]'})])
        
    def join(self, timeout=None):
        self.stoprequest.set()
        super(PlayerManagementThread, self).join(timeout)
    


            
            

        