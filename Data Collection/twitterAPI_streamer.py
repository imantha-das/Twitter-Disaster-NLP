from TwitterAPI import TwitterAPI
import twitter_credentials
import pandas as pd

# ------------------------------------------ TwitterAuthentication -----------------------------------

class TwitterAuthentication():
    """Class to authentice access to twitter API"""
    def authenticate_twitter(self):
        api = TwitterAPI(
            consumer_key= twitter_credentials.api_key,
            consumer_secret= twitter_credentials.api_secret_key,
            access_token_key= twitter_credentials.access_token,
            access_token_secret=twitter_credentials.access_token_secret
        )
        return api

# ----------------------------------------------- getTweets ------------------------------------------

class getTweets():
    """Class to retrieve and read + write tweets to csv files"""
    def __init__(self):
        auth = TwitterAuthentication()

        # attributes
        self.api = auth.authenticate_twitter()

        self.df_live_tweets = None
        self.df_past_tweets = None
        

    # Stream live tweets --------------------------------------------------------------------------------

    def stream_live_tweets(self,keyword):
        """ Method to retrieve live stream tweets (past 7 days) """
        
        # Make a request to the twitter API
        req = self.api.request(
            'search/tweets',
            {
                'q' : keyword + '-filter:retweets',
                'lang' : 'en'
            }
        )

        # Create dataframe with live tweets
        tweet_list = []
        for tweet in req:
            tweet_list.append(
                {
                'created_at' : tweet['created_at'],
                'id' : tweet['id'],
                'text' : tweet['text'],
                'favorite_count' : tweet['favorite_count'],
                'favorited' : tweet['favorited'],
                'retweet_count' : tweet['retweet_count'],
                'retweeted' : tweet['retweeted'],
                'source' : tweet['source'],
                'user' : tweet['user'],
                'geo' : tweet['geo'],
                'coordinates' : tweet['coordinates'],
                }
            )
        self.df_live_tweets = pd.DataFrame(data = tweet_list)
        self.df_live_tweets.set_index('id',inplace = True)

        return self.df_live_tweets

    # Stream past tweets -----------------------------------------------------------------------------------

    def stream_past_tweets(self,keyword,search_from,search_to,num_tweets):
        """ Method to stream past tweets """

        # Make request to twitter API
        self.req = self.api.request(
            'tweets/search/%s/:%s' % ('fullarchive','VolcanicDisaster'),
            #'tweets/search/fullarchive/:VolcanicDisaster',
            {
                'query': keyword,
                'fromDate' : search_from,
                'toDate' : search_to,
                'maxResults' : num_tweets
            }
        )

        # Create a dataframe with past tweets
        tweet_list = []
        for tweet in self.req:
            tweet_list.append(
                {
                'created_at' : tweet['created_at'], 
                'id' : tweet['id'],
                'id_str' : tweet['id_str'],
                'text' : tweet['text'],
                'source' : tweet['source'],
                'truncated' : tweet['truncated'],
                'in_reply_to_status_id' : tweet['in_reply_to_status_id'],
                'in_reply_to_status_id_str' : tweet['in_reply_to_status_id_str'],
                'in_reply_to_user_id' : tweet['in_reply_to_user_id'],
                'in_reply_to_user_id_str' : tweet['in_reply_to_user_id_str'],
                'in_reply_to_screen_name' : tweet['in_reply_to_screen_name'],
                'user' : tweet['user'],
                'geo' : tweet['geo'],
                'coordinates' : tweet['coordinates'],
                'place' : tweet['place'],
                'contributors' : tweet['contributors'],
                #'retweeted_status' : tweet['retweeted_status'],
                'is_quote_status' : tweet['is_quote_status'],
                'quote_count' : tweet['quote_count'],
                'reply_count' : tweet['reply_count'],
                'retweet_count' : tweet['retweet_count'],
                'favorite_count' : tweet['favorite_count'],
                'entities' : tweet['entities'],
                'favorited' : tweet['favorited'],
                'retweeted' : tweet['retweeted'],
                'filter_level' : tweet['filter_level'],
                'lang' : tweet['lang'],
                'matching_rules' : tweet['matching_rules']
                }
            )

        self.df_past_tweets = pd.DataFrame(data = tweet_list)
        self.df_past_tweets.set_index('id',inplace = True)
        

        return self.df_past_tweets

    # Write data -------------------------------------------------------------------------------------------

    def write_to_csv(self):

        if self.df_live_tweets is not None:
            self.df_live_tweets.to_csv('D:/Python/Disaster Sentiment Analysis/live_tweets.csv')

        if self.df_past_tweets is not None:
            self.df_past_tweets.to_csv('D:/Python/Disaster Sentiment Analysis/past_tweets.csv')

    # Read Data -------------------------------------------------------------------------------------------

    def read_from_csv(self,live = False):

        if live == True:
            df = pd.read_csv('D:/Python/Disaster Sentiment Analysis/live_tweets.csv', index_col = 'tweet_id')
            return df
        else:
            df = pd.read_csv('D:/Python/Disaster Sentiment Analysis/past_tweets.csv', index_col = 'tweet_id')
            return df



if __name__ == '__main__':
    inst = getTweets()

    print(inst.stream_live_tweets(keyword = '#kilauea'))
    
"""
Notes from twitter API
* maxResults (num_tweets) : passed as a string
* formDate : passed as a string "YYYYMMDDHHmm"
* toDate : passed as a string "YYYYMMDDHHmm"
"""