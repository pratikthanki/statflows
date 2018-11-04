import os
import pandas as pd
import numpy as np
import pyodbc
import time
from datetime import datetime, timedelta
import colorlover as cl
import requests
import base64
from sqlalchemy import create_engine

import plotly
import plotly.graph_objs as go

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from Settings import *

pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 500)


app = dash.Dash()
server = app.server
app.scripts.config.serve_locally = True
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'
colorscale = cl.scales['9']['qual']['Paired']


# Establish database connection to Write Records
def SQLServerConnection(config):
    conn_str = (
        'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}')

    conn = pyodbc.connect(
        conn_str.format(**config)
    )

    return conn


def loadData(query):
    sqlData = []
    conn = SQLServerConnection(sqlconfig)

    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        sqlData.append(list(row))

    df = pd.DataFrame(sqlData)

    return df


teamsQuery = '''
SELECT DISTINCT
CAST(t.PlayerID as varchar)
,CAST(t.TeamID as varchar)
,t.TeamCode
,t.FirstName
,t.LastName
,t.FullName
,t.TeamLogo
,'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/'+CAST(t.TeamID as varchar)+'/2018/260x190/'+CAST(t.PlayerID as varchar)+'.png' as PlayerImg

FROM (

SELECT
      PlayerGameSummary.[GameID]
      ,PlayerGameSummary.[PlayerID]
      ,Players.FirstName
      ,Players.LastName
      ,Players.FirstName + ' ' + Players.LastName as FullName
      ,PlayerGameSummary.[TeamID]
      ,PlayerLogo
      ,Games.Date
      ,TeamCode
      ,TeamLogo
  FROM [dbo].[PlayerGameSummary]

  JOIN Games ON Games.GameID = PlayerGameSummary.GameID
  JOIN Teams ON Teams.TeamID = PlayerGameSummary.TeamID
  JOIN Players ON Players.PlayerID = PlayerGameSummary.PlayerID

WHERE GAMES.DATE > '2018-09-01' ) t

WHERE t.TeamLogo != ''

ORDER BY t.TeamCode
'''

teams = loadData(teamsQuery)
teams.columns = ['PlayerId', 'TeamId', 'TeamCode',
                 'FirstName', 'LastName', 'FullName', 'TeamLogo', 'PlayerImg']


def parseTeams():
    teamdict = {}
    cols = teams['TeamId'].unique()

    for team in cols:
        teamdict[team] = np.array(
            teams.loc[teams['TeamId'] == team, 'PlayerId'])

    teamdf = pd.DataFrame(dict([(k, pd.Series(v))
                                for k, v in teamdict.items()]))
    teamdf = teamdf.fillna('')

    return teamdf


COLORS = [
    {'background': '#42a059', 'text': 'seagreen'},
    {'background': '#febe2c', 'text': 'goldenrod'},
    {'background': '#e32931', 'text': 'crimson'},
    {'background': '#4990e7', 'text': 'cornflowerblue'},
    {'background': '#d9d9d9', 'text': 'gainsboro'}]


headerstyle = {'align': 'center',
               'width': '300px',
               'background-color': '#0f6db5',
               'text-align': 'center',
               'font-size': '22px',
               'padding': '10px',
               'color': '#ffffff'}

tablestyle = {'display': 'table',
              'border-cllapse': 'separate',
              'font': '15px Open Sans, Arial, sans-serif',
              'font-weight': '30',
              'border-collapse': 'separate'}

rowstyle = {'color': 'black',
            'align': 'center',
            'text-align': 'center',
            'font-size': '40px'}


def localImg(image):
    encoded_image = base64.b64encode(
        open(os.getcwd() + '/TeamLogos/' + image, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image)


teams.loc[teams['PlayerId'] == '1626147', 'PlayerImg'].iloc[0]
teams.loc[teams['TeamId'] == '1610612737', 'TeamLogo'].iloc[0]


def getPlayerImage(player):
    if player != '':
        img = teams.loc[teams['PlayerId'] == player, 'PlayerImg'].iloc[0]
        name = teams.loc[teams['PlayerId'] == player, 'FullName'].iloc[0]

        return html.Div(children=[
            html.Img(src=str(img), style={'height': '120px'}),
            html.Div(html.H4(str(name),
                             style={'font-size': '20px',
                                    'text-align': 'center'}))
        ])


def getTeamImage(team):
    img = teams.loc[teams['TeamId'] == team, 'TeamLogo'].iloc[0]

    return html.Div(children=[
        html.Img(src=str(img), style={'height': '70px'})
    ])


def get_data_object(df):
    rows = []
    for i in range(len(df)):
        row = []
        for col in df.columns:
            value = getPlayerImage(df.iloc[i][col])
            style = {'align': 'center', 'padding': '7px',
                     'text-align': 'center', 'font-size': '25px'}
            row.append(html.Td(value, style=style))

            if i % 2 == 0 and 'background-color' not in style:
                style['background-color'] = '#f2f2f2'

        rows.append(html.Tr(row))

    return html.Table(
        [html.Tr([html.Th(getTeamImage(col), style=headerstyle) for col in df.columns])] + rows, style=tablestyle)


Atlantic = ['BOS', 'BKN', 'NYK', 'PHI', 'TOR']
Central = ['CHI', 'CLE', 'DET', 'IND', 'MIL']
Southeast = ['ATL', 'CHA', 'MIA', 'ORL', 'WAS']
Northwest = ['DEN', 'MIN', 'OKC', 'POR', 'UTA']
Pacific = ['GSW', 'LAC', 'LAL', 'PHX', 'SAC']
Southwest = ['DAL', 'HO', 'MEM', 'NOP', 'SAS']

teamdf = parseTeams()
get_data_object(teamdf)


def update_layout():
    return html.Div(children=[
        html.Div([
            html.Img(src=localImg('nba.png'),
                     style={
                         'height': '145px',
                         'float': 'left'},
                     ),
        ]),

        html.H1("NBA League Analysis",
                style={'text-align': 'center',
                       'padding': '10px'}),

        html.P('This is some text', style={'text-align': 'center',
                                           'padding': '10px'}),

        dcc.Tabs(id="conf-tabs", value='Atlantic', children=[
            dcc.Tab(label='ATLANTIC', value='Atlantic'),
            dcc.Tab(label='CENTRAL', value='Central'),
            dcc.Tab(label='SOUTHEAST', value='Southeast'),

            dcc.Tab(label='NORTHWEST', value='Northwest'),
            dcc.Tab(label='PACIFIC', value='Pacific'),
            dcc.Tab(label='SOUTHWEST', value='Southwest'),
        ]),

        # html.Button('Refresh Dashboard', id='my-button'),

        html.Div(
            id='table-container'
        )

    ])


app.layout = update_layout()


@app.callback(
    Output('table-container', 'children'),
    [Input('conf-tabs', 'value')])

def update_graph(value):
    teams = loadData(teamsQuery)
    teams.columns = ['PlayerId', 'TeamId', 'TeamCode',
                     'FirstName', 'LastName', 'FullName', 'TeamLogo', 'PlayerImg']

    teamdf = parseTeams()

    return get_data_object(teamdf)


external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://codepen.io/chriddyp/pen/brPBPO.css",
    "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]

for css in external_css:
    app.css.append_css({"external_url": css})


if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


if __name__ == '__main__':
    app.run_server(debug=True)
