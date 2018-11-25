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
center_circe_shape = dict(
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


# ---------- CHARTING THE SHOTS ----------
missed_shot_trace = go.Scatter(
    x = shots_df[shots_df['EVENT_TYPE'] == 'Missed Shot']['LOC_X'],
    y = shots_df[shots_df['EVENT_TYPE'] == 'Missed Shot']['LOC_Y'],
    mode = 'markers',
    name = 'Missed Shot',
    marker = dict(
        size = 5,
        color = 'rgba(255, 255, 0, .8)',
        line = dict(
            width = 1,
            color = 'rgb(0, 0, 0, 1)'
        )
    )
)
 
made_shot_trace = go.Scatter(
    x = shots_df[shots_df['EVENT_TYPE'] == 'Made Shot']['LOC_X'],
    y = shots_df[shots_df['EVENT_TYPE'] == 'Made Shot']['LOC_Y'],
    mode = 'markers',
    name = 'Made Shot',
    marker = dict(
        size = 5,
        color = 'rgba(0, 200, 100, .8)',
        line = dict(
            width = 1,
            color = 'rgb(0, 0, 0, 1)'
        )
    )
)
 
data = [missed_shot_trace, made_shot_trace]
 
layout = go.Layout(
    title='Shots by Stephen Curry in NBA session 2015-16',
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
 
fig = go.Figure(data=data, layout=layout)
iplot(fig)


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
