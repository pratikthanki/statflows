import os
import pandas as pd
import numpy as np
import pyodbc
import requests
import base64
from sqlalchemy import create_engine

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from Settings import *
from Queries import *


app = dash.Dash()
server = app.server
app.scripts.config.serve_locally = True
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'

app.head = [
    ('''

    <style type="text/css">

    .overlay {
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        height: 100%;
        width: 100%;
        opacity: 0;
        transition: .5s ease;
        background-color: #0f6db5;
    }

    .container:hover .overlay {
        opacity: .9;
    }

    .text {
        color: white;
        font-size: 20px;
        position: absolute;
        top: 50%;
        left: 50%;
        -webkit-transform: translate(-50%, -50%);
        -ms-transform: translate(-50%, -50%);
        transform: translate(-50%, -50%);
        text-align: center;
    }
     </style>

    ''')
]

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
    'border-collapse': 'separate'}

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
    'column-width': '40px'
}

styleP = {
    'font-size': '10px',
    'text-align': 'center'
}

overlay_style = {
    # 'position': 'absolute',
    # 'top': '0',
    # 'bottom': '0',
    # 'left': '0',
    # 'right': '0',
    # 'height': '100%',
    # 'width': '100%',
    # 'opacity': '0',
    # 'transition': '.5s ease',
    # 'background-color': '#0f6db5'
}


def localImg(image):
    encoded_image = base64.b64encode(
        open(os.getcwd() + '/TeamLogos/' + image, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image)


latest_df = loadData(latestGame)
latest_df.columns = ['LatestDate', 'Venue', 'TeamID', 'PlayerID', 'FullName', 'JerseyNum', 'Pos', 'Min',
                     'Pts', 'Ast', 'Blk', 'Reb', 'Fga', 'Fgm', 'Fta', 'Ftm', 'Stl', 'Tov', 'Pf', 'Pip', 'Pipa', 'Pipm']

latest_df['FG%'] = (latest_df['Fgm'] / latest_df['Fga']) * 100
latest_df['FT%'] = (latest_df['Ftm'] / latest_df['Fta']) * 100
latest_df['Pip%'] = (latest_df['Pipm'] / latest_df['Pipa']) * 100


def playerInfo(player):
    row = []
    cols = ['LatestDate', 'Min', 'Pts', 'Ast',
            'Blk', 'Reb', 'Stl', 'FG%', 'FT%', 'Pip%']

    df = latest_df.loc[latest_df['PlayerID'] == int(player)]

    for col in df.columns:
        if any(col in c for c in cols) and col != 'Pip':
            text = col + ': ' + str(df.iloc[0][col])
            P = html.P(text, style=styleP)
            row.append(html.Li(P))

    return html.Div(html.Ul(row, style=ulstyle), className='text')


def getPlayerImage(player):
    if player != '':
        img = teams.loc[teams['PlayerId'] == player, 'PlayerImg'].iloc[0]
        name = teams.loc[teams['PlayerId'] == player, 'FullName'].iloc[0]

        return html.Div(children=[
            html.Img(src=str(img), style={
                     'height': '100px'}, className='image'),
            html.Div(html.H4(str(name),
                             style={'font-size': '20px',
                                    'text-align': 'center'})),
            html.Div(playerInfo(player), className='overlay', style=overlay_style)],
            className='container', style={'width': '100%', 'position': 'relative'})


def getTeamImage(team):
    img = teams.loc[teams['TeamId'] == team, 'TeamLogo'].iloc[0]

    return html.Div(children=[
        html.Img(src=str(img), style={'height': '90px'})
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
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://codepen.io/chriddyp/pen/brPBPO.css",
    "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"
]

for css in external_css:
    app.css.append_css({"external_url": css})


if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


if __name__ == '__main__':
    app.run_server(debug=True)
