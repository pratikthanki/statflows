import requests
import json
import pandas as pd
import pyodbc
from shared_config import sql_config
from nba_settings import standings_1, headers
from shared_modules import sql_server_connection, execute_sql

standingsRequest = requests.request('GET', standings_1, headers=headers)
standingsRequest = standingsRequest.json()

standings = []
for i in standingsRequest['payload']['standingGroups']:
    for j in i['teams']:
        standings.append({
            'Abbr': j['profile']['abbr'],
            'Conference': j['profile']['conference'],
            'TeamId': j['profile']['id'],
            'TeamName': j['profile']['name'],
            'ConfRank': j['standings']['confRank'],
            'Wins': j['standings']['wins'],
            'Losses': j['standings']['losses'],
            'Streak': j['standings']['streak'],
            'Win%': j['standings']['winPct'],
            'DivLosses': j['standings']['divLoss'],
            'DivWins': j['standings']['divWin'],
            'DivRank': j['standings']['divRank'],
            'Last10': j['standings']['last10'],
            'HomeWins': j['standings']['homeWin'],
            'HomeLosses': j['standings']['homeLoss'],
            'RoadWins': j['standings']['roadWin'],
            'RoadLosses': j['standings']['roadLoss'],
            'RoadStreak': j['standings']['roadStreak'],
            'HomeStreak': j['standings']['homeStreak']
        })

conn, cursor = sql_server_connection(sql_config, 'nba')
cursor.execute('DELETE FROM LeagueStandings')

execute_sql('LeagueStandings', standings, ['TeamName'], cursor)
conn.commit()

print('Task completed')
