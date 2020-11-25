import numpy as np 
import pandas as pd 

import dash  
import dash_core_components as dcc   
import dash_html_components as html 
from dash.dependencies import Input, Output 

from wordcloud import WordCloud, STOPWORDS 
from io import BytesIO
import base64 
import re 

import plotly.graph_objs as go 
import plotly.express as px

import credentials

from termcolor import colored
from datetime import datetime

#______________________________________________________________________________________________________
# Notes : DELETE ME
# All columns names : id, author_name, author_sc

# Data
# ______________________________________________________________________________________________________

data = pd.read_csv("D:/Python/Disaster Sentiment Analysis/Data/Taal/Taal_200111_200119_en_PH_labeled.csv")

selectedCols = ["id","created_at","tweet","lang","lat","lon","sentiment_labels","ash_labels","damage_labels","help_labels","prayer_labels"]

df = data[selectedCols]

# Drop rows with missing values. In this case these are the values without lat/lon values.
df.dropna(inplace = True)

# Dictionary to replace lang code with lang names
lang_dict = {'en' : 'english','es' : 'spanish', 'tl' : 'taglog', 'nl' : 'dutch', 'und' : 'undefned', 'fr' : 'french', 'de' : 'german', 'hi' :  'hindi', 'it' : 'italian', 'in' : 'indonesian', 'ja' : 'japanese', 'et' : 'estonian', 'pt' : 'portuguese', 'ru' : 'russian', 'ar' : 'Arabic', 'ca' : 'catalan','zh' : 'chinese', 'lt' : 'lithuanian', 'ht' : 'hatian', 'cy' : 'welsh', 'pl' : 'polish' }

df["lang"] = df["lang"].apply(lambda x : lang_dict[x])

# Calculate length of tweet
df["length_of_tweet"] = df["tweet"].apply(lambda x : len(x))

# Keys and Tokens
# ______________________________________________________________________________________________________

mapbox_key = credentials.mapbox_key

# Colors & Styles
# ______________________________________________________________________________________________________

sty_d = {
    "fs_title" : "46px",
    "fc_title" : "olive",
    "fs_header" : "30px",
    "fc_header" : "darkslategray"
}

# Plot Figures
# _____________________________________________________________________________________________________

# Sentiment count -------------------------------------------------------------------------------------
df_sent = df["sentiment_labels"].value_counts()

fig_sent_hist = go.Figure()
fig_sent_hist.add_trace(
    go.Bar(name = "positive", x = [1], y = [df_sent.loc[1]], marker_color = '#407BBF')
)
fig_sent_hist.add_trace(
    go.Bar(name = "negative", x = [-1], y = [df_sent.loc[-1]], marker_color = "#EE4D2E")
)
fig_sent_hist.add_trace(
    go.Bar(name = "neutral", x = [0], y = [df_sent.loc[0]], marker_color = "#FFAC20")
)
fig_sent_hist.update_layout(
    xaxis_title = "sentiment", yaxis_title = "tweet count", template = "plotly_white"
)

# Tweets per date ------------------------------------------------------------------------------------
df_time = df["created_at"].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()).value_counts().sort_index()

fig_time = go.Figure()
fig_time.add_trace(go.Scatter(
    x = df_time.index,
    y = df_time.values,
    mode = "markers + lines",
    line = dict(
        color = "steelblue"
    )
))

fig_time.update_layout(
    xaxis_title = "date", yaxis_title = "tweet count", template = "plotly_white"
)

# Tweet length ---------------------------------------------------------------------------------------

fig_tweet_len = px.histogram(
    df,
    x = "length_of_tweet", 
    color = "sentiment_labels", 
    color_discrete_sequence = ['#FFAC20','#EE4D2E','#407BBF'],  
    opacity = 0.8)

fig_tweet_len.update_layout(
    template = "plotly_white"
    )

# Dash App
# ______________________________________________________________________________________________________

app = dash.Dash()

