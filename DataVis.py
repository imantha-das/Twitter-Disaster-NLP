# Imports
#____________________________________________________________________________________________
import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from wordcloud import WordCloud,STOPWORDS
from io import BytesIO
import base64
import re

#Mapbox Credentials
import credentials

import plotly.express as px
import plotly.graph_objs as go

import pandas as pd

# Data
# ___________________________________________________________________________________________

data = pd.read_csv('D:/Python/Disaster Sentiment Analysis/Data/Taal_concise_0016_0019.csv',index_col = 0)
selectedCols = ['created_at','lang','lat','lon','text']
df = data[selectedCols]

# Drop all missing values
df.dropna(inplace = True)

# Dictionary to replace lang code with lang names
lang_dic = {'en' : 'english','es' : 'spanish', 'tl' : 'taglog', 'nl' : 'dutch', 'und' : 'undefned', 'fr' : 'french', 'de' : 'german', 'hi' :  'hindi', 'it' : 'italian', 'in' : 'indonesian', 'ja' : 'japanese', 'et' : 'estonian', 'pt' : 'portuguese', 'ru' : 'russian', 'ar' : 'Arabic', 'ca' : 'catalan','zh' : 'chinese', 'lt' : 'lithuanian', 'ht' : 'hatian', 'cy' : 'welsh', 'pl' : 'polish' }
df['lang'] = df['lang'].apply(lambda x : lang_dic[x])


# Keys and tokens
# ________________________________________________________________________________________________________________________________

mapbox_key = credentials.mapbox_key

# Dash App
# _______________________________________________________________________________________________________________________________

app = dash.Dash()

app.layout = html.Div([

    # ---------------------------------------------------------------------------------------------------------------------------

    html.H1(
        children = 'Twitter data analysis for Taal eruption 2020',
        style = {'textAlign' : 'center', 'color' : 'darkslategray', 'font-size' : '46px'}
    ),
    #C36337
    html.Div([
        html.H2('Language', style = {'color' : 'darkslategray', 'font-size' : '30px'}),
        dcc.Checklist(
            id = 'lang-id',
            options = [{'label' : i, 'value' : i} for i in df['lang'].unique()],
            value = ['english']
        )
    ],style = {'width' : '100%', 'display' : 'inlne-block', 'text-indent' : '70px'}
    ),

    # ----------------------------------------------------------------------------------------------------------------------------

    dcc.Graph(
        id ='fig-map',
        config = {'displayModeBar' : False, 'scrollZoom' : True},
        style = {'background' : '#00F87', 'padding-bottom' :'2px', 'padding-left' : '2px', 'padding-top' : '2px','height' : '75vh'} 
        ),

    # ----------------------------------------------------------------------------------------------------------------------------
    
    html.Div([
        html.H3(
            children = 'Tweet:',
        ),
    ], style = {'text-indent' : '70px'}
    ),

    html.Pre(
        id = 'text-disp-id',
        children = [],
        style = {'white-space' : 'pre-wrap', 'word-break' : 'break-all', 'border' : '1px sold balck', 'text-align' : 'enter', 'padding' : '0px 12px 12px 70px', 'color' : 'black', 'margin-top' : '3px','font-size' : '16px', 'color' : 'olive', 'font-weight' : 'bold'}
    ),
    # -----------------------------------------------------------------------------------------------------------------------

    html.Div([
        html.H2('Language Usage', style = {'font-size' : '30px', 'color' : 'darkslategray'}),
        html.Div([
            html.Img(
                id = 'word-cloud-id',
                style = {'padding-left' : '0px'}
            )
        ],style = {'width' : '48%','float' : 'right'}
        ),

        html.Div([
            dcc.Graph(
                id = 'languge-plot',
                config = {'displayModeBar' : False},
                figure = {
                    'data' : [
                        {
                            'x' : df['lang'].value_counts().index,
                            'y' : df['lang'].value_counts(),
                            'type' : 'bar'
                        }
                    ],
                    'layout' : {
                        'width' : 800,
                        'height' : 400, 
                        'template' : 'plotly_white', 
                        'xaxis' : {'title' : 'language'}, 
                        'yaxis' : {'title' : 'count'}
                    }
                }
            )
        ], style = {'width' : '48%', 'float' : 'left', 'text-indent' : '70px'}
        )
    ], style = {'display' : 'inline-block', 'text-indent' : '70px'}),

    # --------------------------------------------------------------------------------------------------------------------------


    html.Div([
        html.H2('Tweets per day', style = {'font-size' : '30px', 'color' : 'darkslategray'}),
        dcc.Graph(
            id = 'tweet-per-dat-plot',
            config = {'displayModeBar' : False},
            figure = {
                'data' : [
                    {
                        'x' : np.sort(df['created_at'].value_counts().index.values),
                        'y' : df['created_at'].value_counts().sort_index()

                    }
                ],
                'layout' : {
                    'xaxis' : {'title' : 'Date'},
                    'yaxis' : {'title' : 'count'}
                }
            }
        )
    ], style = {'display' : 'inline-block', 'text-indent' : '70px', 'width' : '100%'})


])

# Call backs 1 : Map / Figure
# ---------------------------------------------------------------------------------------------------------------------------------

@app.callback(
    Output('fig-map','figure'),
    [Input('lang-id','value')]
)

def update_map(lang_val):
    
    df_lang = df[df['lang'].isin(lang_val)]
    
    fig_map = go.Figure()
    fig_map.add_trace(
        go.Scattermapbox(
            lat = df_lang['lat'],
            lon = df_lang['lon'],
            mode = 'markers',
            marker = go.scattermapbox.Marker(size =8, color = 'indianred'),
            customdata = df['text']
        )
    )

    fig_map.update_layout(
        uirevision = 'foo',
        clickmode = 'event+select',
        hovermode = 'closest',
        hoverdistance = 1,
        mapbox = dict(
            accesstoken = mapbox_key,
            center = dict(lat = 14.00,lon = 120.99),
            pitch = 0,
            zoom = 7,
            style = 'light'
        ),
        #height = 750
    )
    return fig_map

# Call back 2 : Display click data
# ---------------------------------------------------------------------------------------------------------------------------------

@app.callback(
    Output('text-disp-id','children'),
    [Input('fig-map','clickData')]
)

def displayText(clickData):
    if clickData is None:
        return "Click on any Bubble"
    else:
        the_text = clickData['points'][0]['customdata']
        return the_text

# Callback 3 : WordCloud
# ---------------------------------------------------------------------------------------------------------------------------------

@app.callback(
    Output('word-cloud-id','src'),
    [Input('lang-id','value')]
)

def plot_word_cloud(lang_val):
    df_lang = df[df['lang'].isin(lang_val)]

    # CLean the tweets : remove http links
    cleaned_tweets = []
    for tweet in df_lang['text']:
        cleaned_tweets.append(re.sub(r"http\S+","",tweet))

    img = BytesIO()

    # Create word cloud
    longstring = ','.join(cleaned_tweets)
    wordcloud = WordCloud(stopwords = STOPWORDS,background_color='white',max_words=5000,contour_width=14, contour_color='steelblue', height = 350, width = 800)
    wordcloud.generate(longstring)
    wordcloud.to_image().save(img, format = 'PNG')
    

    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())



# Run Server
# _________________________________________________________________________________________________________________________________

app.run_server(debug = False)

"""
Notes :
mapbox styles : 
    white-bg
    "open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner" or "stamen-watercolor"
    "basic", "streets", "outdoors", "light", "dark", "satellite", or "satellite-streets"

    padding-left/right/bottom/top controls the indentation
"""
