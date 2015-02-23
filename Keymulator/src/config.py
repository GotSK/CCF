'''
Created on 05.01.2015

@author: Christian
'''

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
        update
        To:
        newUser
        updateRequest
        upvote
        buy
        
        LOGGING THREAD
        
"""

fromGameCtl = ['modeResult', 'commandResult' ]
fromPlayerMng = ['update']

toServer = []
toGameCtl = ['modeVote', 'keystroke', 'command', 'chatMsg']
toPlayerMng = ['newUser', 'updateRequest', 'upvote', 'buy']
toBroadcast = ['commandResult', 'modeResult', 'featureUser']

#SHOP
availableItems = [Item.Item("Item1",1),Item.Item("Item2",2),Item.Item("Item3",3),Item.Item("Item4",4)]