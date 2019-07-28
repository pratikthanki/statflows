import pandas as pd
import requests
from Settings import *
import pyodbc
import datetime
import time 


if datetime.date.today().month in (7,8,9,10,11,12):
    y = datetime.date.today().year
    currentseason = str(y) + '-' + str(y+1)[-2:]
else: # datetime.date.today().month in (1,2,3,4,5,6)
    y = datetime.date.today().year
    currentseason = str(y-1) + '-' + str(y)[-2:]


teams = ['1610612737', '1610612738', '1610612751', '1610612766', '1610612741', '1610612739', '1610612765', '1610612754', '1610612748', '1610612749', '1610612752', '1610612753', '1610612755', '1610612761', '1610612764', '1610612742', '1610612743', '1610612744', '1610612745', '1610612746', '1610612747', '1610612763', '1610612750', '1610612740', '1610612760', '1610612756', '1610612757', '1610612758', '1610612759', '1610612762']


def SQLServerConnection(config):
    conn_str = (
        'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}')

    conn = pyodbc.connect(
        conn_str.format(**config)
    )

    return conn


conn = SQLServerConnection(sqlconfig)
cursor = conn.cursor()

tmp = pd.DataFrame()
failed_responses = []
for t in teams:
    try:
        time.sleep(5)
        url = 'https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=' + str(currentseason)+'&TeamID=' + str(t)
        rosters = requests.request('GET', url, headers=rosterheaders)
        print(t, rosters.status_code)
        rosters = rosters.json()
        tmp = tmp.append(rosters['resultSets'][0]['rowSet'])
        pass
    except Exception as e:
        print(t, e)
        failed_responses.append(t)


if len(failed_responses) > 0:
    print('Some team requests failed:', failed_responses)
else:
    print('All team requests completed successfully')


if len(rosters) > 0:
    tmp.columns = list(rosters['resultSets'][0]['headers'])
    tmp['TimeStamp'] = datetime.datetime.now()
else:
    print('No roster data found')

print('Writing to Database')
cursor.executemany('INSERT INTO TeamRosters (TeamID ,SEASON ,LeagueID ,PLAYER ,NUM ,POSITION ,HEIGHT ,WEIGHT ,BIRTH_DATE ,AGE ,EXP ,SCHOOL ,PLAYER_ID ,TimeStamp) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', tmp.values.tolist())

conn.commit()
print('Complete')
