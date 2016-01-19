'''
Created on 04.04.2015

@author: Christian
'''
import json
import csv
import config

gamificationTypes = ['upvoteMsg', 'purchase', 'agendaSuccess', 'agendaDeny', 'agendaFail']
socialNonGamificationTypes = ['chatMsg']
socialTypes = gamificationTypes + socialNonGamificationTypes
commandTypes = ['keystroke', 'command']
['V4','Maria','Ursula','Peter','Wolfgang']
['V5','Monika','Petra','Michael','Werner']
['V7','Elisabeth', 'Sabine','Klaus','Thomas']
['V6','Renate', 'Helga', 'Manfred', 'Helmut']
['V8','Ingrid','Erika','Gerhard','Andreas']
['V2','Andrea','Gisela','Hans','Josef']
['V1','Claudia', 'Susanne', 'G\u00fcnter', 'Dieter']
['V3','Gabriele', 'Anna', 'Walter', 'Frank']

for filenr in range(1,5):
    logfilename = 'in/jsonLog' + str(filenr) + 'crop.txt'
    outfilename = 'actions' + str(filenr) + '.csv'
    
    content = []
    
    
    jActionsByAuthor = {}
    with open(logfilename, 'r') as f:
        content = f.readlines()
        content = [x.strip('\n') for x in content]
           
    for line in content:
        endtime = int(json.loads(line)['time'])
        author = json.loads(line)['author']
        if not author in jActionsByAuthor.keys():
            jActionsByAuthor[author] = []
        jActionsByAuthor[json.loads(line)['author']].append(line)
    
    aggregations = []
    
    for user in jActionsByAuthor.keys():
        actions = jActionsByAuthor[user]
        aggregation = {'CAPM' : 0, 'SAPM' : 0, 'SAPMG':0, 'GAPM':0 }
        for a in actions:
            if json.loads(a)['type'] in gamificationTypes:
                aggregation['GAPM'] += 1
            if json.loads(a)['type'] in socialNonGamificationTypes:
                if not (json.loads(a)['type'] == 'chatMsg' and json.loads(a)['message'] in config.commands):
                    aggregation['SAPMG'] += 1
            if json.loads(a)['type'] in socialTypes:
                if not (json.loads(a)['type'] == 'chatMsg' and json.loads(a)['message'] in config.commands):
                    aggregation['SAPM'] += 1
                else:
                    aggregation['CAPM'] += 1
            if json.loads(a)['type'] in commandTypes:
                aggregation['CAPM'] += 1
        for k in aggregation.keys():
            aggregation[k] /= 15    
        aggregation['Name'] = user 
        aggregations.append(aggregation)
    
    with open(outfilename, 'w') as f:
        writer = csv.DictWriter(f, aggregations[0].keys())
        writer.writeheader()
        writer.writerows(aggregations)
    
