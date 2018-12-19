#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 22:21:09 2018

@author: annietong
"""

#GOOGLE SENTIMENT TWEETS
import sys
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from google.cloud.language_v1 import types
from google.oauth2 import service_account
import six
import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import time
import os
import sys
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
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


def load_api():

    auth = tweepy.OAuthHandler('BnMPYrSUA0eADwbwI6t3mgwp2', '5qtFOcUxWpbfUn3MchuLSg8lwLtBLCCTwlne0nCiwWZbf38pmy')
    auth.set_access_token('157063315-jr1ceRLeScPWFKXovH8KVr1YrbdgFWBJokjRxdtK', '1K4nIYxMHewFtpC0lW5Vb087sQ9Cdwc13wdxjhm7is06a')
    return tweepy.API(auth)

def tweet_search(api, query, max_tweets, max_id, since_id, geocode):


    searched_tweets = []
    while len(searched_tweets) < max_tweets:
        remaining_tweets = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=remaining_tweets,
                                    since_id=str(since_id),
				                    max_id=str(max_id-1),
                                    tweet_mode = 'extended',
                                     geocode=geocode)
            print('found',len(new_tweets),'tweets')
            if not new_tweets:
                print('no tweets found')
                break
            searched_tweets.extend(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError:
            print('exception raised, waiting 15 minutes')
            print('(until:', dt.datetime.now()+dt.timedelta(minutes=15), ')')
            time.sleep(15*60)
            break # stop the loop
    return searched_tweets, max_id


def get_tweet_id(api, date='', days_ago=9, query='a'):
    if date:
        td = date + dt.timedelta(days=1)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        tweet = api.search(q=query, count=1, until=tweet_date)
    else:
        # return an ID from __ days ago
        td = dt.datetime.now() - dt.timedelta(days=days_ago)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        # get list of up to 10 tweets
        tweet = api.search(q=query, count=10, until=tweet_date)
        print('search limit (start/stop):',tweet[0].created_at)
        # return the id of the first tweet in the list
        return tweet[0].id
    
def write_tweets(tweets, filename):
    ''' Function that appends tweets to a file. '''

    with open(filename, 'a') as f:
        for tweet in tweets:
            json.dump(tweet._json, f)
            f.write('\n')

    
def get_state(tweet):
    if tweet._json['user']['location']!= None:
        for state in states:
            if state in tweet._json['user']['location'] or states[state] in tweet._json['user']['location']:
                return state
    else:
        return None
    
def clean_tweet(tweet):
    if "retweeted_status" in tweet._json:
        text = tweet._json['retweeted_status']['full_text']
    else:
        text = tweet._json['full_text']
    t = re.sub('(?<=^|(?<=[^a-zA-Z0-9-_.]))@([A-Za-z0-9]+)','',text)
    t = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',t)
    t = re.sub('[\s]+',' ',t)
    t = re.sub('RT : ','', t)
    return t
    
def get_sentiment(text,key):
    d = {}
    """Detects entity sentiment in the provided text."""
    credentials = service_account.Credentials. from_service_account_file('nlptest-417953ad79a8.json')

    client = language_v1.LanguageServiceClient(credentials=credentials)

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')
    
    document = types.Document(
        content=text.encode('utf-8'),
        type=enums.Document.Type.PLAIN_TEXT)

    try:
        result = client.analyze_entity_sentiment(document=document)
        for entity in result.entities:
            d[str(entity.name)]=entity.sentiment.score
        if key in d:
            print("google key in: "+str(d[key]))
            print("vadar: "+str(get_vadar_sentiment(text)))
            ss = (d[key]+get_vadar_sentiment(text))/2
            return ss
        else:
            annotations = client.analyze_sentiment(document=document)
            print("google: "+str(annotations.document_sentiment.score))
            print("vadar: "+str(get_vadar_sentiment(text)))
            ss = (annotations.document_sentiment.score+get_vadar_sentiment(text))/2
            return ss
    except:
        return get_vadar_sentiment(text)/2
            
def get_vadar_sentiment(texts):
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(texts)
    sentiment = ss['compound']
    return sentiment

def calculate_avg(d):
    avgdict = {}
    avgplusnumber = {}
    outputd={}
    for state in states:
        avgdict[state]="not available"
        avgplusnumber[state]=("not available",0)
    for i in d:
        if len(d[i])>0:
            poscount = 0
            negcount = 0
            totalcount = 0
            for tw in d[i]:
                totalcount+=1
                if tw>0:
                    poscount+=1
                elif tw<0:
                    negcount+=1
            pos = poscount/len(d[i])
            neg = negcount/len(d[i])
            if pos>0 or neg>0:
                posper = pos/(pos+neg)
            else:
                posper = 0
            avgdict[i]=posper
            avgplusnumber[i]=(posper,totalcount)
    outputd["average"]=avgdict
    outputd["averagewithnumber"]=avgplusnumber
    return outputd
            
        

def main():
    ''' This is a script that continuously searches for tweets
        that were created over a given number of days. The search
        dates and search phrase can be changed below. '''

    ''' search variables: '''
    
    time_limit = float(sys.argv[2])                          # runtime limit in hours
    max_tweets = 100                           # number of tweets per search (will be
                                               # iterated over) - maximum is 100
    min_days_old, max_days_old = int(sys.argv[3]), int(sys.argv[4])          # search limits e.g., from 7 to 8
                                               # gives current weekday from last week,
                                               # min_days_old=0 will search from right now
    USA = '39.8,-95.583068847656,2500km'       # this geocode includes nearly all American
                                               # states (and a large portion of Canada)
    
    search_phrases = [sys.argv[1]]
    out = {}
    for state in states:
        out[state]=[]
    for search_phrase in search_phrases:

        print('Search phrase =', search_phrase)

        ''' other variables '''
        name = search_phrase.split()[0]
        json_file_root = name + '/'  + name
        os.makedirs(os.path.dirname(json_file_root), exist_ok=True)
        read_IDs = False
        if max_days_old - min_days_old == 1:
            d = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
        else:
            d1 = dt.datetime.now() - dt.timedelta(days=max_days_old-1)
            d2 = dt.datetime.now() - dt.timedelta(days=min_days_old)
            day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
                  d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
        json_file = json_file_root + '_' + day + '.json'
        if os.path.isfile(json_file):
            print('Appending tweets to file named: ',json_file)
            read_IDs = True
        
        #load the twitter API
        api = load_api()

        if read_IDs:
            # open the json file and get the latest tweet ID
            with open(json_file, 'r') as f:
                lines = f.readlines()
                max_id = json.loads(lines[-1])['id']
                print('Searching from the bottom ID in file')
        else:
            # get the ID of a tweet that is min_days_old
            if min_days_old == 0:
                max_id = -1
            else:
                max_id = get_tweet_id(api, days_ago=(min_days_old-1))
        # set the smallest ID to search for
        since_id = get_tweet_id(api, days_ago=(max_days_old-1))
        print('max id (starting point) =', max_id)
        print('since id (ending point) =', since_id)
        


        ''' tweet gathering loop  '''
        start = dt.datetime.now()
        end = start + dt.timedelta(hours=time_limit)
        count, exitcount = 0, 0
        while dt.datetime.now() < end:
            count += 1
            print('count =',count)
            tweets, max_id = tweet_search(api, search_phrase, max_tweets,
                                          max_id=max_id, since_id=since_id,
                                          geocode=USA)
            if tweets:
                for tweet in tweets:
                    if get_state(tweet)!=None:
                        tmp = out[get_state(tweet)]
                        t = clean_tweet(tweet)
                        print("------------------------")
                        print(t)
                        score = get_sentiment(t,search_phrase)
                        print("average:"+str(score))
                        tmp.append(score)
                        out[get_state(tweet)]=tmp
                write_tweets(tweets, json_file)
                exitcount = 0
            else:
                exitcount += 1
                if exitcount == 3:
                    if search_phrase == search_phrases[-1]:
                        sys.exit('Maximum number of empty tweet strings reached - exiting')
                    else:
                        print('Maximum number of empty tweet strings reached - breaking')
                        break
            filepath = "~/Desktop/data/"+sys.argv[1]+str(dt.datetime.now())+".json"
            with open(os.path.expanduser(filepath),'w') as fp:
                sentimentout = calculate_avg(out)["averagewithnumber"]
                json.dump(sentimentout,fp)


if __name__ == "__main__":
    main()
