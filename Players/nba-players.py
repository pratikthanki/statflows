import requests
import json
import pandas as pd
import pyodbc

# Connection to ms sql using pyodbc
driver = 'ODBC DRIVER 13 for SQL Server'
server = 's'
database = 'd'
username = 'u'
password = 'p'
conn  = pyodbc.connect(r'DRIVER={ODBC DRIVER 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)


# Request a cursor from the connection that can be used for queries
cursor= conn.cursor()


# Create dataframe from sql table in database
Players = pd.read_sql("select * from [dbo].[Players]", conn)
Players = Players[:10]
# --------------------------- Player Info Rwquest ---------------------------

headers = {'user-agent': 'python'}

playerInfo = []
for i in Players['PlayerID']:
    try:
        playerInfoRequest = requests.get(r'http://' + str(i), headers=headers)
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


engine = create_engine('mssql+pyodbc://uid:pwd@dbname')


