import os
import pandas as pd
import numpy as np
import pyodbc
import requests
import base64
import time
from sqlalchemy import create_engine

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go

from Settings import *
from Queries import *


app = dash.Dash(__name__)
server = app.server
app.scripts.config.serve_locally = True
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'


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
        rows = pd.read_sql(query, conn)

    for row in rows:
        sqlData.append(list(row))

    df = pd.DataFrame(sqlData)

    return df


game_Query = "EXEC [dbo].[sp_PlayerShotChart] '201142'"

game_locations = loadData(game_Query)
game_locations.columns = ['ClockTime' ,'Description' ,'EType' ,'Evt' ,'LocationX' ,'LocationY' ,'Period' ,'TeamID', 'PlayerID']

game_list = game_locations.values.tolist()


# outer boundary
outer_shape = {
    'type': 'rect',
    'x0': 0,
    'y0': 0,
    'x1': 94,
    'y1': 50,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left backboard
left_backboard_shape = {
    'type': 'line',
    'x0': 4,
    'y0': 22,
    'x1': 4,
    'y1': 28,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right backboard
right_backboard_shape = {
    'type': 'line',
    'x0': 90,
    'y0': 22,
    'x1': 90,
    'y1': 28,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left outer box
left_outerbox_shape = {
    'type': 'rect',
    'x0': 0,
    'y0': 17,
    'x1': 19,
    'y1': 33,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left inner box
left_innerbox_shape = {
    'type': 'rect',
    'x0': 0,
    'y0': 19,
    'x1': 19,
    'y1': 31,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right outer box
right_outerbox_shape = {
    'type': 'rect',
    'x0': 75,
    'y0': 17,
    'x1': 94,
    'y1': 33,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right inner box
right_innerbox_shape = {
    'type': 'rect',
    'x0': 75,
    'y0': 19,
    'x1': 94,
    'y1': 31,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left corner a
leftcorner_topline_shape = {
    'type': 'rect',
    'x0': 0,
    'y0': 47,
    'x1': 14,
    'y1': 47,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left corner b
leftcorner_bottomline_shape = {
    'type': 'rect',
    'x0': 0,
    'y0': 3,
    'x1': 14,
    'y1': 3,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right corner a
rightcorner_topline_shape = {
    'type': 'rect',
    'x0': 80,
    'y0': 47,
    'x1': 94,
    'y1': 47,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right corner b
rightcorner_bottomline_shape = {
    'type': 'rect',
    'x0': 80,
    'y0': 3,
    'x1': 94,
    'y1': 3,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# half court
half_court_shape = {
    'type': 'rect',
    'x0': 47,
    'y0': 0,
    'x1': 47,
    'y1': 50,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left hoop
left_hoop_shape = {
    'type': 'circle',
    'x0': 6.1,
    'y0': 25.75,
    'x1': 4.6,
    'y1': 24.25,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right hoop
right_hoop_shape = {
    'type': 'circle',
    'x0': 89.4,
    'y0': 25.75,
    'x1': 87.9,
    'y1': 24.25,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left free throw circle
left_freethrow_shape = {
    'type': 'circle',
    'x0': 25,
    'y0': 31,
    'x1': 13,
    'y1': 19,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right free throw circle
right_freethrow_shape = {
    'type': 'circle',
    'x0': 81,
    'y0': 31,
    'x1': 69,
    'y1': 19,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# center big circle
center_big_shape = {
    'type': 'circle',
    'x0': 53,
    'y0': 31,
    'x1': 41,
    'y1': 19,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# center small circle
center_small_shape = {
    'type': 'circle',
    'x0': 49,
    'y0': 27,
    'x1': 45,
    'y1': 23,
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# left arc shape
left_arc_shape = {
    'type': 'path',
    'path': 'M 14,47 Q 45,25 14,3',
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# right arc shape
right_arc_shape = {
    'type': 'path',
    'path': 'M 80,47 Q 49,25 80,3',
    'line': {
        'color': 'rgba(0,0,0,1)',
        'width': 1
    },
}

# list containing all the shapes
_shapes = [
    outer_shape,
    left_backboard_shape,
    right_backboard_shape,
    left_outerbox_shape,
    left_innerbox_shape,
    right_outerbox_shape,
    right_innerbox_shape,
    leftcorner_topline_shape,
    leftcorner_bottomline_shape,
    rightcorner_topline_shape,
    rightcorner_bottomline_shape,
    half_court_shape,
    left_hoop_shape,
    right_hoop_shape,
    left_freethrow_shape,
    right_freethrow_shape,
    center_big_shape,
    center_small_shape,
    left_arc_shape,
    right_arc_shape
]


def localImg(image):
    encoded_image = base64.b64encode(
        open(os.getcwd() + '/TeamLogos/' + image, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image)


def get_layout():
    return html.Div(children=[
        html.Div(
            html.Img(src=localImg('nba.png'),
                     style={
                         'height': '145px',
                         'float': 'left'},
                     ),
        ),

        html.Div(
            dcc.Graph(
                id='shot-plot',
                figure={
                    'data': [
                        go.Scatter(
                            x=[47],
                            y=[25]
                        )
                    ],
                    'layout': go.Layout(
                        title='Basketball Court',
                        shapes=_shapes
                    )
                }
            ), style={'float': 'right'})
    ])


app.layout = get_layout()

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
