import os
import pandas as pd
import numpy as np
import pyodbc
import requests
import base64
import time
from sqlalchemy import create_engine
from flask import Flask
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


COLORS = [
    {'background': '#42a059', 'text': 'seagreen'},
    {'background': '#febe2c', 'text': 'goldenrod'},
    {'background': '#e32931', 'text': 'crimson'},
    {'background': '#4990e7', 'text': 'cornflowerblue'},
    {'background': '#d9d9d9', 'text': 'gainsboro'}]


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
    'border-collapse': 'separate',
    'width': '100%'}


rowstyle = {
    'color': 'black',
    'align': 'center',
    'text-align': 'center',
    'font-size': '40px'}


tabs_styles = {
    'height': '50px'
}


tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '5px',
    'font-size': '18px'
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


def localImg(image):
    encoded_image = base64.b64encode(
        open(os.getcwd() + '/TeamLogos/' + image, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image)


latest_df = loadData(latestGame)
latest_df.columns = ['LatestDate', 'GameDate', 'TeamID', 'OppositionId', 'OppositionTeamCode', 'OppositionTeamLogo', 'PlayerID', 'FullName', 'FullNamePos',
                     'Num', 'Pos', 'Min', 'Pts', 'Ast', 'Blk', 'Reb', 'Fga', 'Fgm', 'Fta', 'Ftm', 'Stl', 'Tov', 'Pf', 'Pip', 'Pipa', 'Pipm']


def playerInfo(player):
    row = []
    rows = []
    cols = ['GameDate', 'OppositionTeamLogo', 'FullNamePos',
            'Min', 'Pts', 'Ast', 'Blk', 'Reb', 'Stl']

    df = latest_df[latest_df['PlayerID'] == int(player)]
    df = df.head(1)

    for col in df.columns:
        if col in cols:
            if col == 'OppositionTeamLogo':
                value = html.Div(
                    html.Img(src=str(df.iloc[0][col]),
                             style={'height': '70px'})
                )
                row.append(value)

            elif col in ['Pos', 'Min', 'Pts', 'Ast', 'Blk', 'Reb', 'Stl']:
                value = col + ': ' + str(df.iloc[0][col])
                style = {'font-size': '12px'}
                row.append(html.P(value, style=style))

            else:
                value = df.iloc[0][col]
                style = {'font-size': '15px'}
                row.append(html.P(value, style=style))

    rows.append(html.Li(row))

    return html.Div(html.Ul(rows, style=ulstyle), className='text')


def playerImage(player):
    if player != '':
        img = teams.loc[teams['PlayerId'] == player, 'PlayerImg'].iloc[0]
        name = teams.loc[teams['PlayerId'] == player, 'FullName'].iloc[0]

        return html.Div(children=[
            html.Img(src=str(img), style={
                     'height': '130px'}, className='image'),
            html.Div(html.H4(str(name),
                             style={'font-size': '20px',
                                    'text-align': 'center'})),
            html.Div(playerInfo(player), className='overlay')],
            className='container', style={'width': '100%', 'height': '100%', 'position': 'relative'})


def getTeamImage(team):
    img = teams.loc[teams['TeamId'] == team, 'TeamLogo'].iloc[0]

    return html.Div(children=[
        html.Img(src=str(img), style={'height': '100px'})
    ])


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


# Atlantic = ['BOS', 'BKN', 'NYK', 'PHI', 'TOR']
# Central = ['CHI', 'CLE', 'DET', 'IND', 'MIL']
# Southeast = ['ATL', 'CHA', 'MIA', 'ORL', 'WAS']
# Northwest = ['DEN', 'MIN', 'OKC', 'POR', 'UTA']
# Pacific = ['GSW', 'LAC', 'LAL', 'PHX', 'SAC']
# Southwest = ['DAL', 'HO', 'MEM', 'NOP', 'SAS']

teams = loadData(teamRosters)
teams.columns = ['PlayerId', 'TeamId', 'TeamCode', 'FirstName', 'LastName',
                 'FullName', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']
teamdf = parseTeams(teams)
get_data_object(teamdf)


def update_layout():
    return html.Div(children=[
        html.Div([
            html.Img(src='http://www.performgroup.com/wp-content/uploads/2015/09/nba-logo-png.png',
                     style={
                         'height': '120px',
                         'float': 'left'},
                     ),
        ]),

        html.P('Latest match stats from teams across the league. Click on a division or hover over a player to see their latest stats', style={'text-align': 'center',
                                                                                                                                               'padding': '10px'}),

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
                    style=tab_style, selected_style=tab_selected_style),
        ], style=tabs_styles),

        # html.Button('Refresh Dashboard', id='my-button'),

        html.Div(
            id='table-container'
        )

    ])


app.layout = update_layout()


@app.callback(
    Output('table-container', 'children'),
    [Input('div-tabs', 'value')])
def update_graph(value):
    teams = loadData(teamRosters)
    teams.columns = ['PlayerId', 'TeamId', 'TeamCode', 'FirstName', 'LastName',
                     'FullName', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']
    teams = teams[teams['Division'] == value]
    teamdf = parseTeams(teams)

    return get_data_object(teamdf)


external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css"
    ,"https://codepen.io/chriddyp/pen/brPBPO.css"
    ,"https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"
]


for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
