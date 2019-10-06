import pandas as pd
import requests
import pyodbc
import datetime
import time
from Settings import sql_config, roster_headers
from py_modules import sql_server_connection, execute_sql

if datetime.date.today().month in (7, 8, 9, 10, 11, 12):
    y = datetime.date.today().year
    current_season = str(y) + '-' + str(y + 1)[-2:]
else:
    y = datetime.date.today().year
    current_season = str(y - 1) + '-' + str(y)[-2:]

teams = ['1610612737', '1610612738', '1610612751', '1610612766', '1610612741', '1610612739',
         '1610612765', '1610612754', '1610612748', '1610612749', '1610612752', '1610612753',
         '1610612755', '1610612761', '1610612764', '1610612742', '1610612743', '1610612744',
         '1610612745', '1610612746', '1610612747', '1610612763', '1610612750', '1610612740',
         '1610612760', '1610612756', '1610612757', '1610612758', '1610612759', '1610612762']

conn = sql_server_connection(sql_config)
cursor = conn.cursor()

roster_lst = []
failed_responses = []
for t in teams:
    try:
        url = 'https://stats.nba.com/stats/commonteamroster?LeagueID=00&Season=' + str(
            current_season) + '&TeamID=' + str(t)
        roster_rqst = requests.request('GET', url, headers=roster_headers)

        print(t, roster_rqst.status_code)

        roster = roster_rqst.json()
        roster_lst.append(roster['resultSets'][0]['rowSet'])

        time.sleep(5)
        pass
    except Exception as e:
        print(t, e)
        failed_responses.append(t)

headers = roster['resultSets'][0]['headers']
team_rosters = [dict(zip(headers, player)) for team in roster_lst for player in team]

now = datetime.datetime.utcnow()

for team in team_rosters:
    team['TIMESTAMP'] = now

execute_sql('TeamRosters', team_rosters, ['TIMESTAMP'], cursor)
conn.commit()
