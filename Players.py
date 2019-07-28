import requests
import json
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
import time
from Settings import *


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


# Create dataframe from sql table in database
Players = loadData('SELECT * FROM [dbo].[Players] WHERE PlayerID != 0')
Players.columns = ['PlayerID', 'FirstName', 'LastName']
Players = Players[:10]


# --------------------------- Player Info Rwquest ---------------------------

playerInfo = []
for i in Players['PlayerID'].values:
    try:
        time.sleep(5)
        playerInfoRequest = requests.get(Players_url1 + str(i), headers=headers)
        print(str(i), str(playerInfoRequest.status_code))
        #playerInfoRequest.raise_for_status()
        playerInfoRequest = playerInfoRequest.json()
        playerInfo.append(playerInfoRequest)
        pass
    except ValueError as e:
        print(i, e)



playerInfo[0]['resultSets'][0]['headers']

playerTable = []
for i in playerInfo:
    for j in i['resultSets']:
        if j['name'] == 'CommonPlayerInfo':
            for k in j['rowSet']:
                try:
                    playerTable.append(k)
                except KeyError:
                    print('JSON error')

playerTable = pd.DataFrame(playerTable)
playerHeaders = playerInfo[0]['resultSets'][0]['headers']
playerTable.columns = playerHeaders
