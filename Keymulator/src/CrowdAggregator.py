'''
Created on 05.01.2015

@author: Christian
'''
import random

class BasicCrowdAggregator():
    def __init__(self, tWindow, db):
        self.db = db
        self.timeWindow = tWindow
        self.usersVoted = {}
        self.ballot = {}
        self.test = lambda x,y: y[x] == y[max(iter(y.keys()), key=(lambda key: y[key]) )]  
          
    def addVote(self, vote, username):
        if not username in self.usersVoted.keys():
            self.usersVoted[username] = vote 
            if vote in self.ballot.keys():
                self.ballot[vote] += 1
            else:
                self.ballot[vote] = 1
                
    def getVoteResult(self):
        if not self.ballot:
            return None
        
        result = None
        for v in self.ballot.keys():
            result= v
            break
        self.reset()
        return result
        
    def getTimeWindow(self):
        return self.timeWindow
    
    def reset(self):
        self.ballot = {}
        self.usersVoted = {}
    
class MajorityVoteCrowdAggregator(BasicCrowdAggregator):
    def getVoteResult(self):
        if not self.ballot:
            return None
        resultlist = [x for x in self.ballot.keys() if self.test(x, self.ballot)]
        result = random.choice(resultlist)
        self.reset()
        return result
        
class CrowdWeightedVoteAggregator(BasicCrowdAggregator):
    #compliant decision yields baseMod * [percentage of winning vote] weight gain 
    #non compliant decision yields baseMod * ([percentage of winning vote] - [percentage of users vote]) weight loss
    
    def __init__(self, tWindow, db, baseMod = 1, maxWeight = 3, minWeight = 0, initialWeight = 1):
        super(CrowdWeightedVoteAggregator, self).__init__(tWindow, db)
        self.maxWeight = maxWeight
        self.baseMod = baseMod
        self.minWeight = minWeight
        self.initialWeight = initialWeight
        self.weightedBallot = {}
        self.weightByUsername = {}
    
    def addVote(self, vote, username):
        if not username in self.weightByUsername.keys():
            self.weightByUsername[username] = self.initialWeight
        if not username in self.usersVoted.keys():
            self.usersVoted[username] = vote 
            
            if vote in self.ballot.keys():
                self.ballot[vote] += 1
            else:
                self.ballot[vote] = 1
                
            if vote in self.weightedBallot.keys():
                self.weightedBallot[vote] += self.weightByUsername[username]
            else:
                self.weightedBallot[vote] = self.weightByUsername[username]
        
             
    
    def getVoteResult(self):
        if not self.ballot:
            return None
        
        resultlist = [x for x in self.weightedBallot.keys() if self.test(x,self.weightedBallot)]
        result = random.choice(resultlist)
        
        percentages = {k: round(float(self.ballot[k]/sum(list(self.ballot.values()))),3) for k in self.ballot.keys()}
        
        self.updateWeights(percentages, resultlist)
        self.reset()
        
        return result
    
    def reset(self):
        super(CrowdWeightedVoteAggregator, self).reset()
        self.weightedBallot = {}
    
    def updateWeights(self, percentages, winners):
        for user in self.weightByUsername.keys():
            if user in self.usersVoted.keys():
                if self.usersVoted[user] in winners:
                    self.weightByUsername[user] = min(self.maxWeight, self.weightByUsername[user] + (self.baseMod * percentages[self.usersVoted[user]]))
                else:
                    self.weightByUsername[user] = max(self.minWeight, self.weightByUsername[user] - (self.baseMod * (percentages[winners[0]] - percentages[self.usersVoted[user]])) )

