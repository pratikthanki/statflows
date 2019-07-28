import requests 
import pandas as pd
import numpy as np
import pydoc
from Settings import * 
from datetime import datetime
import datetime


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

games = loadData('SELECT * FROM Games')
games.columns = ['GameId', 'Date', 'DateStr', 'GameInfo', 'Venue']


def getSeason(date):
    y = date.year

    if date.month in (7,8,9,10,11,12):
        currentseason = str(y) + '-' + str(y+1)[-2:]
    else:
        currentseason = str(y-1) + '-' + str(y)[-2:]

    return currentseason


params = {
    'StartRange':'0'
    ,'EndRange':'28800'
    ,'StartPeriod':'1'
    ,'EndPeriod':'10'
    ,'RangeType':'0'
    ,'Season': '2018-19'
    ,'SeasonType':'Playoffs'
    ,'GameID':'0041800406'
}

getdata = requests.request('GET', SpeedLoads_url1, headers=headers, params=params)
getdata = getdata.json()
results = getdata['resultSets']
pd.DataFrame(data=results[0]['rowSet'], columns= results[0]['headers'])

