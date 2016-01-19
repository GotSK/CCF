'''

@author: Christian
'''
import random
import json
class Item():
    def __init__(self, name, cost,  ownerName, description, pmt):
        self.name = name
        self.cost = cost
        self.pmt = pmt
        self.description = description
        self.ownerName = ownerName
        
    def useItem(self, dataList):
        pass
        
class RepayItem(Item):
       
    def useItem(self, dataList):
        users = list(dataList[0].keys())
        
        users.remove(self.ownerName)
        if len(users) > 0:
            allGain  = self.cost//len(users)
            extraGainUsers = random.sample(users, self.cost%len(users))
            # dataList: clientByUsername, idByClient
            for user in users:
                gain = allGain
                if user in extraGainUsers:
                    gain += 1
                if self.pmt.db.hasUser(user):
                    self.pmt.db.modifyUserRep(user, gain)
                    self.pmt.db.modifyUserInf(user, gain)
                    self.pmt.sendUserUpdate(dataList[1][dataList[0][user]], user)

class StatusItem(Item):
    
    def useItem(self, dataList):
        if self.ownerName in self.pmt.spotlightDict.keys():
            self.pmt.spotlightDict[self.ownerName] += 3

        else:
            alert = {'type':'danger', 'msg':'Something went wrong'}
            self.pmt.outputQ.put([dataList[1][dataList[0][self.ownerName]], json.dumps({ 'message':json.dumps(alert), 'author': '[SYSTEM]', 'type':"userAlert"})] )
            self.pmt.db.userRefund(self.ownerName, self)
       #self.pmt.outputQ.put([dataList[1][dataList[0][self.ownerName]], json.dumps({ 'message':self.ownerName, 'author': '[SYSTEM]', 'type':"featureUser"})] )


class AgendaItem(Item):
    
    def useItem(self, dataList):
        if not self.pmt.agendaSet:
            self.pmt.agendaSet = True
            self.pmt.agendaText = self.description
            agenda = {'success':0, 'fail':0, 'deny':0, 'text':self.description}
            self.pmt.outputQ.put([dataList[1][dataList[0][self.ownerName]], json.dumps({ 'message':json.dumps(agenda), 'author': '[SYSTEM]', 'type':"setAgenda"})] )
        else:
            alert = {'type':'danger', 'msg':'The current agenda is not finished yet!'}
            self.pmt.outputQ.put([dataList[1][dataList[0][self.ownerName]], json.dumps({ 'message':json.dumps(alert), 'author': '[SYSTEM]', 'type':"userAlert"})] )
            self.pmt.db.userRefund(self.ownerName, self)