import tweepy as tw
import credentials
import pandas as pd
import numpy as np
from datetime import datetime

# ------------------------------------- Twitter Authentication ---------------------------
class TwitterAuthentication():
        
    def authenticate_twitter(self):
        """ A class to connect to twitter API and authenticate """
        auth = tw.OAuthHandler(
            consumer_key = credentials.api_key,
            consumer_secret= credentials.api_secret_key
        )
        auth.set_access_token(
            key = credentials.access_token,
            secret = credentials.access_token_secret
        )

        return auth

# ---------------------------------------- Get Tweets -----------------------------------

class GetTweets():
    """ A class to stream and write tweets """
    def __init__(self):
        # Instantiate TwitterAuthentication object and authenticate access to twitter
        
        auth = TwitterAuthentication().authenticate_twitter()
        self.api = tw.API(auth)
        self.df_live_tweets = None
        self.df_past_tweets = None
        self.df_past30_tweets = None
        self.df_past_compiled = None
        self.file_name = None

    # Stream live tweets ------------------------------------------------------------------------------

    def stream_live_tweets(self,keyword,num_tweets):
        """ Method to search live tweets (past 7 days) """
        
        # Stream live twitter data (past 7 days)
        tweetsObj = tw.Cursor(
            self.api.search,
            q = keyword +'-filter:retweets',    
        ).items(num_tweets)

        properties = ['author','contributors','coordinates','created_at','destroy','entities','extended_entities','favorite','favorite_count','favorited','geo','id','id_str','in_reply_to_screen_name','in_reply_to_status_id','in_reply_to_status_id_str','in_reply_to_user_id','in_reply_to_user_id_str','is_quote_status','lang','metadata','parse','parse_list','place','possibly_sensitive','quoted_status','quoted_status_id','quoted_status_id_str','retweet','retweet_count','retweeted','retweets','source','source_url','text','truncated','user']

        tweet_list = []
        for tweet in tweetsObj:
            tweet_list.append({key : getattr(tweet,key,None) for key in properties})

        self.df_live_tweets= pd.DataFrame(data = tweet_list)
        self.df_live_tweets.set_index('id',inplace = True)
        
        return self.df_live_tweets

    # Stream past tweets (30 days) --------------------------------------------------------------------------------

    def stream_past30_tweets(self,keyword,search_from,search_to,max_results = 100,pg = 1, lang = None ,country_code = None):
        """Streams past 30 data tweets, uses 30 Days / Sandbox Account"""


        if (lang is not None) & (country_code is not None):
            keyword = keyword + ' lang:' + lang + ' place_country:' + country_code
        elif (lang is None) & (country_code is not None):
            keyword = keyword  + ' place_country:' + country_code
        elif (lang is not None) & (country_code is None):
            keyword = keyword + ' lang:' + lang 
        else:
            keyword = keyword


        # Tweepy cursor object
        past30TweetsObj = tw.Cursor(
            self.api.search_30_day,
            environment_name = 'VolcanicDisaster30',
            query = keyword, 
            maxResults = max_results,
            fromDate = search_from,
            toDate = search_to
        ).pages(pg)
        
        
        # Create Dataframe
        properties = ['author','contributors','coordinates','created_at','destroy','display_text_range','entities','extended_entities','extended_tweet','favorite','favorite_count','favorited','filter_level','geo','id','id_str','in_reply_to_screen_name','in_reply_to_status_id','in_reply_to_status_id_str','in_reply_to_user_id','in_reply_to_user_id_str','is_quote_status','lang','matching_rules','parse','parse_list','place','possibly_sensitive','quote_count','quoted_status','quoted_status_id','quoted_status_id_str','quoted_status_permalink','reply_count','retweet','retweet_count','retweeted','retweeted_status','retweets','source','source_url','text','truncated','user']
        
        page_list = [pg for pg in past30TweetsObj]
        tweet_list = [{key : getattr(tweet,key,None) for key in properties} for tweet_collection in page_list for tweet in tweet_collection]

        self.df_past30_tweets = pd.DataFrame(data = tweet_list)
        self.df_past30_tweets.set_index('id', inplace = True)
        

        return self.df_past30_tweets
      
    # stream past tweets (since 2006) -------------------------------------------------------------------------------

    def stream_past_tweets(self,keyword,search_from,search_to,max_results = 100, pg = 1, lang = None ,country_code = None):
        """ Method to search for past tweets (since 2006) """

        if (lang is not None) & (country_code is not None):
            keyword = keyword + ' lang:' + lang + ' place_country:' + country_code
        elif (lang is None) & (country_code is not None):
            keyword = keyword  + ' place_country:' + country_code
        elif (lang is not None) & (country_code is None):
            keyword = keyword + ' lang:' + lang 
        else:
            keyword = keyword

        # Stream past twitter data (since 2006)
        pastTweetsObj = tw.Cursor(
            self.api.search_full_archive,
            environment_name = 'VolcanicDisaster',
            query = keyword, 
            maxResults = max_results,
            fromDate = search_from,
            toDate = search_to
        ).pages(pg)

        # create a dataframe with past tweets
        properties = ['author','contributors','coordinates','created_at','destroy','display_text_range','entities','extended_entities','extended_tweet','favorite','favorite_count','favorited','filter_level','geo','id','id_str','in_reply_to_screen_name','in_reply_to_status_id','in_reply_to_status_id_str','in_reply_to_user_id','in_reply_to_user_id_str','is_quote_status','lang','matching_rules','parse','parse_list','place','possibly_sensitive','quote_count','quoted_status','quoted_status_id','quoted_status_id_str','quoted_status_permalink','reply_count','retweet','retweet_count','retweeted','retweeted_status','retweets','source','source_url','text','truncated','user']

        page_list = [pg for pg in pastTweetsObj]
        tweet_list = [{key : getattr(tweet,key,None) for key in properties} for tweet_collection in page_list for tweet in tweet_collection]

        self.df_past_tweets = pd.DataFrame(data = tweet_list)
        self.df_past_tweets.set_index('id',inplace = True)

        return self.df_past_tweets

    # Compiled dataframe --------------------------------------------------------------------------------

    def stream_single_over_dateRange(self,keyword,search_from,search_to,max_results = 100, pg = 1, lang = None, country_code = None, pastSearch30 = True):
        from datetime import date,timedelta
        from dateutil.relativedelta import relativedelta

        # Construct query based on keyword, lang, and country code
        if (lang is not None) & (country_code is not None):
            keyword = keyword + ' lang:' + lang + ' place_country:' + country_code
        elif (lang is None) & (country_code is not None):
            keyword = keyword  + ' place_country:' + country_code
        elif (lang is not None) & (country_code is None):
            keyword = keyword + ' lang:' + lang 
        else:
            keyword = keyword

        # Create a range of dates to iterate over
        startDate = datetime.strptime(search_from,'%Y%m%d%H%M')
        endDate = datetime.strptime(search_to,'%Y%m%d%H%M')
        dateRange = [startDate + timedelta(days = i) for i in range((endDate-startDate).days)]
        dateRangeStr =[dt.strftime('%Y%m%d%H%M') for dt in dateRange]

        # create a dataframe with past tweets
        properties = ['author','contributors','coordinates','created_at','destroy','display_text_range','entities','extended_entities','extended_tweet','favorite','favorite_count','favorited','filter_level','geo','id','id_str','in_reply_to_screen_name','in_reply_to_status_id','in_reply_to_status_id_str','in_reply_to_user_id','in_reply_to_user_id_str','is_quote_status','lang','matching_rules','parse','parse_list','place','possibly_sensitive','quote_count','quoted_status','quoted_status_id','quoted_status_id_str','quoted_status_permalink','reply_count','retweet','retweet_count','retweeted','retweeted_status','retweets','source','source_url','text','truncated','user']
        
        if pastSearch30 == True:
            
            df_list = []

            for dt_idx,dt in enumerate(dateRangeStr):
                if dt_idx < len(dateRangeStr)-1:
                    # Tweepy cursor object
                    df_search30 = self.stream_past30_tweets(keyword = keyword, search_from = dt , search_to = dateRangeStr[dt_idx + 1], pg =pg, lang = lang, country_code = country_code)
                    df_list.append(df_search30)

            self.df_past_compiled = pd.concat(df_list)

        else:

            df_list = []

            for dt_idx,dt in enumerate(dateRangeStr):
                if dt_idx < len(dateRangeStr)-1:
                    # Tweepy cursor object
                    df_search = self.stream_past_tweets(keyword = keyword, search_from = dt , search_to = dateRangeStr[dt_idx + 1], pg =pg, lang = lang, country_code = country_code)
                    df_list.append(df_search)

            self.df_past_compiled = pd.concat(df_list)


        return self.df_past_compiled
        

    # write data ----------------------------------------------------------------------------------------

    def write_to_csv(self,f_name = None):
        """Method to write streamed tweets to csv file """

        self.file_name = f_name
        if self.file_name is not None:
            path = 'D:/Python/Disaster Sentiment Analysis/Data/'
            with open(path + self.file_name,'w'):
                pass

            if self.df_live_tweets is not None:
                self.df_live_tweets.to_csv(path + self.file_name)

            if self.df_past_tweets is not None:
                self.df_past_tweets.to_csv(path + self.file_name)

            if self.df_past30_tweets is not None:
                self.df_past30_tweets.to_csv(path + self.file_name)

            if self.df_past_compiled is not None:
                self.df_past_compiled.to_csv(path + self.file_name)

        if (self.df_live_tweets is not None) & (self.file_name is None) & (self.df_past_compiled is None) :
            self.df_live_tweets.to_csv('D:/Python/Disaster Sentiment Analysis/Data/live_tweets.csv')

        if (self.df_past_tweets is not None) & (self.file_name is None) & (self.df_past_compiled is None):
            self.df_past_tweets.to_csv('D:/Python/Disaster Sentiment Analysis/Data/past_tweets.csv')

        if (self.df_past30_tweets is not None) & (self.file_name is None) & (self.df_past_compiled is None):
            self.df_past30_tweets.to_csv('D:/Python/Disaster Sentiment Analysis/Data/past30_tweets.csv')

        if (self.df_past_compiled is not None) & (self.file_name is None):
            self.df_past_compiled.to_csv('D:/Python/Disaster Sentiment Analysis/Data/past_compiled_tweets.csv')

    # read data ----------------------------------------------------------------------------------------

    def read_csv(self,f_name):
        """ Method to read saved tweets in csv file """
        path = 'D:/Python/Disaster Sentiment Analysis/Data/'
        df = pd.read_csv(path + f_name, index_col = 'id')
        return df
        
# --------------------------------------- Run Main File -----------------------------------------------

"""
if __name__ == '__main__':
    inst = GetTweets()
    df = inst.stream_live_tweets(keyword = '#kilauea', num_tweets= 5)
    print(df)
    #print(df.shape)

    # try to write it to file
    #inst.write_to_csv()
    #print(inst.read_csv())
    
    tweets_list = list()
    print(inst.liveTweetsObj)
    for tweet in inst.liveTweetsObj:
        print(tweet.id)


"""

"""
#previous method
# Streams past tweets from te past 30 days
        past30TweetsObj = self.api.search_30_day(
            environment_name = 'VolcanicDisaster30',
            query = keyword,
            fromDate =search_from,
            toDate = search_to
        )

"""

    
