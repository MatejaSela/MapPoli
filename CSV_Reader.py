import csv
from collections import defaultdict
import math
    
# open the file in universal line ending mode
states = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}
with open('C:/Users/Mateja/Desktop/701 Project/obamacare.csv', encoding="utf-8") as infile:
  # read the file as a dictionary for each row ({header : value})
  infile.readline()
  reader = csv.DictReader(infile)
  next(reader, None)
  data = {}
  for row in reader:
    for header, value in row.items():
        data.setdefault(header, list()).append(value)

# map the state to each vote, each YES will give a +1,
# each NO will give a -1 "Not Voting" will be ignored
voters_per_state = {}
#initiate the dictionary to all empty values
for state in states:
    voters_per_state[state] = {}
    # get the votes number for each party to see the overall voting pattern
    voters_per_state[state]['RY'] = 0 #republican yes
    voters_per_state[state]['RN'] = 0 #republican no
    voters_per_state[state]['DY'] = 0 #democrat yes
    voters_per_state[state]['DN'] = 0 #democrat no
    
    voters_per_state[state]['fillKey'] = []
    
all_votes = data['vote']
all_states = data['state']
all_parties = data['party']
i = 0
# loop through the vote/state array and add each to dictionary
while(i<len(all_votes)):
    if(all_votes[i] == 'Not Voting'):
        i+=1
        continue

    #append to the list if the 
    if(all_votes[i] == 'Aye'):
        voters_per_state[all_states[i]]["fillKey"].append(1)
    else:
        voters_per_state[all_states[i]]["fillKey"].append(0)
            
    if(all_parties[i] == "Republican" and all_votes[i] == 'No'):
        voters_per_state[all_states[i]]["RN"] +=1

    elif(all_parties[i] == "Democrat" and all_votes[i] == 'No'):
        voters_per_state[all_states[i]]["DN"] +=1

    elif(all_parties[i] == "Republican" and all_votes[i] == 'Aye'):
        voters_per_state[all_states[i]]["RY"] +=1

    elif(all_parties[i] == "Democrat" and all_votes[i] == 'Aye'):
        voters_per_state[all_states[i]]["DY"] +=1

    i+=1
    
# convert the map into JSON!
import json
import copy

#import sentimentDict
with open('C:/Users/Mateja/Desktop/701 Project/obamacaretwitter.json') as json_data:
    twitter_dict = json.load(json_data)

combined_data = copy.deepcopy(voters_per_state)

# find the average between all the states 
for state in voters_per_state.keys():
    #if the state has voter information, calculate the discrepancy score
    if (voters_per_state[state] != {'RY': 0, 'RN': 0, 'DY': 0, 'DN': 0, 'fillKey': 0.0}
        and twitter_dict[state] != "not available" and voters_per_state[state] != {'RY': 0, 'RN': 0, 'DY': 0, 'DN': 0, 'fillKey': [0]}):
        #calculate the average among all votes
        sum_of_votes = sum(voters_per_state[state]["fillKey"])
        len_of_votes = len(voters_per_state[state]["fillKey"])

        congress_sentiment = sum_of_votes / len_of_votes
        voters_per_state[state]["fillKey"] = congress_sentiment

        # calculate the percentage of dems who voted yes vs. republicans per state
        len_of_parties = voters_per_state[state]["DN"] + voters_per_state[state]["DY"] + voters_per_state[state]["RN"] + voters_per_state[state]["RY"]
        #calculate the percentage of democrats and republicans who voted how in each state
        
        #if there is no twitter data available we have to mark everything as unavailable
        if(twitter_dict[state]["fillKey"] != "not available"):
            combined_data[state]["fillKey"] = abs(twitter_dict[state]["fillKey"] - congress_sentiment)
        else:
            combined_data[state]["fillKey"] = "not available"

        
        if(len_of_parties == 0):
            continue
        combined_data[state]["DY"] = voters_per_state[state]['DY'] / len_of_parties
        combined_data[state]["RY"] = voters_per_state[state]['RY'] / len_of_parties
        combined_data[state]["RN"] = voters_per_state[state]['RN'] / len_of_parties
        combined_data[state]["DN"] = voters_per_state[state]['DN'] / len_of_parties
  
        #if there is no data in the preloaded or streamed set, we make all
        # the data unavailable

        #if(stream_dict[state] != "not available"):
        #    stream_data[state]["fillKey"] = abs(stream_dict[state] - congress_sentiment)
    else:
        #if the state has no information, label as not available
        print(state)
        combined_data[state]["fillKey"] = "not available"

        if(voters_per_state[state] == {'RY': 0, 'RN': 0, 'DY': 0, 'DN': 0, 'fillKey': 0.0} or voters_per_state[state] == {'RY': 0, 'RN': 0, 'DY': 0, 'DN': 0, 'fillKey': [0]}):
            voters_per_state[state]['fillKey'] = "not available"
       
#dump congress-only data to be toggled
with open('C:/Users/Mateja/Desktop/701 Project/obamacarecongress.json', 'w') as outfile:
    json.dump(voters_per_state, outfile)

#export all files in the appropriate format
with open('C:/Users/Mateja/Desktop/701 Project/obamacareboth.json', 'w') as outfile:
    json.dump(combined_data, outfile)
    
#with open('C:/Users/Mateja/Desktop/701 Project/healthcare.json', 'w') as outfile:
 #   json.dump(stream_data, outfile)
    
    
    

