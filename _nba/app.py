import os
import pandas as pd
import numpy as np
import statistics

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from flask import Flask

from teams import TEAMS
from court import court_plot
from shared_config import authorized_app_emails
from shared_modules import SqlConnection

from app_styles import DEFAULT_IMAGE, HEADER_STYLE, TABLE_STYLE, SELECTED_TAB_STYLE, \
    SINGLE_TAB_STYLE, ALL_TAB_STYLE, EVENT_DEFINITIONS
from sql_queries import team_roster_query, team_query, shot_chart_query, team_season_stats_query, \
    SHOT_PLOT_COLUMNS, TEAM_COLUMNS, TEAM_STATS_COLUMNS, CURRENT_ROSTER_COLUMNS

server = Flask(__name__)

app = dash.Dash(
    name='nba_app',
    server=server,
    url_base_pathname='/',
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
    suppress_callback_exceptions=True)

sql = SqlConnection('NBA')


# server.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
# server.config["GOOGLE_OAUTH_CLIENT_ID"] = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
# server.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
#
# # one of the Redirect URIs from Google APIs console
# REDIRECT_URI = '/oauth2callback'
#
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# auth = GoogleOAuth(
#     app,
#     authorized_app_emails,
# )


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-logo",
                children=[
                    html.Img(id="logo", src=app.get_asset_url("logo-white.png"),
                             style={'height': '100px', 'float': 'right'}),
                ],
            ),
        ],
    )


def get_shots(player, period, venue):
    if player:
        shot_query = shot_chart_query.format(player, period, venue)
        shot_plot = sql.load_data(shot_query, SHOT_PLOT_COLUMNS)

        return shot_plot


def player_card(player):
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
                     'border': 'white', 'text-align': 'center', 'font-size': '14px'}
            row.append(html.Td(value, style=style))

        rows.append(html.Tr(row))

    return html.Div(children=[
        html.Table(rows, style=TABLE_STYLE),
        dcc.Link(html.Button('MORE STATS', id='player-drilldown-' + str(player), style={
            'font-size': '12px', 'color': 'darkgrey', 'font-weight': 'bold', 'border': 'none'}),
                 href='/player/' + str(player))
    ])


def current_roster(df, team_id=None):
    if team_id is not None:
        df = df[df['TeamId'] == str(team_id)]

    team_dict = {}
    cols = df['Position'].unique()

    for position in cols:
        team_dict[position] = np.array(
            df.loc[df['Position'] == position, 'PlayerId'])

    roster = pd.DataFrame(dict([(k, pd.Series(v))
                                for k, v in team_dict.items()]))
    roster = roster.fillna('')

    return roster


def player_image(player):
    if player != '':
        img = rosters.loc[rosters['PlayerId'] == player, 'PlayerImg']
        img = img.iloc[0] if len(img) > 0 else DEFAULT_IMAGE

        name = rosters.loc[rosters['PlayerId'] == player, 'Player']
        name = name.iloc[0] if len(name) > 0 else 'Name Missing'

        return html.Div(children=[
            html.Img(src=str(img), style={
                'height': '160px'}, className='image'),
            html.Div(html.H4(str(name),
                             style={'font-size': '22px',
                                    'text-align': 'center'})),
            html.Div(player_card(player), className='overlay')],
            className='container', style={'width': '100%', 'height': '100%', 'position': 'relative'})


def build_table(df, table_setting='Summary'):
    rows = []
    if df is not None:
        for i in range(len(df)):
            row = []
            for col in df.columns:
                value = player_image(df.iloc[i][col]) if table_setting == 'Summary' else df.iloc[i][col]
                style = {'align': 'center', 'padding': '3px', 'text-align': 'center',
                         'font-size': '12px'}
                row.append(html.Td(value, style=style))

                if i % 2 == 0 and 'background-color' not in style:
                    style['background-color'] = '#f2f2f2'

            rows.append(html.Tr(row))

        return html.Table(
            [html.Tr([html.Th(col, style=HEADER_STYLE) for col in df.columns])] + rows, style=TABLE_STYLE)


