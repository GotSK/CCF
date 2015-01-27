'''
Created on 05.01.2015

@author: Christian
'''
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

availableItems = [Item.Item("Item1",1),Item.Item("Item2",2),Item.Item("Item3",3),Item.Item("Item4",4)]