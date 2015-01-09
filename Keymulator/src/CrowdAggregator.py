'''
Created on 05.01.2015

@author: Christian
'''

class BasicCrowdAggregator():
    def __init__(self, tWindow):
        self.timeWindow = tWindow
        self.usersVoted = []
        self.ballot = {}  
          
    def addVote(self, vote, username):
        if not username in self.usersVoted:
            self.usersVoted.append(username) 
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
        self.ballot = {}
        self.usersVoted = []
        return result
        
    def getTimeWindow(self):
        return self.timeWindow
    
class MajorityVoteCrowdAggregator(BasicCrowdAggregator):      
    def getVoteResult(self):
        if not self.ballot:
            return None
        result = max(iter(self.ballot.keys()), key=(lambda key: self.ballot[key]))
        self.ballot = {}
        self.usersVoted = []
        return result
        

    
    
        
    