def shot_map(data):
    if data is not None:
        made_x = data[data['EType'] == 1]['LocationX']
        made_y = data[data['EType'] == 1]['LocationY']

        missed_x = data[data['EType'] == 2]['LocationX']
        missed_y = data[data['EType'] == 2]['LocationY']

        return html.Div(
            dcc.Graph(
                id='shot-plot',
                figure={
                    'data': [
                        go.Scatter(
                            x=made_x,
                            y=made_y,
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
                            x=missed_x,
                            y=missed_y,
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
                        shapes=court_plot()
                    )
                }
            )
        )


def division_image_header(conf, float, align):
    return html.Div(
        [dcc.Link(
            html.Img(src=teams.loc[teams['TeamID'] == i['TeamID'], 'TeamLogo'].iloc[0],
                     style={'height': 'auto', 'width': '75px'},
                     className='team-overlay',
                     id='team-logo-' + str(i['TeamID'])),
            href='/team/' + str(i['TeamID']),
            style={'padding-{}'.format(align): '20px'})
            for i in teams.sort_values(by=['Division', 'TeamCode']).to_dict('records') if
            i['TeamID'] is not None and i['Conference'] == conf],
        style={'float': float, 'width': '50%', 'text-align': align, 'padding': '0px 0px 0px 0px'}
    )


def team_stats_layout(xaxis_title, chart_title):
    layout = go.Layout(
        title=chart_title,
        xaxis=dict(
            title=xaxis_title,
            fixedrange=True,
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Value',
            fixedrange=True,
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        showlegend=True,
        plot_bgcolor='#ffffff',
        barmode='group',
        bargap=0.2,
        bargroupgap=0.2,
        margin=go.layout.Margin(l=40, r=0, t=40, b=30)
    )
    return layout


def team_stats_figure(team_stats, data_x, metrics, chart_title, chart_type):
    return go.Figure(
        data=[
                 go.Bar(
                     x=data_x,
                     y=[stat[m] for stat in team_stats],
                     text=[stat[m] for stat in team_stats],
                     textposition='inside',
                     name=m.upper(),
                 ) for m in metrics if m is not None
             ] +
             [
                 go.Scatter(
                     x=data_x,
                     y=[statistics.mean([stat[m] for stat in team_stats])] * len(data_x),
                     mode='lines+markers',
                     line=dict(
                         width=7
                     ),
                     name='AVG {}'.format(m.upper()),
                 ) for m in metrics if m is not None
             ],
        layout=team_stats_layout(chart_type, chart_title),
    )


def team_stats_graph(team_id, value, option, metric, season):
    metrics = [metric, None] if type(metric) == str else metric

    if team_id and team_id != '':
        chart_title = 'Team: {0}'.format(TEAMS[team_id]['name'])
    else:
        chart_title = 'Select a team to get started'

    if team_id and value == 'Roster':
        if option == 'Compare':
            query = '{}'.format(team_season_stats_query)
            team_stats = sql.load_data(query, TEAM_STATS_COLUMNS).sort_values(by='teamcode').to_dict('records')

            team_stats = [stat for stat in team_stats if stat['season'] == season]
            data_x = [stat['teamcode'] for stat in team_stats]

            return team_stats_figure(team_stats, data_x, metrics, chart_title, 'Team')

        elif option == 'Trend':
            query = '{} {}'.format(team_season_stats_query, team_id)
            team_stats = sql.load_data(query, TEAM_STATS_COLUMNS).sort_values(by='season').to_dict('records')

            data_x = [str(i['season']) for i in team_stats]

            return team_stats_figure(team_stats, data_x, metrics, chart_title, 'Season')

    else:
        return go.Figure(
            data=[
                go.Bar(
                    x=[],
                    y=[]
                )
            ],
            layout=go.Layout(
                title='Select a team to get started',
            )
        )


def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="div-tabs",
                value='Roster',
                className='custom-tabs',
                children=[
                    dcc.Tab(label='ROSTER', value='Roster',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                    dcc.Tab(label='STATS', value='Stats',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                    dcc.Tab(label='SHOTS', value='Shots',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE)],
                style=ALL_TAB_STYLE
            ),
        ],
    )


rosters = sql.load_data(team_roster_query, CURRENT_ROSTER_COLUMNS)
team_df = current_roster(rosters)

teams = sql.load_data(team_query, TEAM_COLUMNS)


def update_layout():
    return html.Div(
        children=[
            dcc.Location(id='team_url', refresh=False),

            html.Div(
                children=[
                    division_image_header('Eastern', 'left', 'right'),
                    division_image_header('Western', 'right', 'left')
                ],
                style={'display': 'flex'}
            ),

            build_tabs(),

            html.P('Select TREND to view team stats over time or COMPARE to see stats for all teams in the league',
                   style={'font-size': '12px'}
                   ),

            dcc.RadioItems(
                id='stat-option',
                options=[
                    {'label': 'TREND', 'value': 'Trend'},
                    {'label': 'COMPARE', 'value': 'Compare'}
                ],
                value='Trend',
                labelStyle={'display': 'inline-block', 'padding': '5px'}
            ),

            html.P('Choose between PLAYER and TEAM level stats',
                   style={'font-size': '12px'}
                   ),

            dcc.RadioItems(
                id='xaxis-option',
                options=[
                    {'label': 'PLAYER', 'value': 'Player'},
                    {'label': 'TEAM', 'value': 'Team'}
                ],
                value='Team',
                labelStyle={'display': 'inline-block', 'padding': '5px'}
            ),

            dcc.RadioItems(
                id='season-option',
                options=[{'label': i, 'value': i} for i in
                         ['2014-2015', '2015-2016', '2016-2017', '2017-2018', '2018-2019', '2019-2020']],
                value='2019-2020',
                labelStyle={'display': 'inline-block', 'padding': '5px'}
            ),

            dcc.Dropdown(
                id='metric-picker',
                options=[{'label': i, 'value': i} for i in TEAM_STATS_COLUMNS if
                         i not in ['tid', 'teamcode', 'season']],
                multi=True,
                value='ast'
            ),

            dcc.Loading(
                id="loading-1",
                children=[html.Div(
                    dcc.Graph(
                        id='team_graph',
                        config={
                            'displayModeBar': False
                        }
                    ),
                    style={'padding': '10px'}
                )],
                type="default"
            ),

            dcc.Loading(
                id="loading-2",
                children=html.Div(
                    id='team_roster_container',
                    style={'padding': '10px'}
                ),
                type="default"
            ),

            html.Div(
                id='shot_plot'
            )

        ])


app.layout = update_layout()


@app.callback(
    Output('team_roster_container', 'children'),
    [Input('team_url', 'pathname'),
     Input('div-tabs', 'value')]
)
def update_team_roster_table(pathname, value):
    if pathname:
        team_id = pathname.split('/')[-1]
    else:
        return html.P('Select a team to get started')

    if value == 'Roster':
        _teamdf = current_roster(rosters, team_id)
        return build_table(_teamdf, 'Summary')

    elif value == 'Shots':
        return html.P('Shots')


@app.callback(
    Output('team_graph', 'figure'),
    [Input('team_url', 'pathname'),
     Input('div-tabs', 'value'),
     Input('stat-option', 'value'),
     Input('metric-picker', 'value'),
     Input('season-option', 'value')]
)
def team_summary_stats(pathname, value, option, metric, season):
    team_id = pathname.split('/')[-1] if pathname else None

    return team_stats_graph(team_id, value, option, metric, season)


@app.callback(
    Output('shot_plot', 'figure'),
    [Input('team_url', 'pathname')]
)
def update_shot_plot(pathname):
    if pathname:
        if pathname.split('/')[1] == 'player':
            player_id = pathname.split('/')[-1]
        else:
            return html.P('SELECT A TEAM ABOVE TO GET STARTED', style={'float': 'center'})

        player_df = get_shots(player_id, period='', venue='')

        return shot_map(player_df)


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8050)
