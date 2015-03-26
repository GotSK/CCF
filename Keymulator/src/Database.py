'''
@author: Christian
'''
import config, Item
class UserAlreadyExistsError(Exception):

    def __init__(self, username):
        self.username = username
        self.msg = 'A user with name ' + username + ' already exists.'
        
    def __str__(self):
        return str(self.msg)
    
    __repr__ = __str__
    
class NoSuchUserError(Exception):

    def __init__(self, username):
        self.username = username
        self.msg = 'A user with name ' + username + ' does not exist.'
        
    def __str__(self):
        return str(self.msg)
    
    __repr__ = __str__
    
class User():
    
    def __init__(self, name, reputation, influence):
        self.name = name
        self.reputation = reputation
        self.influence = influence
        self.items = []
    
    def modifyInfluence(self, mod):
        self.influence += mod
    
    def setInfluence(self, infl):
        self.influence = infl
    
    def modifyReputation(self, mod):
        self.reputation += mod
    
    def setReputation(self, rep):
        self.reputation = rep

    def addItem(self, item):
        self.items.append(item)
        
    def removeItem(self, item):
        self.items.remove(item)

class Database():
    def __init__(self, initRep = 0, initInfl = 0, items = config.availableItems):
        #replace this with an actual DB / table
        self.users = []
        #redundand
        self.userByName = {}
        
        self.availableItems = items
        self.log = []
        self.initialReputation = initRep
        self.initialInfluence = initInfl
        
    def userPurchase(self, username, item):
        self.userByName[username].modifyInfluence(-item.cost)
        self.userByName[username].addItem(item)
    
    def userRefund(self, username, item):
        self.userByName[username].modifyInfluence(item.cost)
        self.userByName[username].removeItem(item)

    def addUser(self, username, initRep = None, initInfl = None):
        if username in self.userByName.keys():
            raise UserAlreadyExistsError(username)
        
        rep, inf = initRep, initInfl
        
        if initRep is None:
            rep = self.initialReputation
        if initInfl is None:
            inf = self.initialInfluence
        
        newUser = User(username, rep, inf)
        self.users.append(newUser)
        self.userByName[username] = newUser
    
    def hasUser(self, username):
        return username in self.userByName.keys()
        
    def getInfluenceByName(self, username):
        return self.__getUserByName__(username).influence
    
    def getReputationByName(self, username):
        return self.__getUserByName__(username).reputation
    
    def modifyUserRep(self, username, mod):
        self.__getUserByName__(username).modifyReputation(mod)
        
    def modifyUserInf(self, username, mod):
        self.__getUserByName__(username).modifyInfluence(mod)
    
    def setUserRep(self, username, val):
        self.__getUserByName__(username).setReputation(val)
        
    def setUserInf(self, username, val):
        self.__getUserByName__(username).setInfluence(val)
    
    def modifyUsersRep(self, usernames, mod):
        for name in usernames:
            self.modifyUserRep(name, mod)
            
    def modifyUsersInf(self, usernames, mod):
        for name in usernames:
            self.modifyUserInf(name, mod)
    
    def setUsersRep(self, usernames, val):
        for name in usernames:
            self.setUserRep(name, val)
            
    def setUsersInf(self, usernames, val):
        for name in usernames:
            self.setUserInf(name, val)
    
    def __getUserByName__(self, username):
        try:
            name = self.userByName[username]
        except KeyError:
            raise NoSuchUserError(username)
        
        return self.userByName[username]
    
        