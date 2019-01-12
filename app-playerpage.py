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
import plotly.graph_objs as go

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


conn = SQLServerConnection(sqlconfig)


@cache.memoize(timeout=TIMEOUT)
def loadData(query):
    sqlData = []

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


@cache.memoize(timeout=TIMEOUT)
def getShots(player):
    if player:
        shot_Query = shotChart + ' %s'
        shot_Query = shot_Query.format(player)

    else:
        shot_Query = shotChart.replace('SELECT', 'SELECT TOP 1000')

    shot_Plot = loadData(shot_Query)
    shot_Plot.columns = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX',
                         'LocationY', 'Period', 'TeamID', 'PlayerID']

    return shot_Plot


headerstyle = {
    'align': 'center',
    'width': '300px',
    'background-color': '#464646',
    'text-align': 'center',
    'font-size': '25px',
    'padding': '10px',
    'color': '#ffffff'}


tablestyle = {
    'display': 'table',
    'border-cllapse': 'separate',
    'font': '15px Open Sans, Arial, sans-serif',
    'font-weight': '30',
    'width': '100%'}


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

    return html.Table(rows, style=tablestyle)


def parseTeams(df, teamId):
    df = df[df['TeamId'] == str(teamId)]

    teamdict = {}
    cols = df['Position'].unique()

    for pos in cols:
        teamdict[pos] = np.array(
            df.loc[df['Position'] == pos, 'PlayerId'])

    teamdf = pd.DataFrame(dict([(k, pd.Series(v))
                                for k, v in teamdict.items()]))
    teamdf = teamdf.fillna('')

    return teamdf


def playerImage(player):
    if player != '':
        img = rosters.loc[rosters['PlayerId'] == player, 'PlayerImg'].iloc[0]
        name = rosters.loc[rosters['PlayerId'] == player, 'Player'].iloc[0]

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


rosters = loadData(teamRosters)
rosters.columns = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                   'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']

teamdf = parseTeams(rosters, '1610612738')
get_data_object(teamdf)

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

# ---------- list containing all the shapes ----------
# ---------- OUTER LINES ----------
court_shapes = []

outer_lines_shape = dict(
    type='rect',
    xref='x',
    yref='y',
    x0='-250',
    y0='-47.5',
    x1='250',
    y1='422.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(outer_lines_shape)

# ---------- BASKETBALL HOOP ----------
hoop_shape = dict(
    type='circle',
    xref='x',
    yref='y',
    x0='7.5',
    y0='7.5',
    x1='-7.5',
    y1='-7.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(hoop_shape)

# ---------- BASKET BACKBOARD ----------
backboard_shape = dict(
    type='rect',
    xref='x',
    yref='y',
    x0='-30',
    y0='-7.5',
    x1='30',
    y1='-6.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    ),
    fillcolor='rgba(10, 10, 10, 1)'
)

court_shapes.append(backboard_shape)

# ---------- OUTER BOX OF THREE-SECOND AREA ----------
outer_three_sec_shape = dict(
    type='rect',
    xref='x',
    yref='y',
    x0='-80',
    y0='-47.5',
    x1='80',
    y1='143.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(outer_three_sec_shape)

# ---------- INNER BOX OF THREE-SECOND AREA ----------
inner_three_sec_shape = dict(
    type='rect',
    xref='x',
    yref='y',
    x0='-60',
    y0='-47.5',
    x1='60',
    y1='143.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(inner_three_sec_shape)

# ---------- THREE-POINT LINE (LEFT) ----------
left_line_shape = dict(
    type='line',
    xref='x',
    yref='y',
    x0='-220',
    y0='-47.5',
    x1='-220',
    y1='92.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(left_line_shape)

# ---------- THREE-POINT LINE (RIGHT) ----------
right_line_shape = dict(
    type='line',
    xref='x',
    yref='y',
    x0='220',
    y0='-47.5',
    x1='220',
    y1='92.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(right_line_shape)

# ---------- THREE-POINT ARC ----------
three_point_arc_shape = dict(
    type='path',
    xref='x',
    yref='y',
    path='M -220 92.5 C -70 300, 70 300, 220 92.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(three_point_arc_shape)

# ---------- CENTER CIRCLE ----------
center_circle_shape = dict(
    type='circle',
    xref='x',
    yref='y',
    x0='60',
    y0='482.5',
    x1='-60',
    y1='362.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(center_circle_shape)

# ---------- RESTRAINING CIRCE ----------
res_circle_shape = dict(
    type='circle',
    xref='x',
    yref='y',
    x0='20',
    y0='442.5',
    x1='-20',
    y1='402.5',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(res_circle_shape)

# ---------- FREE-THROW CIRCLE ----------
free_throw_circle_shape = dict(
    type='circle',
    xref='x',
    yref='y',
    x0='60',
    y0='200',
    x1='-60',
    y1='80',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1
    )
)

court_shapes.append(free_throw_circle_shape)


# ---------- RESTRICTED AREA ----------
res_area_shape = dict(
    type='circle',
    xref='x',
    yref='y',
    x0='40',
    y0='40',
    x1='-40',
    y1='-40',
    line=dict(
        color='rgba(10, 10, 10, 1)',
        width=1,
        dash='dot'
    )
)

court_shapes.append(res_area_shape)


nbaLogo = 'http://www.performgroup.com/wp-content/uploads/2015/09/nba-logo-png.png'


def update_layout():
    data = getShots(None)

    return html.Div(children=[
        html.Div(
            html.Div(
                html.A(
                    [html.Img(src=i, style={'height': '92px'}, className='team-overlay')
                     for i in teams['TeamLogo'].values if i is not None], style={'padding': '10px'},)
            ), className='team-container'),

        html.Div(id="placeholder"),

        html.Div(
            id='tableContainer',
        ),

        html.Div(
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
                        shapes=court_shapes
                    )
                }
            ), style={'float': 'right'})
    ])


app.layout = update_layout()


@app.callback(
    Output('tableContainer', 'children'),
    [Input('placeholder', 'n_clicks')])
def update_graph(value):
    # teamId = teams.loc[teams['TeamLogo'] == value, 'TeamID'].iloc[0]
    rosters = loadData(teamRosters)
    rosters.columns = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                       'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']
    teamdf = parseTeams(rosters, '1610612752')
    return get_data_object(teamdf)


@app.callback(
    Output('shot-plot', 'figure'))
def update_shotPlot():
    return update_layout()


external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css", "https://codepen.io/chriddyp/pen/brPBPO.css", "https://codepen.io/chriddyp/pen/dZVMbK.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True)
