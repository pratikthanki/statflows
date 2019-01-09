import os
import pandas as pd
import numpy as np
import pyodbc
import requests
import base64
import time
from sqlalchemy import create_engine

from flask import Flask
from flask_caching import Cache

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from Settings import *
from Queries import *


server = Flask(__name__)
app = dash.Dash(name='app1', sharing=True, server=server, csrf_protect=False)

# used for local development
# server = app.server


TIMEOUT = 60

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})


# Establish database connection to Write Records
def SQLServerConnection(config):
    conn_str = (
        'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}')

    conn = pyodbc.connect(
        conn_str.format(**config)
    )

    return conn


@cache.memoize(timeout=TIMEOUT)
def loadData(query):
    sqlData = []
    conn = SQLServerConnection(sqlconfig)

    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        pass
    except Exception as e:
        rows = pd.read_sql(query, conn)

    for row in rows:
        sqlData.append(list(row))

    df = pd.DataFrame(sqlData)

    return df


def parseTeams(df):
    teamdict = {}
    cols = df['TeamId'].unique()

    for team in cols:
        teamdict[team] = np.array(
            df.loc[df['TeamId'] == team, 'PlayerId'])

    teamdf = pd.DataFrame(dict([(k, pd.Series(v))
                                for k, v in teamdict.items()]))
    teamdf = teamdf.fillna('')

    return teamdf


headerstyle = {
    'align': 'center',
    'width': '300px',
    'background-color': '#0f6db5',
    'text-align': 'center',
    'font-size': '22px',
    'padding': '5px',
    'color': '#ffffff'}


tablestyle = {
    'display': 'table',
    'border-cllapse': 'separate',
    'font': '15px Open Sans, Arial, sans-serif',
    'font-weight': '30',
    'width': '100%'}


rowstyle = {
    'color': 'black',
    'align': 'center',
    'text-align': 'center',
    'font-size': '40px'}


tabs_styles = {
    'height': '50px', 
    'padding': '15px'
}


tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '10px',
    'font-size': '15px'
}


tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'fontWeight': 'bold',
    'color': 'white',
    'padding': '5px',
    'font-size': '22px'
}


ulstyle = {
    'list-style-type': 'none',
    'columnCount': '2',
    'columnWidth': '30px'
}


styleP = {
    'font-size': '12px',
    'text-align': 'center'
}

nbaLogo = 'http://www.performgroup.com/wp-content/uploads/2015/09/nba-logo-png.png'


