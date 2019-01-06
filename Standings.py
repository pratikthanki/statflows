import requests
import json
import pandas as pd
import pyodbc
from Settings import *


standingsRequest = requests.request('GET', Standings_url1, headers=headers)
standingsRequest = standingsRequest.json()


standings = []
for i in standingsRequest['payload']['standingGroups']:
    for j in i['teams']:
        standings.append([j['profile']['abbr']] + [j['profile']['conference']] + [j['profile']['id']] + [j['profile']['name']] + [j['standings']['confRank']] + [j['standings']['wins']] + [j['standings']['losses']] + [j['standings']['streak']] + [j['standings']['winPct']] + [j['standings']['divLoss']] + [j['standings']['divWin']] + [j['standings']['divRank']] + [j['standings']['last10']] + [j['standings']['homeWin']] + [j['standings']['homeLoss']] + [j['standings']['roadWin']] + [j['standings']['roadLoss']] + [j['standings']['roadStreak']] + [j['standings']['homeStreak']])


standings = pd.DataFrame(standings)
standings.columns = ['Abbr', 'Conference', 'TeamId', 'TeamName', 'ConfRank', 'Wins', 'Losses', 'Streak', 'Win%', 'DivLosses',
                     'DivWins', 'DivRank', 'Last10', 'HomeWins', 'HomeLosses', 'RoadWins', 'RoadLosses', 'RoadStreak', 'HomeStreak']


# Writing to the database
def SQLServerConnection(config):
    conn_str = (
        'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}')

    conn = pyodbc.connect(
        conn_str.format(**config)
    )

    return conn


conn = SQLServerConnection(sqlconfig)
cursor = conn.cursor()

cursor.execute('DELETE FROM LeagueStandings')

print('Writing to database')

cursor.executemany(
    'INSERT INTO LeagueStandings (Abbr, Conference, TeamId, TeamName, ConfRank, Wins, Losses, Streak, [Win%], DivLosses, DivWins, DivRank, Last10, HomeWins, HomeLosses, RoadWins, RoadLosses, RoadStreak, HomeStreak, LastUpdates) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, GETDATE())', standings.values.tolist())

conn.commit()

print('Job completed successfully')
