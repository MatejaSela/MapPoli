#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 21:30:15 2018

@author: annietong
"""
import os, json
import sys

path_to_json = '/Users/annietong/Desktop/data/'
path_to_merge = '/Users/annietong/Desktop/merge/'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json') and pos_json.startswith(sys.argv[1])]
out = {}
finalout={}
for i in json_files:
    filepath = path_to_json+i
    with open(os.path.expanduser(filepath),'r') as fp:
        data = fp.read()
        d = json.loads(data)
        for i in d:
            if i not in out and d[i][0]!="not available":
                out[i]=[d[i][0]*d[i][1],d[i][1]]
            elif d[i][0]!="not available":
                if d[i][0]=="0":
                    d[i][0]=0
                out[i][0]+=d[i][0]*d[i][1]
                out[i][1]+=d[i][1]
for i in out:
    if out[i][0] == "":
        finalout[i]="not available"
    else:
        finalout[i]=out[i][0]/out[i][1]

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
        }
finaloutwithallstates={}
for i in states:
    if i in finalout:
        finaloutwithallstates[i]={}
        finaloutwithallstates[i]["fillKey"]=finalout[i]
    else:
        finaloutwithallstates[i]={}
        finaloutwithallstates[i]["fillKey"]="not available"

with open(os.path.expanduser(path_to_merge+sys.argv[1]+"merged.json"),'w') as fp:
    json.dump(finaloutwithallstates,fp)