def localImg(image):
    encoded_image = base64.b64encode(
        open(os.getcwd() + '/TeamLogos/' + image, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image)


latest_df = loadData(latestGame)
latest_df.columns = ['GameDate', 'GameDateFormatted', 'GameID', 'TeamID', 'OppositionTeamId', 'PlayerID', 'FullName', 'Num', 'Pos', 'Min', 'Ast', 'Blk', 'Blka',
                     'Dreb', 'Oreb', 'Reb', 'Fbpts', 'Fbptsa', 'Fbptsm', 'Fga', 'Fgm', 'Fta', 'Ftm', 'Pf', 'Pip', 'Pipa', 'Pipm', 'Pm', 'Pts', 'Stl', 'Tf', 'Tov', 'Tpa', 'Tpm']

latest_df = latest_df.where((pd.notnull(latest_df)), '')

teams = loadData(teams)
teams.columns = ['TeamID', 'TeamCode', 'TeamLogo']


standings = loadData(standings)
standings.columns = ['Conference', 'TeamId', 'Conf Record', 'Conf Rank', 'Streak', 'Win %', 'Last 10',
                     'Div Record', 'Div Rank', 'Home Wins', 'Home Losses', 'Home Streak', 'Road Wins', 'Road Losses', 'Road Streak']


def playerInfo(player):
    row = []
    rows = []
    cols = ['GameDate', 'OppositionTeamId',
            'Min', 'Pts', 'Ast', 'Blk', 'Reb', 'Stl']

    df = latest_df[latest_df['PlayerID'] == int(player)]  # 1628979

    for col in df.columns:
        if col in cols:
            if col == 'OppositionTeamId':
                oppImg = nbaLogo

                if df.iloc[0][col] == '':
                    oppImg = nbaLogo
                    style = {'height': '40px'}
                else:
                    try:
                        oppImg = teams.loc[teams['TeamID'] ==
                                           df.iloc[0][col], 'TeamLogo'].iloc[0]
                        style = {'height': '80px'}
                        pass
                    except IndexError as e:
                        print(e, df.iloc[0]['PlayerID'])

                value = html.Div(
                    html.Img(src=oppImg,
                             style=style)
                )
                row.append(value)

            elif col in ['Min', 'Pts', 'Ast', 'Blk', 'Reb', 'Stl']:
                value = col.upper() + ': ' + str(df.iloc[0][col])
                style = {'font-size': '12px'}
                row.append(html.P(value, style=style))

            else:
                value = df.iloc[0][col]
                style = {'font-size': '15px'}
                row.append(html.P(value, style=style))

    rows.append(html.Li(row))

    return html.Div(html.Ul(rows, style=ulstyle), className='text')


def playerCard(player):
    rows = []
    df = rosters[rosters['PlayerId'] == str(player)]
    df = df[['Height', 'Weight', 'Position', 'DoB',
             'Age', 'Experience', 'School']].copy()
    df = pd.DataFrame({'Metric': df.columns, 'Value': df.iloc[-1].values})

    for i in range(len(df)):
        row = []
        for col in df.columns:
            value = df.iloc[i][col]
            style = {'align': 'center', 'padding': '5px', 'color': 'white',
                     'border': 'white', 'text-align': 'center', 'font-size': '13px'}
            row.append(html.Td(value, style=style))

        rows.append(html.Tr(row))

    return html.Div(children=[
        html.Table(rows, style=tablestyle),
        html.Button('More Information', id='player-drilldown', style={'font-size': '10px', 'color': 'white', 'font-weight': 'bold'})
    ])


def teamCard(team):
    rows = []
    df = standings[standings['TeamId'] == str(team)]
    df = df[['Conference', 'Conf Record', 'Conf Rank', 'Streak',
             'Win %', 'Last 10', 'Div Record', 'Div Rank']].copy()
    df = pd.DataFrame({'Metric': df.columns, 'Value': df.iloc[-1].values})

    for i in range(len(df)):
        row = []
        for col in df.columns:
            value = df.iloc[i][col]
            style = {'align': 'center', 'padding': '3px', 'color': 'white',
                     'border': 'white', 'text-align': 'center', 'font-size': '11px'}
            row.append(html.Td(value, style=style))

        rows.append(html.Tr(row))

    return html.Div(children=[
        html.Table(rows, style=tablestyle),
        html.Button('More Information', id='player-drilldown', style={'font-size': '10px', 'color': 'white', 'font-weight': 'bold'})
    ])


def playerImage(player):
    if player != '':
        img = rosters.loc[rosters['PlayerId'] == player, 'PlayerImg'].iloc[0]
        name = rosters.loc[rosters['PlayerId'] == player, 'Player'].iloc[0]

        return html.Div(children=[
            html.Img(src=str(img), style={
                     'height': '140px', 'padding': '10px'}, className='image'),
            html.Div(html.H4(str(name),
                             style={'font-size': '20px',
                                    'text-align': 'center'})),
            html.Div(playerCard(player), className='overlay')],
            className='container', style={'width': '100%', 'height': '100%', 'position': 'relative'})


def getTeamImage(team):
    img = rosters.loc[rosters['TeamId'] == team, 'TeamLogo'].iloc[0]

    return html.Div(children=[
        html.Img(src=str(img), style={
            'height': '150px', 'padding': '15px'}),
        html.Div(teamCard(team), className='overlay')], 
        className='container', style={'width': '100%', 'height': '100%', 'position': 'relative'})


def get_data_object(df):
    rows = []
    for i in range(len(df)):
        row = []
        for col in df.columns:
            value = playerImage(df.iloc[i][col])
            style = {'align': 'center', 'padding': '5px',
                     'text-align': 'center', 'font-size': '25px'}
            row.append(html.Td(value, style=style))

            if i % 2 == 0 and 'background-color' not in style:
                style['background-color'] = '#f2f2f2'

        rows.append(html.Tr(row))

    return html.Table(
        [html.Tr([html.Th(getTeamImage(col), style=headerstyle) for col in df.columns])] + rows, style=tablestyle)


rosters = loadData(teamRosters)
rosters.columns = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                   'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']

teamdf = parseTeams(rosters)
get_data_object(teamdf)


def update_layout():
    return html.Div(children=[
        dcc.Tabs(id="div-tabs", value='Atlantic', children=[
            dcc.Tab(label='ATLANTIC', value='Atlantic',
                    style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='CENTRAL', value='Central', style=tab_style,
                    selected_style=tab_selected_style),
            dcc.Tab(label='SOUTHEAST', value='Southeast',
                    style=tab_style, selected_style=tab_selected_style),

            dcc.Tab(label='NORTHWEST', value='Northwest',
                    style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='PACIFIC', value='Pacific', style=tab_style,
                    selected_style=tab_selected_style),
            dcc.Tab(label='SOUTHWEST', value='Southwest',
                    style=tab_style, selected_style=tab_selected_style)], style=tabs_styles),

        html.Div(
            id='table-container'
        )

    ])


app.layout = update_layout()


@app.callback(
    Output('table-container', 'children'),
    [Input('div-tabs', 'value')])
def update_graph(value):
    rosters = loadData(teamRosters)
    rosters.columns = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                       'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']

    rosters = rosters[rosters['Division'] == value]
    teamdf = parseTeams(rosters)

    return get_data_object(teamdf)


external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css", "https://codepen.io/chriddyp/pen/brPBPO.css", "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"
]


for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
