'''
Created on 03.04.2015

@author: Christian
'''
import json

logfilename = 'in/jsonLog4crop.txt'
logOut = 'in/jsonLog2crop.txt'
content = []

with open(logfilename, 'r') as f:
    content = f.readlines()
    content = [x.strip('\n') for x in content]
    
starttime = int(json.loads(content[0])['time'])
endtime = 0    
for line in content:
    endtime = int(json.loads(line)['time'])
    print (line)
    
print(starttime)
print(endtime)
print((starttime - endtime)/1000/60)