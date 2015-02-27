'''

@author: Christian
'''
import random
import json
class Item():
    def __init__(self, name, cost,  ownerName, pmt):
        self.name = name
        self.cost = cost
        self.pmt = pmt
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
        self.pmt.outputQ.put([dataList[1][dataList[0][self.ownerName]], json.dumps({ 'message':self.ownerName, 'author': '[SYSTEM]', 'type':"featureUser"})] )