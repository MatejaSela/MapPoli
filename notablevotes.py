import csv
import pandas as pd
import json
import sys
import os
path_to_merge = '/Users/annietong/Desktop/merge/'
data = pd.read_csv("https://www.govtrack.us/congress/votes/111-2010/h165/export/csv",header=1)
newjson = json.loads(data.to_json(orient='index'))
outjson = {}
for i in newjson:
    d = newjson[i]
    outjson[d['person']]={'state':d['state'],'vote':d['vote'],'name':d['name'],'party':d['party']}
reverse={"repn":[],"repy":[],"demn":[],"demy":[]}

for i in outjson:
    if outjson[i]['party']=='Republican' and outjson[i]['vote']=='Nay':
        reverse["repn"].append(i)
    elif outjson[i]['party']=='Republican' and outjson[i]['vote']=='Yea':
        reverse["repy"].append(i)
    elif outjson[i]['party']=='Democrat' and outjson[i]['vote']=='Nay':
        reverse["demn"].append(i)
    elif outjson[i]['party']=='Democrat' and outjson[i]['vote']=='Yea':
        reverse["demy"].append(i)

notablevotes = []
limit = 10
if len(reverse['repy']) < limit:
    notablevotes.extend(reverse["repy"])
if len(reverse['repn']) < limit:
    notablevotes.extend(reverse["repn"])
if len(reverse['demy']) < limit:
    notablevotes.extend(reverse["demy"])
if len(reverse['demn']) < limit:
    notablevotes.extend(reverse["demn"])
finalout={}
for i in notablevotes:
    finalout[i]=outjson[i]


with open(os.path.expanduser(path_to_merge+sys.argv[1]+"notable.json"),'w') as fp:
    json.dump(finalout,fp)
