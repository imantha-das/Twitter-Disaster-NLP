import os 
import argparse

# Text based libaries
import re
import string

# Dataframe and linear algebra libraries
import numpy as np 
import pandas as pd 

# NLP libraries
import spacy
from spacy.lang.en import English 
from spacy.tokenizer import Tokenizer
import emoji

# Unsupervised Sentiment Score libraries
from emosent import get_emoji_sentiment_rank

# Data Visulization libraries
import plotly.express as px
import plotly.graph_objs as go


def label_sentiment(df, replace_with):
    """
    Replaces integer values with 
    Inputs : df - Pandas DataFrame
             replace_with - python dictionary

    return DataFrame 
    """
    for k,v in replace_with.items():
        df.sentiment_labels = df.sentiment_labels.apply(lambda x: v if x == k else x)
    return df

# Feature Extraction
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def extract_tokens(tweet, regExp):
    """
    Extracts text based feature such as emotics, hashtags, etc.
    Inputs :
        Tweet
        regular expression to extract content such as emoticons, hashtags etc.
    Outputs :
        Count of 
    """
    tweetRegExp = re.compile(regExp)
    return len(tweetRegExp.findall(tweet))

def havesine_distance(tw_lat, tw_long, vol_lat = 14.13, vol_long = 120.99):
    """
    Caculates the havesine distance between 2 sets of GPS coordinates
    Input arguments :
        tw_lat : latitude where tweet originated from 
        tw_long : longitude where yweey originated from
        vol_lat : latitude of volcano
        vol_lonf : longitude of volcano
    Outputs :
        Haversine distance between tweet location and volcano
    """
    r = 6371 #Average radius of the earth in km
    tw_phi = np.radians(tw_lat)
    vol_phi = np.radians(vol_lat)

    delta_phi = np.radians(tw_lat - vol_lat)
    delta_lambda = np.radians(tw_long - vol_long)

    a = np.sin(delta_phi/2)**2 + np.cos(tw_phi) * np.cos(vol_phi) * np.sin(delta_lambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = (r * c) # in kilometers
    return d

# Data Visulaization
# --------------------------------------------------------------------------    

def data_vis(df):
    sent_counts = df.sentiment_labels.value_counts().to_frame()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x = sent_counts.index,
            y = sent_counts.sentiment_labels
        )
    )

    fig.update_layout(
        template = "plotly_white",
        xaxis_title = "sentiment",
        yaxis_title = "count"
    )

    return fig   

def plot_dist(df, colname, color_col = "sentiment_labels"):
    if color_col is None:
        fig = px.histogram(data_frame = df, x = colname)
    else:
        fig = px.histogram(data_frame = df, x = colname, color = color_col)
    return fig

# Extract Emoticons
# ---------------------------------------------------------------------------

def extract_emoticons(tweet):
    """
    Extracts emoticons from Tweet
    Inputs : Tweet
    Output : List of emoticons
    """
    return [c for c in tweet if c in emoji.UNICODE_EMOJI["en"].keys()]

def compute_emoticon_score(emoticonList:list):
    """
    Computes an emoticon score using emosent library
    Inputs : List of emoticons
    Outputs : Mean emoticon score for multiple emoji's, Score of 0 for tweets without emojis 
    """

    emoticon_score = [] 
    for emoticon in emoticonList:
        try:
            emoticon_score.append(get_emoji_sentiment_rank(emoticon)["sentiment_score"])
        except KeyError:
            emoticon_score.append(0)

    if len(emoticon_score) > 0:
        return sum(emoticon_score) / len(emoticon_score)
    else:
        return 0




if __name__ == "__main__":

    # Load data
    path = os.path.join(os.getcwd(),"twitter_sentiment_analysis", "Data","Taal_200111_200119_en_PH_labeled.csv")
    data = pd.read_csv(path)

    # Replace sentiment interger values with
    replace_with = {1 : "positive", 0 : "neutral", -1 : "negative"}

    df = label_sentiment(df = data, replace_with = replace_with)
    
    # Feature extraction
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    # Compute Haversine Distance
    df = df.assign(distance_from_volcano = lambda x: havesine_distance(x.lat, x.lon))
    
    # Extracts Mention, Hashtags and URLS counts
    regExpDict = {
        "mentions" : r'@\w+',
        "hashtags" : r'#\w+',
        "urls" :  r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    }
    
    for k,v in regExpDict.items():
        df[k] = df.tweet.apply(lambda tw: extract_tokens(tw, v))

    # Extract other text related features : Word count, unique words ...
    nlp = English()
    tokenizer = Tokenizer(nlp.vocab)

    sp = spacy.load("en_core_web_sm")
    all_stop_words = sp.Defaults.stop_words 
    all_punctuations = string.punctuation 

    df["word_count"] = df.tweet.apply(lambda x: len(tokenizer(x)))
    df["unique_word_count"] = df.tweet.apply(lambda x: len(set([word.text.lower() for word in tokenizer(x)])))
    df["char_count"] = df.tweet.apply(lambda x: len(x))
    df["stop_word_count"] = df.tweet.apply(lambda x: len([word for word in map(lambda x: x.text.lower(), tokenizer(x)) if word in all_stop_words]))
    df["mean_word_length"] = df.tweet.apply(lambda x: np.mean([len(w) for w in x.split()]))
    df["punctuation_count"] = df.tweet.apply(lambda x: len([char for char in x if char in all_punctuations]))

    # Compute emoticon score
    df["emoticons"] = df.tweet.apply(lambda x: extract_emoticons(tweet = x))
    df["emoticon_count"] = df["emoticons"].apply(lambda x: len(x))
    df["emoticon_score"] = df["emoticons"].apply(lambda x: compute_emoticon_score(emoticonList = x))


    # Data Visualization
    # ----------------------------------------------------------------------
    
    # Figure 
    #fig = data_vis(df = df)
    #fig.show()

    fig = plot_dist(df = df, colname = "emoticon_score", color_col = "sentiment_labels")
    fig.show()

    # Filter required columns
    df = df.filter(
        items = [
            "tweet", 
            "mentions", 
            "hashtags", 
            "urls", 
            "distance_from_volcano",
            "word_count",
            "unique_word_count",
            "char_cont",
            "stop_word_count",
            "mean_word_length",
            "punctuation_count",
            "emoticon_count",
            "emoticons",
            "emoticon_score",
            "sentiment_labels"
        ]
    )
    print(df)



