'''
Created on 03.04.2015

@author: Christian
'''
import json

logfilename = 'in/jsonLog4.txt'
logOut = 'in/jsonLog4crop.txt'
content = []

with open(logfilename, 'r') as f:
    content = f.readlines()
    content = [x.strip('\n') for x in content]
    
starttime = int(json.loads(content[0])['time'])
endtime = 0
with open(logOut,'w') as nf:
    for line in content:
        if (int(json.loads(line)['time']) - starttime) <= 15*60*1000:
            nf.write(line+'\n')
    
