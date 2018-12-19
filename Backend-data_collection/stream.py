#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 16:18:58 2018

@author: annietong
"""

import tweepy
import re
import os
import json
import sys
import datetime

from nltk.sentiment.vader import SentimentIntensityAnalyzer
#
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from google.cloud.language_v1 import types
from google.oauth2 import service_account
import six


def get_vadar_sentiment(texts):
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(texts)
    sentiment = ss['compound']
    print(texts, sentiment)
    return sentiment
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        
        sid = SentimentIntensityAnalyzer()
        text = ""
        try:
            if status.retweeted_status:
                text = status.retweeted_status._json['extended_tweet']['full_text']
            else:
                text = status._json['extended_tweet']['full_text']
        except:
#            print("incomplete     "+status._json['text'])
            text = status._json['text']
        t = re.sub('(?<=^|(?<=[^a-zA-Z0-9-_.]))@([A-Za-z0-9]+)','',text)
        t = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',t)
        t = re.sub('[\s]+',' ',t)
        t = re.sub('RT : ','', t)
        
        def entity_sentiment_text(text,key):
            d = {}
            """Detects entity sentiment."""
            credentials = service_account.Credentials. from_service_account_file('nlptest-417953ad79a8.json')
        
            client = language_v1.LanguageServiceClient(credentials=credentials)
        
            if isinstance(text, six.binary_type):
                text = text.decode('utf-8')
            
            document = types.Document(
                content=text.encode('utf-8'),
                type=enums.Document.Type.PLAIN_TEXT)
            result = client.analyze_entity_sentiment(document=document)
            for entity in result.entities:
                d[str(entity.name)]=entity.sentiment.score
            if key in d:
                return(d[key])
            else:
                annotations = client.analyze_sentiment(document=document)
                return(annotations.document_sentiment.score)
                
        if status.user.location != None:
            for state in states:
                if state in status.user.location or states[state] in status.user.location:
                    print(status.user.location)
                    print(t)
                    ss = entity_sentiment_text(t,keyword)
                    print("google: "+str(ss))
                    print("vadar: "+str(get_vadar_sentiment(t)))
                    sentiment = ss
                    tmp = table[state]
                    tmp.append(sentiment)
                    table[state]=tmp
        count = 0
        tweetcount =0
        for state in table:
            if len(table[state])>0:
                count+=1
                tweetcount+=len(table[state])
        print("===="+str(count))
        print("===="+str(tweetcount))
        if count>50 and tweetcount>2000:
            out = {}
            for i in states:
                out[i] = "not available"
            for state in table:
                if len(table[state])>0:
                    poscount = 0
                    negcount = 0
                    for tw in table[state]:
                        if tw>0:
                            poscount+=1
                        elif tw<0:
                            negcount+=1
                    pos = poscount/len(table[state])
                    neg = negcount/len(table[state])
                if pos>0 or neg>0:
                    posper = pos/(pos+neg)
                else:
                    posper = 0
                out[state]=posper
            
            currentDT = datetime.datetime.now()
            
            filepath = "~/Desktop/tweetstream"+keyword+currentDT.strftime("%Y-%m-%d-%H-%M-%S")+".json"
            with open(os.path.expanduser(filepath),'w') as fp:
                json.dump(out,fp)
            sys.exit()

    def on_error(self, status_code):
        if status_code == 420:
            return False

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
        'GU': 'Guam',
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
        'MP': 'Northern Mariana Islands',
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
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
        }

auth = tweepy.OAuthHandler('BnMPYrSUA0eADwbwI6t3mgwp2', '5qtFOcUxWpbfUn3MchuLSg8lwLtBLCCTwlne0nCiwWZbf38pmy')
auth.set_access_token('157063315-jr1ceRLeScPWFKXovH8KVr1YrbdgFWBJokjRxdtK', '1K4nIYxMHewFtpC0lW5Vb087sQ9Cdwc13wdxjhm7is06a')

api = tweepy.API(auth)
myStreamListener = MyStreamListener()
table = {}

for state in states:
    table[state]=[]
stream = tweepy.Stream(auth=api.auth, listener=MyStreamListener(),tweet_mode='extended')

keyword = "Trump"
stream.filter(track=[keyword])