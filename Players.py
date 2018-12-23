import requests
import json
import pandas as pd
import pyodbc
from sqlalchemy import create_engine
from Settings import *


ms_sql = ms_sql
# engine = create_engine('mssql+pyodbc://' + ms_sql)
cursor = engine.connect()


# Create dataframe from sql table in database
Players = pd.read_sql("select * from [dbo].[Players]", conn)
Players = Players[:10]


# --------------------------- Player Info Rwquest ---------------------------

headers = headers

playerInfo = []
url1 = Players_url1
for i in Players['PlayerID']:
    try:
        playerInfoRequest = requests.get(url1 + str(i), headers=headers)
        print(str(i) + ' - ' + str(playerInfoRequest.status_code))
        #playerInfoRequest.raise_for_status()
        playerInfoRequest = playerInfoRequest.json()
        playerInfo.append(playerInfoRequest)
        pass
    except ValueError:
        print(str(i) + 'Error during request')



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