class ActiveAggregator(BasicCrowdAggregator):
    def __init__(self, tWindow, db, activeUsers = []):
        super(ActiveAggregator,self).__init__(tWindow, db)
        self.activeUsers = activeUsers
        self.leader = None 

    
    def addVote(self, vote, username):
        if username not in self.activeUsers:
            self.activeUsers.append(username)
        BasicCrowdAggregator.addVote(self, vote, username)
    
    def getVoteResult(self):
        result = None
        while(result is None and len(self.activeUsers)>0):
            if self.leader in self.usersVoted.keys():
                result = self.usersVoted[self.leader]
            else:
                self.activeUsers.remove(self.leader)
                self.setNewRandomLeader()
        self.reset()
        return result
                
    def setNewRandomLeader(self):
        if self.activeUsers:
            self.leader = random.choice(self.activeUsers)
        else:
            self.leader = None

class LeaderAggregator(CrowdWeightedVoteAggregator):
    def __init__(self, tWindow, db, baseMod=1, maxWeight=3, minWeight=0, initialWeight=1, activeUsers = []):
        CrowdWeightedVoteAggregator.__init__(self, tWindow, db, baseMod=baseMod, maxWeight=maxWeight, minWeight=minWeight, initialWeight=initialWeight)
        self.activeUsers = activeUsers
        self.leader = None
    def addVote(self, vote, username):
        if username not in self.activeUsers:
            self.activeUsers.append(username)
        CrowdWeightedVoteAggregator.addVote(self, vote, username)
        if self.leader is None:
            self.setNewRandomLeader()
        
    def getVoteResult(self):
        if not self.ballot:
            return None
        
        result = None
        
        while(result is None and len(self.activeUsers)>0):
            if self.leader in self.usersVoted.keys():
                result = self.usersVoted[self.leader]
            else:
                self.activeUsers.remove(self.leader)
                self.setNewRandomLeader()
        
        percentages = {k: round(float(self.ballot[k]/sum(list(self.ballot.values()))),3) for k in self.ballot.keys()}
        resultlist = [x for x in self.ballot.keys() if self.test(x, self.ballot)]
        
        self.updateWeights(percentages, resultlist)
        self.reset()
        
        return result
    
    def setNewRandomLeader(self):
        if self.activeUsers:
            leaderCandidates = [x for x in self.activeUsers if self.test(x, self.weightByUsername)]
            self.leader = random.choice(leaderCandidates)
        else:
            self.leader = None
#TODO: add db synchronization
class ExpertiseWeightedVote(CrowdWeightedVoteAggregator):        
        def __init__(self, tWindow, db, baseMod=1, maxWeight=3, minWeight=0, initialWeight=1, repFactor = 0.1):
            self.repFactor = repFactor
            CrowdWeightedVoteAggregator.__init__(self, tWindow, db, baseMod=baseMod, maxWeight=maxWeight, minWeight=minWeight, initialWeight=initialWeight)
            for username in self.db.userByName.keys():
                self.weightByUsername[username] = min(max(self.minWeight, self.db.getReputationByName(username) * self.repFactor), self.maxWeight)
        def updateWeights(self, percentages, winners):
            for username in self.db.userByName.keys():
                self.weightByUsername[username] = min(max(self.minWeight, self.db.getReputationByName(username) * self.repFactor), self.maxWeight)
                
class ProletarianAggregator(CrowdWeightedVoteAggregator):
        def __init__(self, tWindow, db, baseMod=1, maxWeight=3, minWeight=0, initialWeight=1, repFactor = 0.1, minRep = 1):
            self.repFactor = repFactor
            self.minRep = minRep
            CrowdWeightedVoteAggregator.__init__(self, tWindow, db, baseMod=baseMod, maxWeight=maxWeight, minWeight=minWeight, initialWeight=initialWeight)
            for username in self.db.userByName.keys():
                if self.db.getReputationByName(username) >= self.minRep:
                    self.weightByUsername[username] = min(max(self.minWeight, self.maxWeight - self.db.getReputationByName(username) * self.repFactor), self.maxWeight)
        def updateWeights(self, percentages, winners):
            for username in self.db.userByName.keys():
                self.weightByUsername[username] = min(max(self.minWeight, self.db.getReputationByName(username) * self.repFactor), self.maxWeight)