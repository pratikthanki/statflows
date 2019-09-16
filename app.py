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
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go

from Settings import sqlconfig
from Queries import latestGame, teamRosters, teams, shotChart, standings
from Court import courtPlot


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


conn = SQLServerConnection(sqlconfig)


def loadData(query):
    sqlData = []

    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        pass
    except Exception as e:
        print(e)
        rows = pd.read_sql(query, conn)

    for row in rows:
        sqlData.append(list(row))

    df = pd.DataFrame(sqlData)

    return df


def getShots(player):
    if player:
        shot_Query = shotChart + ' ' + str(player)
        shot_Plot = loadData(shot_Query)
        shot_Plot.columns = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX',
                             'LocationY', 'Period', 'TeamID', 'PlayerID']

        return shot_Plot


headerstyle = {
    'align': 'center',
    'width': '300px',
    'background-color': '#0f6db5',
    'text-align': 'center',
    'font-size': '20px',
    'padding': '20px',
    'color': '#ffffff'}


tablestyle = {
    'display': 'table',
    'border-cllapse': 'separate',
    'font': '15px Open Sans, Arial, sans-serif',
    'font-weight': '30',
    'width': '100%'}


tabs_styles = {
    'height': '50px',
    'padding': '15px'}


tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '10px',
    'font-size': '15px'}


tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'fontWeight': 'bold',
    'color': 'white',
    'padding': '5px',
    'font-size': '22px'}


def playerCard(player):
    rows = []
    df = rosters[rosters['PlayerId'] == str(player)]

    if len(df) > 0:
        df = df[['Height', 'Weight', 'Position', 'DoB',
                'Age', 'Experience', 'School']].copy()
        df = pd.DataFrame({'Metric': df.columns, 'Value': df.iloc[-1].values})

    for i in range(len(df)):
        row = []
        for col in df.columns:
            value = df.iloc[i][col]
            style = {'align': 'center', 'padding': '5px', 'color': 'black',
                     'border': 'white', 'text-align': 'center', 'font-size': '11px'}
            row.append(html.Td(value, style=style))

        rows.append(html.Tr(row))

    # return html.Table(rows, style=tablestyle)

    return html.Div(children=[
        html.Table(rows, style=tablestyle),
        dcc.Link(html.Button('More Info', id='player-drilldown-'+str(player), style={
            'font-size': '10px', 'color': 'darkgrey', 'font-weight': 'bold', 'border': 'none'}), href='/' + str(player))
    ])


def parseTeams(df, teamId=None):
    if len(df.columns) == int(17):
        df.columns = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                      'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']

    if teamId is not None:
        df = df[df['TeamId'] == str(teamId)]
    else:
        df = df

    teamdict = {}
    cols = df['Position'].unique()

    for pos in cols:
        teamdict[pos] = np.array(
            df.loc[df['Position'] == pos, 'PlayerId'])

    teamdf = pd.DataFrame(dict([(k, pd.Series(v))
                                for k, v in teamdict.items()]))
    teamdf = teamdf.fillna('')

    return teamdf


def statstab(df, teamId=None):
    if len(df.columns) == int(17):
        df.columns = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                      'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']

    if teamId is not None:
        return df[df['TeamId'] == str(teamId)]
    else:
        return df


defaultimg = 'https://stats.nba.com/media/img/league/nba-headshot-fallback.png'

def playerImage(player):
    if player != '':
        img = rosters.loc[rosters['PlayerId'] == player, 'PlayerImg']
        img = img.iloc[0] if len(img) > 0 else defaultimg

        name = rosters.loc[rosters['PlayerId'] == player, 'Player']
        name = name.iloc[0] if len(name) > 0 else 'Name Missing'

        return html.Div(children=[
            html.Img(src=str(img), style={
                     'height': '130px'}, className='image'),
            html.Div(html.H4(str(name),
                             style={'font-size': '20px',
                                    'text-align': 'center'})),
            html.Div(playerCard(player), className='overlay')],
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
        [html.Tr([html.Th(col, style=headerstyle) for col in df.columns])] + rows, style=tablestyle)


def buildTable(df):
    rows = []
    if df is not None:
        for i in range(len(df)):
            row = []
            for col in df.columns:
                value = df.iloc[i][col]
                style = {'align': 'center', 'padding': '5px',
                         'text-align': 'center', 'font-size': '12px'}
                row.append(html.Td(value, style=style))

                if i % 2 == 0 and 'background-color' not in style:
                    style['background-color'] = '#f2f2f2'

            rows.append(html.Tr(row))

        return html.Table(
            [html.Tr([html.Th(col, style=headerstyle) for col in df.columns])] + rows, style=tablestyle)


rosters = loadData(teamRosters)
teamdf = parseTeams(rosters)

teams = loadData(teams)
teams.columns = ['TeamID', 'TeamCode', 'TeamLogo']


