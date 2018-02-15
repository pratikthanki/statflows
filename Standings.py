import requests
import json
import pandas as pd 
import pyodbc
from sqlalchemy import create_engine
from Links import *


# current league standing, always replace latest request with data in DB
headers = headers


url1 = Standings_url1
try:
    standingsRequest = requests.get(url1, headers=headers)
    standingsRequest = standingsRequest.json()
    pass
except:
    print('Request Failed')


standings = []
for i in standingsRequest['payload']['standingGroups']:
    for j in i['teams']:
        standings.append([j['profile']['abbr']] + [j['profile']['conference']] + [j['profile']['id']] + [j['profile']['name']] + [j['standings']['confRank']] + [j['standings']['wins']] + [j['standings']['losses']] + [j['standings']['streak']] + [j['standings']['winPct']] + [j['standings']['divLoss']] + [j['standings']['divWin']] + [j['standings']['divRank']] + [j['standings']['last10']] + [j['standings']['homeWin']] + [j['standings']['homeLoss']] + [j['standings']['roadWin']] + [j['standings']['roadLoss']] + [j['standings']['roadStreak']] + [j['standings']['homeStreak']])

            

standings = pd.DataFrame(standings)
standings.columns = ['Abbr', 'Conference', 'Team ID', 'Team Name', 'Conf Rank', 'Wins', 'Losses', 'Streak', 'Win %', 'Div Losses', 'Div Wins', 'Div Rank', 'Last 10', 'Home Wins', 'Home Losses', 'Road Wins', 'Road Losses', 'Road Streak', 'Home Streak']


# team request to get player data for all players at team X


teamData = []
url2 = Standings_url2
for i in standings['Team Name']:
    try:
        teamRequest = requests.get(url2 + str(i), headers=headers)
        teamRequest = teamRequest.json()
        teamData.append(teamRequest)
        print(i)
    except ValueError:
        print(i + ' - Decoding Error')


teamData[0]['payload']['season']


for i in teamData:
    for j in i['payload']['leagueSeasonAverage']:
        print(j)



# Writing to the database 
ms_sql = ms_sql
# engine = create_engine('mssql+pyodbc://' + ms_sql)


mysql = mysql
# engine = create_engine('mysql+mysqlconnector://' + mysql)


cursor = engine.connect()


standings.to_sql('LeagueStandings', engine, flavor=None, schema='dbo', if_exists='replace', index=None)


