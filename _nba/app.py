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

from nba_settings import player_img_url, team_img_url

from app_styles import DEFAULT_IMAGE, HEADER_STYLE, TABLE_STYLE, SELECTED_TAB_STYLE, \
    SINGLE_TAB_STYLE, ALL_TAB_STYLE, EVENT_DEFINITIONS

from sql_queries import team_roster_query, shot_chart_query, team_compare_query, team_trend_query, \
    SHOT_PLOT_COLUMNS, TEAM_STATS_COLUMNS, CURRENT_ROSTER_COLUMNS, player_shooting_stats_query, \
    SHOOTING_STATS_COLUMNS, position_clusters_query, POSITION_CLUSTERS_COLUMNS

server = Flask(__name__)
sql = SqlConnection('NBA')

app = dash.Dash(
    name='nba_app',
    server=server,
    url_base_pathname='/',
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
    suppress_callback_exceptions=True)

POSITIONS = [
    ['C-F', 'Center'],
    ['G', 'Guard'],
    ['F-C', 'Forward'],
    ['F', 'Forward'],
    ['F-G', 'Forward'],
    ['C', 'Center'],
    ['G-F', 'Guard']
]

position_reference = pd.DataFrame(
    data=POSITIONS, columns=['Position', 'Position Group'])


def player_card(player):
    rows = []
    rosters = get_roster()
    df = rosters[rosters['player_id'] == str(player)]

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

    return html.Div(children=[html.Table(rows, style=TABLE_STYLE)])


def current_roster(team_id=None):
    if team_id is None:
        return []

    roster = get_roster(team_id)
    new_df = pd.merge(roster, position_reference, on='Position', how='left')

    team_dict = {}
    for position in ['Forward', 'Guard', 'Center']:
        team_dict[position] = np.array(
            new_df.loc[new_df['Position Group'] == position, 'player_id'])

    roster = pd.DataFrame(dict([(k, pd.Series(v))
                                for k, v in team_dict.items()]))
    roster = roster.fillna('')

    return roster


def player_image(player):
    rosters = get_roster()

    if player != '':
        img = get_player_img(player)

        name = rosters.loc[rosters['player_id'] == player, 'Player']
        name = name.iloc[0] if len(name) > 0 else 'Name Missing'

        return html.Div(children=[
            html.Img(src=str(img), style={
                'height': '160px'}, className='image'),
            html.Div(html.H4(str(name),
                             style={'font-size': '22px',
                                    'text-align': 'center'})),
            html.Div(player_card(player), className='overlay')],
            className='container', style={'width': '100%', 'height': '100%', 'position': 'relative'})


def build_table(df, table_setting='Player Summary'):
    if df is None:
        return []

    rows = []
    for i in range(len(df)):
        row = []
        for col in df.columns:

            if table_setting == 'Player Summary':
                value = player_image(df.iloc[i][col])

            elif table_setting == 'Shot Summary' and col == 'Player':
                player = df.iloc[i][col]

                roster = get_roster()
                player_id = roster.loc[roster['Player']
                                       == str(player), 'player_id'].iloc[0]

                value = dcc.Link(html.Button(player,
                                             id='player-shots-' +
                                             str(player),
                                             style={'font-size': '12px', 'color': 'darkgrey', 'font-weight': 'bold', 'border': 'none'}),
                                 href='/player/' + str(player_id))
            else:
                value = df.iloc[i][col]

            if table_setting == 'Shot Summary':
                style = {'align': 'center', 'padding': '3px',
                         'text-align': 'center', 'font-size': '10px'}

            style = {'align': 'center', 'padding': '3px',
                     'text-align': 'center', 'font-size': '12px'}
            row.append(html.Td(value, style=style))

            if i % 2 == 0 and 'background-color' not in style:
                style['background-color'] = '#f2f2f2'

        rows.append(html.Tr(row))

    if table_setting == 'Shot Summary':
        SHOT_HEADER_STYLE = {
            'align': 'center',
            'width': '80px',
            'background-color': '#0f6db5',
            'text-align': 'center',
            'font-size': '14px',
            'padding': '10px',
            'color': '#ffffff'}

        return html.Table(
            [html.Tr([html.Th(col, style=SHOT_HEADER_STYLE) for col in df.columns])] + rows, style=TABLE_STYLE)

    return html.Table(
        [html.Tr([html.Th(col, style=HEADER_STYLE) for col in df.columns])] + rows, style=TABLE_STYLE)


def get_shots(stat_id, stat_type):
    if stat_type == 'player':
        return sql.load_data(shot_chart_query.format(stat_id, 'gp.[tid]'), SHOT_PLOT_COLUMNS)
    elif stat_type == 'team':
        return sql.load_data(shot_chart_query.format('gp.[pid]', stat_id), SHOT_PLOT_COLUMNS)