app.layout = html.Div([

    html.H1(
        children = "Sentiment Analysis for Taal eruption 2020",
        style = {"textAlign" : "center", "color" : sty_d["fc_title"], "font-size" : sty_d["fs_title"]}
    ),

    html.Div([
        html.H2(
            children = "Select Language & Labels", 
            style = {'color' : sty_d["fc_header"], 'font-size' : sty_d["fs_header"]}
            ),
        html.Div([
            dcc.Dropdown(
                id = "lang-dd",
                options = [{"label" : i, "value" : i} for i in df["lang"].unique()],
                value = "english",
                #multi = True
            )
        ],style = {"width" : "48%", "display" : "inline-block"}
        ),
        html.Div([
            dcc.Dropdown(
                id = "label-cl",
                options = [
                    {"label" : "sentiment", "value" : "sentiment_labels"},
                    {"label" : "ash", "value" : "ash_labels"},
                    {"label" : "interuption", "value" : "damage_labels"},
                    {"label" : "help", "value" : "help_labels"},
                    {"label" : "prayer", "value" : "prayer_labels"}],
                value = "sentiment_labels"
            )
        ], style = {"width" : "48%", "display" : "inline-block"}
        )
    ]),

    #Map 
    # ---------------------------------------------------------------------------------------------------------------------------
    dcc.Graph(
        id = 'map',
        config = {"displayModeBar" : False, "scrollZoom" : True},
        style = {'background' : '#00F87', 'padding-bottom' :'2px', 'padding-left' : '2px', 'padding-top' : '2px','height' : '75vh'}
    ),

    #Tweet dialog
    # ---------------------------------------------------------------------------------------------------------------------------
    html.Div([
        html.H3(
            children = "Tweet:",
            style = {"font-size" : "24px", "color" : "olive"}
        )
    ]
    ),

    html.Pre(
        id = "tweet",
        children = [],
        style = {'white-space' : 'pre-wrap', 'word-break' : 'break-all', 'border' : '1px sold balck', 'text-align' : 'enter', 'padding' : '0px 12px 12px 70px', 'color' : 'black', 'margin-top' : '3px','font-size' : '20px', 'color' : 'olive', 'font-weight' : 'bold'}
    ),

    # Sentiment count histogram 
    # --------------------------------------------------------------------------------------------------------------------------
    html.Div([

        html.Div([
            html.H2(
                children = "No of tweets per sentiment",
                style = {"font-size" : sty_d["fs_header"], "color" : sty_d["fc_header"]}
            ),
            dcc.Graph(
                id = "sentiment-count",
                config = {"displayModeBar" : False},
                figure = fig_sent_hist
            )
        ], style = {"width" : "48%", "float" : "left", "display" : "inline-block"}
        ),

        html.Div([
            html.H2(
                children = "No of tweets per day",
                style = {"font-size" : sty_d["fs_header"], "color" : sty_d["fc_header"],"display" : "inline-block"}
            ),
            dcc.Graph(
                id = "tweets-per-time",
                config = {"displayModeBar" : False},
                figure = fig_time
            )
        ], style = {"width" : "48%", "float" : "right", "display" : "inline-block"}
        )
    ]),

    html.Div([

        html.Div([
            html.H2(
                children = "wordcloud",
                style = {"font-size" : sty_d["fs_header"], "color" : sty_d["fc_header"]}
            ),
            dcc.RadioItems(
                id = "sentiment-selector",
                options = [
                    {"label" : "positive", "value" : "pos-val"},
                    {"label" : "neutral", "value" : "neut-val"},
                    {"label" : "negative", "value" : "neg-val"}
                ],
                value = "pos-val"
            ),
            html.Br(),
            html.Img(
                id = "wc"    
            )
        ],style = {"width" : "48%", "float" : "left", "diplay" : "inline-block"}
        ),

        html.Div([
            html.H2(
                children = "Tweet length per sentiment",
                style = {"width" : "48%","font-size" : sty_d["fs_header"], "color" : sty_d["fc_header"]}  
            ),
            dcc.Graph(
                config = {"displayModeBar" : False},
                figure = fig_tweet_len
            )
        ],style = {"width" : "48%", "float" : "right","display" : "inline-block"})
    ]
    )
])
# Call backs
# ____________________________________________________________________________________________________________________________

