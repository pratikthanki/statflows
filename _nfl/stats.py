import pandas as pd
import requests 
from sqlalchemy import create_engine
import pyodbc
import os 

os.chdir('C:\\Users\\PratikThanki\\OneDrive - EDGE10 (UK) Ltd\\Pratik\\Python\\statflows-nfl')
from Settings import *


pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 30)

def getStats(stat):
    emptylist = []
    playerlist = []
    #for s in stats:
    for i in seasons:
        for x in range(1, 23):
            if x <= 17:
                query = requests.request('GET', baseurl + str(stat) + '?season=' + str(i) + '&seasonType=REG&week=' + str(x), headers=headers)
            else:
                query = requests.request('GET', baseurl + str(stat) + '?season=' + str(i) + '&seasonType=POST&week=' + str(x), headers=headers)

            print(i, x, query.status_code)
            emptylist.append(query.json())
            playerlist.append(query.json())

    temp = []
    player = []
    new = []
    for weeks in emptylist:
        for stats in weeks['stats']:
            player.append(stats['player'])
            if 'player' in stats:
                del stats['player']
            temp.append(stats)

    tempdf = pd.DataFrame(temp)

    return tempdf


passinglist = getStats('passing')
rushinglist = getStats('rushing')
receivinglist = getStats('receiving')

# engine = create_engine(str(mssql) + 'nfldata')
# cursor = engine.connect()

# passinglist.to_sql('Passing', engine, schema='dbo', if_exists='replace', index=None, chunksize=1000)
# rushinglist.to_sql('Rushing', engine, schema='dbo', if_exists='replace', index=None, chunksize=10000)
# receivinglist.to_sql('Receiving', engine, schema='dbo', if_exists='replace', index=None, chunksize=10000)

