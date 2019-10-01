import pandas as pd
import numpy as np
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

from Settings import sqlconfig, SQLServerConnection
from Queries import latestGame, teamRosters, teams, shotChart, standings
from Court import courtPlot


server = Flask(__name__)
app = dash.Dash(name='app1', sharing=True, server=server, csrf_protect=False)


def load_data(query):
    sqlData = []
    conn = SQLServerConnection(sqlconfig)

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


def get_shots(player):
    if player:
        shot_Query = shotChart + str(player)
        shot_Plot = load_data(shot_Query)
        shot_Plot.columns = ['ClockTime', 'Description', 'EType', 'Evt', 'LocationX',
                             'LocationY', 'Period', 'TeamID', 'PlayerID']

        return shot_Plot


HEADER_STYLE = {
    'align': 'center',
    'width': '300px',
    'background-color': '#0f6db5',
    'text-align': 'center',
    'font-size': '20px',
    'padding': '20px',
    'color': '#ffffff'}


TABLE_STYLE = {
    'display': 'table',
    'border-cllapse': 'separate',
    'font': '15px Open Sans, Arial, sans-serif',
    'font-weight': '30',
    'width': '100%'}


ALL_TAB_STYLE = {
    'height': '50px',
    'padding': '15px'}


SINGLE_TAB_STYLE = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '10px',
    'font-size': '15px'}


SELECTED_TAB_STYLE = {
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

    return html.Div(children=[
        html.Table(rows, style=TABLE_STYLE),
        dcc.Link(html.Button('More Info', id='player-drilldown-'+str(player), style={
            'font-size': '10px', 'color': 'darkgrey', 'font-weight': 'bold', 'border': 'none'}), href='/player/' + str(player))
    ])


def parseTeams(df, teamId=None):
    if len(df.columns) == int(17):
        df.columns = ['TeamId', 'Season', 'LeagueId', 'Player', 'JerseyNumber', 'Position', 'Height', 'Weight',
                      'DoB', 'Age', 'Experience', 'School', 'PlayerId', 'TeamLogo', 'PlayerImg', 'Division', 'Conference']

    if teamId is not None:
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


def buildTable(df, table_setting='Summary'):
    rows = []
    if df is not None:
        for i in range(len(df)):
            row = []
            for col in df.columns:
                value = df.iloc[i][col] if table_setting != 'Summary' else playerImage(
                    df.iloc[i][col])
                style = {'align': 'center', 'padding': '5px',
                         'text-align': 'center', 'font-size': '12px'}
                row.append(html.Td(value, style=style))

                if i % 2 == 0 and 'background-color' not in style:
                    style['background-color'] = '#f2f2f2'

            rows.append(html.Tr(row))

        return html.Table(
            [html.Tr([html.Th(col, style=HEADER_STYLE) for col in df.columns])] + rows, style=TABLE_STYLE)


rosters = load_data(teamRosters)
teamdf = parseTeams(rosters)

teams = load_data(teams)
teams.columns = ['TeamID', 'TeamCode', 'TeamLogo']


event_definitions = {
    '0': 'Game End',
    '1': 'Shot Made',
    '2': 'Shot Missed',
    '3': 'Free Throw',
    '4': 'Rebound',
    '5': 'Turnover',
    '6': 'Foul',
    '7': 'Violation',
    '8': 'Substitution',
    '9': 'Timeout',
    '10': 'Jump Ball',
    '11': 'Ejection',
    '12': 'Start Period',
    '13': 'End Period',
    '18': 'Instant Replay',
    '20': 'Stoppage: Out-of-Bounds'}


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
                         className='team-overlay', id='team-logo-'+str(i)), href='/team/' + str(i))
             for i in teams['TeamID'].values if i is not None]),


        dcc.Tabs(id="div-tabs", value='Current Roster', children=[
                    dcc.Tab(label='ROSTER', value='Current Roster',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                    dcc.Tab(label='RESULTS', value='Results',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                    dcc.Tab(label='STATS', value='Stats',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                    dcc.Tab(label='SHOTS', value='Shots',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE)],
                 style=ALL_TAB_STYLE),

        html.Div(
            html.P('Select a team to get started', style={'align': 'center'}),
            id='tableContainer'),

        html.Div(
            id='shotplot')

    ])


app.layout = update_layout()

app.config['suppress_callback_exceptions'] = True


@app.callback(
    Output('tableContainer', 'children'),
    [Input('teamurl', 'pathname'),
     Input('div-tabs', 'value')])
def updateTeamTable(pathname, value):
    if pathname:
        teamId = pathname.split('/')[-1]
    else:
        return html.P('Select a team to get started')

    if value == 'Current Roster':
        teamdf = parseTeams(rosters, teamId)
        return buildTable(teamdf, 'Summary')

    elif value == 'Results':
        return html.P('Results')

    elif value == 'Stats':
        df = statstab(rosters, teamId)
        df = df[['Player', 'JerseyNumber', 'Position', 'Height',
                 'Weight', 'DoB', 'Age', 'Experience', 'School']].copy()
        return buildTable(df, 'Stats')

    elif value == 'Shots':
        return html.P('Shots')


@app.callback(
    Output('shotplot', 'figure'),
    [Input('teamurl', 'pathname')]
)
def updateShotPlot(pathname):
    if pathname:
        if pathname.split('/')[1] == u'player':
            playerId = pathname.split('/')[-1]
        else:
            return html.P('SELECT A TEAM ABOVE TO GET STARTED', style={'float': 'center'})

        playerdf = get_shots(playerId)

        return createShotPlot(playerdf)


external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://codepen.io/chriddyp/pen/brPBPO.css",
    "https://codepen.io/chriddyp/pen/dZVMbK.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True)