event_definitions = [
    {'EType': '0', 'Event': 'Game End'},
    {'EType': '1', 'Event': 'Shot Made'},
    {'EType': '2', 'Event': 'Shot Missed'},
    {'EType': '3', 'Event': 'Free Throw'},
    {'EType': '4', 'Event': 'Rebound'},
    {'EType': '5', 'Event': 'Turnover'},
    {'EType': '6', 'Event': 'Foul'},
    {'EType': '7', 'Event': 'Violation'},
    {'EType': '8', 'Event': 'Substitution'},
    {'EType': '9', 'Event': 'Timeout'},
    {'EType': '10', 'Event': 'Jump Ball'},
    {'EType': '11', 'Event': 'Ejection'},
    {'EType': '12', 'Event': 'Start Period'},
    {'EType': '13', 'Event': 'End Period'},
    {'EType': '18', 'Event': 'Instant Replay'},
    {'EType': '20', 'Event': 'Stoppage: Out-of-Bounds'}
]


nbaLogo = 'http://www.performgroup.com/wp-content/uploads/2015/09/nba-logo-png.png'


def createShotPlot(data):
    if data is not None:
        return html.Div(
            dcc.Graph(
                id='shot-plot',
                figure={
                    'data': [
                        go.Scatter(
                            x=data[data['EType']
                                == 1]['LocationX'],
                            y=data[data['EType']
                                == 1]['LocationY'],
                            mode='markers',
                            name='Made Shot',
                            opacity=0.7,
                            marker=dict(
                                size=5,
                                color='rgba(0, 200, 100, .8)',
                                line=dict(
                                    width=1,
                                    color='rgb(0, 0, 0, 1)'
                                )
                            )
                        ),
                        go.Scatter(
                            x=data[data['EType']
                                == 2]['LocationX'],
                            y=data[data['EType']
                                == 2]['LocationY'],
                            mode='markers',
                            name='Missed Shot',
                            opacity=0.7,
                            marker=dict(
                                size=5,
                                color='rgba(255, 255, 0, .8)',
                                line=dict(
                                    width=1,
                                    color='rgb(0, 0, 0, 1)'
                                )
                            )
                        )
                    ],
                    'layout': go.Layout(
                        title='Made & Missed Shots',
                        showlegend=True,
                        xaxis=dict(
                            showgrid=False,
                            range=[-300, 300]
                        ),
                        yaxis=dict(
                            showgrid=False,
                            range=[-100, 500]
                        ),
                        height=600,
                        width=650,
                        shapes=courtPlot()
                    )
                }
            )
        )


def update_layout():

    return html.Div(children=[
        dcc.Location(id='teamurl', refresh=False),
        html.Div(
            [dcc.Link(
                html.Img(src=teams.loc[teams['TeamID'] == i, 'TeamLogo'].iloc[0], style={'height': '92px'},
                         className='team-overlay', id='team-logo-'+str(i)), href='/' + str(i))
             for i in teams['TeamID'].values if i is not None]),


        dcc.Tabs(id="div-tabs", value='Current Roster', children=[
                    dcc.Tab(label='ROSTER', value='Current Roster',
                            style=tab_style, selected_style=tab_selected_style),
                    dcc.Tab(label='RESULTS', value='Results', style=tab_style,
                            selected_style=tab_selected_style),
                    dcc.Tab(label='STATS', value='Stats',
                            style=tab_style, selected_style=tab_selected_style),
                    dcc.Tab(label='SHOTS', value='Shots',
                            style=tab_style, selected_style=tab_selected_style)], style=tabs_styles),

        html.Div(
            get_data_object(teamdf), id='tableContainer'
            ),

        html.Div(
            createShotPlot(getShots(None)), id='shotplot', style={'float': 'right'}
            )

    ])


app.layout=update_layout()

app.config['suppress_callback_exceptions']=True


@app.callback(
    Output('tableContainer', 'children'),
    [Input('teamurl', 'pathname'),
     Input('div-tabs', 'value')]
)
def updateTeamTable(pathname, value):
    print(pathname.split('/'))
    teamId = int(pathname.split('/')[-1]) if pathname is not u'/' else None

    if value == 'Current Roster':
        teamdf = parseTeams(rosters, teamId)
        return get_data_object(teamdf)

    elif value == 'Results':
        return html.P('Results')

    elif value == 'Stats':
        df = statstab(rosters, teamId)
        df = df[['Player', 'JerseyNumber', 'Position', 'Height', 'Weight', 'DoB', 'Age', 'Experience', 'School']].copy()
        return buildTable(df)

    elif value == 'Shots':
        return html.P('Shots')


@app.callback(
    Output('shotplot', 'figure'),
    [Input('teamurl', 'pathname')]
)
def updateShotPlot(pathname):
    print(pathname.split('/'))
    if pathname is not u'/' or pathname is not None:
        playerId = int(float(pathname.split('/')[-1]))
        playerdf = getShots(playerId)

    return get_data_object(playerdf)


# @app.callback(
#     Output('shot-plot', 'figure'))
# def update_shotPlot():
#     return update_layout()


external_css=[
    "https://codepen.io/chriddyp/pen/bWLwgP.css", 
    "https://codepen.io/chriddyp/pen/brPBPO.css", 
    "https://codepen.io/chriddyp/pen/dZVMbK.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True)
