# Sentiment Analysis for Volcanic Disasters

![](Images-Gifs/Dash-App.gif)

## Overview 
* credentials.py : Contains credential to access TwitterAPI & Mapbox accounts
* twitterAPI_streamer.py : Class to stream data from twitter API + read and write data to csv files.
* DataVis.py : Dashboard for data visualization

## How to use

### Credentials
* Please follow the instructions at https://developer.twitter.com/en/apply-for-access to setup twitter developer account
  * The following 4 access codes will be required to authenticate and connect to the twitter API.
      * Under the developer portal an app must be created ( more information how to create an app found at https://developer.twitter.com/en/docs/apps/overview)
      * The app must be upgraded upgraded into tier "sandbox" (free version with streaming up to 5000 tweets per month) or "premium" (paid with more functionality and streaming more data)
      * The '???' must filled with the user access tokens
      
### Stream Data
* twitter_credentials.py : File containing the twitter authentification credentials.   
* tweepy_streamer : Class containing functions to stream data using tweepy package and write data to csv file.
  * stream_live_tweets : Stream tweets in past 7 days (Unlmited access)
    * Example :
      * inst = GetTweets()
      * inst.stream_live_tweets(keyword = 'Taal', num_tweets =50)
  * stream_past30_tweets : Capable of streaming tweets for the last 30 days (Limited access)
    * Example
      * inst.stream_past30_tweets((keyword = 'Taal',search_from='202001120000', search_to = '202001200000',max_results=100,pg = 10, lang = 'en')
  * stream_past_tweets : Capable of streaming tweets since 2006
    * Example :
       * inst.stream_past_tweets(keyword = 'Taal',search_from='202001120000', search_to = '202001200000',max_results=100,pg = 10, country_code = 'PH')
  * stream_single_over_dateRange : Iterates over each day and stream the number of pages inputed.
    * Uses either stream_past30_tweets method or stream_past_tweets method. 
      * To use stream_past30_tweets, set streamPast30 = True. 
      * To use stream_past_tweets, set streamPast30 = False.
    * Example : 
      * df = inst.stream_single_over_dateRange(keyword = 'Taal', search_from = '202009210000', search_to = '202010010000', pg =2, country_code = 'PH', pastSearch30=True)
  * search_from, search_to are in the format 'YYYYMMDDHHMM'
  * max_results : maxmum number of results tat can be streamedin one response (Max of 100 for free sandbox environments)
  * pg : No of pages the search results will look through (note search of each page will eat 1 response of your usage)
  * lang : streams only the language requested (Note language must be a two letter code)
  * country_code : Will stream only tweets from requestd country (Note country_code is a two letter code)
 