@app.callback(
    Output("map","figure"),
    [
        Input("lang-dd","value"),
        Input("label-cl","value")
    ]
)

# Update Map
# ----------------------------------------------------------------------------------------------------------------------------
def update_map(lang_val,label_val):


    df_lang = df[df["lang"].isin([lang_val])]

    if label_val == "sentiment_labels":
        df_pos = df_lang[df_lang[label_val] == 1]
        df_neg = df_lang[df_lang[label_val] == -1]
        df_neut = df_lang[df_lang[label_val] == 0]

        fig_map = go.Figure()
        fig_map.add_trace(
            go.Scattermapbox(
                lat = df_pos['lat'],
                lon = df_pos['lon'],
                mode = 'markers',
                marker = go.scattermapbox.Marker(size =8, color = '#407BBF'),
                name = "positive",
                customdata = df_pos["tweet"]
            )
        )

        fig_map.add_trace(
            go.Scattermapbox(
                lat = df_neg['lat'],
                lon = df_neg['lon'],
                mode = 'markers',
                marker = go.scattermapbox.Marker(size =8, color = '#EE4D2E'),
                name = "negative",
                customdata = df_neg["tweet"]
            )
        )

        fig_map.add_trace(
            go.Scattermapbox(
                lat = df_neut['lat'],
                lon = df_neut['lon'],
                mode = 'markers',
                marker = go.scattermapbox.Marker(size =8, color = '#FFAC20'),
                name = "neutral",
                customdata = df_neut["tweet"]
            )
        )
        
    else:

        df_update = df_lang[df[label_val] == 1]

        fig_map = go.Figure()
        fig_map.add_trace(
            go.Scattermapbox(
                lat = df_update['lat'],
                lon = df_update['lon'],
                mode = 'markers',
                marker = go.scattermapbox.Marker(size =8, color = 'slategray'),
                customdata = df_update["tweet"]
            )
        )

    # Update the layout of the map, either the map from sentiment labels or the other labels
    fig_map.update_layout(
        uirevision = 'foo',
        clickmode = 'event+select',
        hovermode = 'closest',
        hoverdistance = 1,
        mapbox = dict(
            accesstoken = mapbox_key,
            center = dict(lat = 14.00,lon = 120.99),
            pitch = 0,
            zoom = 5,
            style = 'light'
        ),
    )

    return fig_map

@app.callback(
    Output("tweet","children"),
    [Input("map","clickData")]
)

def displayText(clickData):
    if clickData is None:
        return "click on any of the points on the map"
    else:
        tweet_text = clickData["points"][0]["customdata"]
        return tweet_text

# Word cloud
# ------------------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output("wc","src"),
    [Input("sentiment-selector", "value")]
)
def updateWC(sent_val):
    if sent_val == "pos-val":
        df_sent = df[df["sentiment_labels"] == 1]
    elif sent_val == "neg-val":
        df_sent = df[df["sentiment_labels"] == -1]
    else:
        df_sent = df[df["sentiment_labels"] == 0]

    cleaned_tweets = []
    for tweet in df_sent["tweet"]:
        cleaned_tweets.append(re.sub(r"http\S+","",tweet))

    img = BytesIO()

    # Create word cloud
    longstring = ','.join(cleaned_tweets)
    wordcloud = WordCloud(stopwords = STOPWORDS,background_color='white',max_words=5000,contour_width=14, contour_color='steelblue', height = 350, width = 800)
    wordcloud.generate(longstring)
    wordcloud.to_image().save(img, format = 'PNG')
    
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

if __name__ == "__main__":
    app.run_server(debug = False)
