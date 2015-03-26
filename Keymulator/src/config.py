'''
Created on 05.01.2015

@author: Christian
'''
import os
#GAMIFICATION SWITCH
gamification = True

#ITEMS
maxAgendaDuration = 10000
agendaFinishQuota = 0.6

#PLAYER INTERACTION
upvoteModifier = 5
upvotesPerCycle = 1

#GAME MODEs
votingOptions =["Mob", "Majority Vote", "Crowd Weighted Vote", "Active", "Leader", "Expertise Weighted Vote", "Proletarian"]

mobTimeWindow = 0
majorityTimeWindow = 10000
cwvTimeWindow = 10000
actTimeWindow = 5000
leadTimeWindow = 5000
ewvTimeWindow = 10000
prolTimeWindow = 10000
modeTimeValues = {"Mob":mobTimeWindow, "Majority Vote":majorityTimeWindow, "Crowd Weighted Vote":cwvTimeWindow, "Active":actTimeWindow, "Leader":leadTimeWindow, "Expertise Weighted Vote":ewvTimeWindow, "Proletarian":prolTimeWindow}

#GAME CONTROLS
import Item
commands = {
            '!u':'w',
            '!l':'a',
            '!r':'d',
            '!d':'s',
            '87':'w',
            '65':'a',
            '83':'s',
            '68':'d'
            }


commandsToControl = {
                     'w':'Up',
                     'a':'Left',
                     's':'Down',
                     'd':'Right'
                     
                     }

inputMap = {
            'w': 0x57,
            'd':0x44,
            's':0x53,
            'a':0x41
            }

#JSON IDENTIFIERS
"""
        SERVERJS:
        From:
        [all messages]
        To:
        nothing
        
        GAME CONTROL THREAD:
        From:
        result
        To:
        modeVote
        keystroke
        command
        
        PLAYER MANAGEMENT THREAD:
        From:
        userUpdate
        To:
        newUser
        updateRequest
        upvote
        buy
        
        LOGGING THREAD
        
"""


toServer = []
toGameCtl = ['keystroke', 'command', 'chatMsg']
toPlayerMng = ['newUser', 'changeUser', 'updateRequest', 'upvoteMsg', 'purchase', 'agendaSuccess', 'agendaDeny', 'agendaFail']
dataAppended = ['purchase', 'agendaSuccess', 'agendaDeny', 'agendaFail']
toBroadcast = ['commandResult', 'modeResult', 'featureUser', 'updateAll', 'refreshUpvotes', 'setAgenda', 'updateAgenda', 'finishAgenda']
toClient = ['updateUser']

#SHOP
#deprecated! item objects are generated on demand. this should just be a list for the angular app
#availableItems = [Item.Item("Item1",1),Item.Item("Item2",2),Item.Item("Item3",3),Item.Item("Item4",4)]
#-----------------
availableItems = []
itemObjectDict = {'Repay':Item.RepayItem, 'Spotlight':Item.StatusItem, 'Agenda':Item.AgendaItem}



#LOG FILE
DATA_OUTPUT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'jsonLog.txt'))