def shot_map(data, stat_type):
    if data is None:
        return []

    made_x = data[data['EType'] == 1]['LocationX']
    made_y = data[data['EType'] == 1]['LocationY']
    made_text = data[data['EType'] == 1]['Description']

    missed_x = data[data['EType'] == 2]['LocationX']
    missed_y = data[data['EType'] == 2]['LocationY']
    missed_text = data[data['EType'] == 2]['Description']


    team_id = data['TeamID'].iloc[0]
    roster = get_roster(team_id)

    if stat_type == 'player':
        player_id = data['PlayerID'].iloc[0]
        player = roster.loc[roster['player_id']
                            == str(player_id), 'Player'].iloc[0]

    title = player if stat_type == 'player' else teams.loc[teams['team_id'] == str(
        team_id), 'name'].iloc[0]

    shooting_stats = sql.load_data(
        player_shooting_stats_query.format(team_id), SHOOTING_STATS_COLUMNS)
    shooting_stats = shooting_stats[['Player', 'G', 'GS', 'FGM', 'FGA', 'FG%', 'FTM', 'FTA', 'FT%', 'PIP', 'PIPM',
                                     'PIPA', 'PIP%', 'PTS', '3PM', '3PA', '3P%']]

    data = [
        go.Scatter(
            x=made_x,
            y=made_y,
            text=made_text,
            mode='markers',
            name='Made',
            opacity=0.7,
            marker=dict(
                size=5,
                color='blue',
                line=dict(
                    width=1,
                    color='rgb(0, 0, 0, 1)'
                )
            )
        ),
        go.Scatter(
            x=missed_x,
            y=missed_y,
            text=missed_text,
            mode='markers',
            name='Missed',
            opacity=0.7,
            marker=dict(
                size=5,
                color='red',
                line=dict(
                    width=1,
                    color='rgb(0, 0, 0, 1)'
                )
            )
        )
    ]

    layout = go.Layout(
        title=f'Shooting Analysis: {title}',
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

    return html.Div(
        children=[
            html.H1(),
            dcc.Graph(
                id='shot_plot',
                figure={
                    'data': data,
                    'layout': layout
                }
            ),
            build_table(shooting_stats, 'Shot Summary')]
    )


def division_image_header(conf, float, align):
    return html.Div(
        [dcc.Link(
            html.Img(src=teams.loc[teams['team_id'] == i['team_id'], 'teamLogo'].iloc[0],
                     style={'height': 'auto', 'width': '75px'},
                     className='team-overlay',
                     id='team-logo-' + str(i['team_id'])),
            href='/team/' + str(i['team_id']),
            style={'padding-{}'.format(align): '20px'})
            for i in teams.sort_values(by=['division', 'abbr']).to_dict('records') if
            i['team_id'] is not None and i['conference'] == conf],
        style={'float': float, 'width': '50%',
               'text-align': align, 'padding': '0px 0px 0px 0px'}
    )


def team_box_plots(season):
    query = team_compare_query.format(season)
    teams = generate_teams_df()

    team_stats = sql.load_data(query, TEAM_STATS_COLUMNS).sort_values(by='tid')
    team_stats = team_stats.drop(['season', 'games'], axis=1)
    metrics = team_stats.columns
    team_stats = team_stats.to_dict('records')

    data = []
    for metric in metrics:
        if metric == 'tid':
            continue

        data.append(
            go.Box(
                y=[stat[metric] for stat in team_stats],
                name=metric,
                jitter=0.1,
                pointpos=-1,
                boxpoints='all',
                text=[teams.loc[teams['team_id'] == str(
                    stat['tid']), 'name'].iloc[0] for stat in team_stats],
                marker=dict(
                    color='rgb(7,40,89)'),
                line=dict(
                    color='rgb(7,40,89)')
            )
        )

    layout = go.Layout(
        title=f'Team Box Score Stats Comparison: {season}',
        height=500,
        yaxis=dict(
            autorange=True,
            showgrid=True,
            zeroline=False,
            dtick=10,
            gridcolor='rgb(255, 255, 255)',
            gridwidth=1,
            zerolinecolor='rgb(255, 255, 255)',
            zerolinewidth=2,
        ),
        margin=dict(
            l=40,
            r=30,
            b=80,
            t=100,
        ),
        paper_bgcolor='rgb(255, 255, 255)',
        plot_bgcolor='rgb(255, 255, 255)',
        showlegend=False
    )

    fig = go.Figure(data=data, layout=layout)

    return [
        dcc.RadioItems(
            id='season_option',
            options=[{'label': i, 'value': i} for i in
                     ['2016-2017', '2017-2018', '2018-2019', '2019-2020']],
            value='2019-2020',
            labelStyle={
                'display': 'inline-block', 'padding': '5px'}
        ),

        dcc.Graph(
            figure=fig,
            id='box-plot'
        ),

        player_cluster_scatter(season)

    ]


def player_cluster_scatter(season):

    position_clusters = sql.load_data(position_clusters_query.format(
        season), POSITION_CLUSTERS_COLUMNS).sort_values(by='tags')

    clusters = position_clusters.tags.unique().tolist()
    data = []
    for cluster in clusters:
        data_x = position_clusters[position_clusters['tags']
                                   == cluster]['x1'].tolist()
        data_y = position_clusters[position_clusters['tags']
                                   == cluster]['x2'].tolist()
        data_text = position_clusters[position_clusters['tags']
                                      == cluster]['player_name'].tolist()

        data.append(
            go.Scatter(
                x=data_x,
                y=data_y,
                text=data_text,
                name=cluster,
                mode='markers',
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
            )
        )

    layout = dict(
        title=f'Player KMeans Clusters: {season}',
        xaxis={'title': 'X1'},
        yaxis={'title': 'X2'},
        height=500,

        margin=dict(
            l=40,
            r=30,
            b=80,
            t=100,
        ),
        legend={'x': 0, 'y': 1},
        paper_bgcolor='rgb(255, 255, 255)',
        plot_bgcolor='rgb(255, 255, 255)',
        hovermode='closest'
    )

    fig = go.Figure(data=data, layout=layout)

    return dcc.Graph(
        id='player-cluster-scatter',
        figure=fig
    )


def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="div_tabs",
                value='ROSTER',
                className='custom-tabs',
                children=[
                    dcc.Tab(label='ROSTER', value='ROSTER',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                    dcc.Tab(label='STATS', value='STATS',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE),
                    dcc.Tab(label='SHOTS', value='SHOTS',
                            style=SINGLE_TAB_STYLE, selected_style=SELECTED_TAB_STYLE)],
                style=ALL_TAB_STYLE
            ),
        ],
    )


def generate_teams_df():
    data = []
    for team in TEAMS.keys():
        TEAMS[team]['teamLogo'] = team_img_url.format(TEAMS[team]['abbr'])
        data.append(TEAMS[team])

    return pd.DataFrame(data)


def get_player_img(player_id):
    return player_img_url.format(player_id)


teams = generate_teams_df()


def get_roster(team_id=None):
    if team_id:
        return sql.load_data(team_roster_query.format(team_id), CURRENT_ROSTER_COLUMNS)
    else:
        return sql.load_data(team_roster_query.format('[teamid]'), CURRENT_ROSTER_COLUMNS)


def default_layout():
    return [
        dcc.Location(id='team_url', refresh=False),

        html.Div(
            children=[
                division_image_header('Eastern', 'left', 'right'),
                division_image_header('Western', 'right', 'left')
            ],
            style={'display': 'flex'}
        ),

        html.P('Select a team to get started.', style={'font': ''}),

        build_tabs(),
    ]


def update_layout():
    return html.Div(
        children=default_layout() + [
            dcc.Loading(
                id="loading-1",
                children=[html.Div(
                    id='team_roster_container',
                    style={'padding': '10px'}
                )],
                type="default"
            ),

            html.Div(
                id='season_option',
            ),

            dcc.Loading(
                id="loading-2",
                children=[html.Div(
                    id='team_graph',
                    style={'padding': '10px'}
                )],
                type="default"
            ),

            html.Div(
                id='shot_plot',
                style={'padding': '10px'}
            )
        ])


app.layout = update_layout()


@app.callback(
    Output('team_roster_container', 'children'),
    [Input('team_url', 'pathname'), Input('div_tabs', 'value')]
)
def update_team_roster_table(pathname, value):
    if pathname and value == 'ROSTER':
        path = pathname.split('/')
        path.pop(0)
    else:
        return []

    if path[0] == 'team':
        team_df = current_roster(path[1])

        return build_table(team_df, 'Player Summary')


@app.callback(
    Output('team_graph', 'children'),
    [Input('div_tabs', 'value')]
)
def update_stat_plot(value):
    if value == 'STATS':
        season = '2019-2020'
        return team_box_plots(season)
    else:
        return []


@app.callback(
    Output('shot_plot', 'children'),
    [Input('team_url', 'pathname'), Input('div_tabs', 'value')]
)
def update_shot_plot(pathname, value):
    if pathname and value == 'SHOTS':
        path = pathname.split('/')
        path.pop(0)
    else:
        return []

    shots = get_shots(path[1], path[0])

    return shot_map(shots, path[0])


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True, port=8050)
