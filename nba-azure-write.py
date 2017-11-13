import os
import sys
import requests
import json
import pandas as pd
import numpy as np
import pyodbc
from sqlalchemy import create_engine


# get today's date, for use later when getting Id's
import time
from datetime import datetime, timedelta

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
yesterday = datetime.today() - timedelta(days=1)
yesterday = datetime.strptime(yesterday.strftime("%Y-%m-%d"), "%Y-%m-%d")


# initial GET request for full season schedule for the 2017 season
scheduleRequest = requests.get(r'url').json()
type(scheduleRequest)



# --------------------------- General Game Data for use in other calls ---------------------------

# empty lists to append empty lists with general game details
gameIDs = []
gameCode = []
venue = []
gameDate = []

for i in scheduleRequest['lscd']:
    for j in i['mscd']['g']:
        if datetime.strptime(j['gdte'], "%Y-%m-%d") < now:
            gameIDs.append(j['gid'])
            gameCode.append(j['gcode'])
            venue.append(j['an'])
            gameDate.append(j['gdte'])

dateSTR = []
for line in gameCode:
    dateSTR.append(line.split('/')[0])

# pandas dataframe with all game general data
gameDetails = pd.DataFrame({'Game ID':gameIDs, 'GameCode':gameCode, 'Venue':venue, 'Date':gameDate, 'DateString': dateSTR}) # final dataframe
print(str(len(gameIDs)) + ' Game IDs Found')



# --------------------------- Game Summary per Player per Game ---------------------------

# game summary data by player by game, looping through all gameIDs up till today
gameSummaryStats = [] 
for i in gameDetails['Game ID']:
    gamedetailRequest = requests.get(r'url')
    print(i + ' - Status Code: ' + str(gamedetailRequest.status_code))
    gamedetailRequest.raise_for_status()
    gamedetailRequest = gamedetailRequest.json()
    gameSummaryStats.append(gamedetailRequest)

#print(gameSummaryStats) # list


# condensed version using function to call game stats for vls and hls
def getSummary(prop, summaries, gameList):
    for a in gameSummaryStats:
        for b in [a['g']]:
            if 'pstsg' not in b[prop]:
                test = 1
            else:
                for c in b[prop]['pstsg']:
                    c['gid'] = b['gid']
                    c['mid'] = b['mid']
                    c['tid'] = b[prop]['tid']
                    c['ta'] = b[prop]['ta']
                    gameList.append(c)



game_vls = []
game_hls = []
getSummary('vls', gameSummaryStats, game_vls)
getSummary('hls', gameSummaryStats, game_hls)

game_vls = pd.DataFrame(game_vls)
game_hls = pd.DataFrame(game_hls)
gameStaging = [game_vls, game_hls]
playergameSummary = pd.concat(gameStaging) # final dataframe
playergameSummary.dtypes

playergameSummary.columns = ['Ast','Blk', 'Blka', 'Court', 'Dreb', 'Fbpts', 'Fbptsa', 'Fbptsm', 'Fga', 'Fgm', 'Fn', 'Fta', 'Ftm', 'Game ID', 'Ln', 'Memo', 'Mid', 'Min', 'Num', 'Oreb', 'Pf', 'Player ID', 'Pip', 'Pipa', 'Pipm', 'Pm', 'Pos', 'Pts', 'Reb', 'Sec', 'Status', 'Stl', 'Ta', 'Tf', 'Team ID', 'Totsec', 'Tov', 'Tpa', 'Tpm']


# --------------------------- Game Plays - full event breakdown in the game ---------------------------

# game summary data by player by game, looping through all gameIDs up till today

gamePlaybyPlay = [] 
for i in gameDetails['Game ID']:
    gamePlotRequest = requests.get(r'url')
    print(i + ' - Status Code: ' + str(gamePlotRequest.status_code))
    gamePlotRequest.raise_for_status()
    gamePlotRequest = gamePlotRequest.json()
    gamePlaybyPlay.append(gamePlotRequest)
    
#print(gamePlaybyPlay) # list
#gamePlaybyPlay[0]['g']['pd'][0]['p']

PlaybyPlay = []
for i in gamePlaybyPlay:
    for j in i['g']['pd']:
        for k in j['pla']:
            k['period'] = j['p']
            k['gid'] = i['g']['gid']
            k['mid'] = i['g']['mid']
            PlaybyPlay.append(k)

gamePlays = pd.DataFrame(PlaybyPlay) # final dataframe
gamePlays.dtypes

gamePlays.columns = ['Clock Time', 'Description', 'EPId', 'EType', 'Evt', 'Game ID', 'HS', 'LocationX', 'LocationY', 'MId', 'MType', 'OftId', 'OpId', 'Opt1', 'Opt2', 'Period', 'Player ID', 'Team ID', 'Vs']

# --------------------------- Create Player Team DF ---------------------------

players = pd.DataFrame({'Player ID': playergameSummary['Player ID'], 'Last Name': playergameSummary['Ln'], 'First Name': playergameSummary['Fn'], 'Team ID': playergameSummary['Team ID']})
players = players.drop_duplicates()


teams = pd.DataFrame({'Team ID': playergameSummary['Team ID'], 'Team Code': playergameSummary['Ta']})
teams = teams.drop_duplicates()


# --------------------------- Player Info Rwquest ---------------------------

playerInfo = []
for i in players['Player ID']:
    playerInfoRequest = requests.get(r'url)
    playerInfoRequest.raise_for_status()
    playerInfoRequest = playerInfoRequest.json()
    playerInfo.append(playerInfoRequest)


# --------------------------- Game Box Score ---------------------------


# game box score descriptons by game, looping through all gameIDs up till today
dateSTR = sorted(set(dateSTR))
print(str(len(dateSTR)) + ' matchdays found')


gameBoxScore_staging = [] 
for i in dateSTR:
    gameBoxScoreRequest = requests.get(r'url')
    print(i + ' - Status Code: ' + str(gameBoxScoreRequest.status_code))
    gameBoxScoreRequest.raise_for_status()
    gameBoxScoreRequest = gameBoxScoreRequest.json()
    gameBoxScore_staging.append(gameBoxScoreRequest)
    
#print(gameBoxScore_staging) # list

gameBoxScore = []
for i in gameBoxScore_staging:
    if int(i['result_count']) > 0:
        for j in i['results']:
            if 'Game' and 'GameID' and 'Breakdown' in j:
                if j['GameID'] != '00':
                    if j['Breakdown'] is not None:
                        gameBoxScore.append([j['Game']] + [j['GameID']] + [j['Breakdown']] + [j['HomeTeam']['triCode']] + [j['HomeTeam']['teamName']] + [j['HomeTeam']['teamNickname']] + [j['VisitorTeam']['triCode']] + [j['VisitorTeam']['teamName']] + [j['VisitorTeam']['teamNickname']])

gameBoxScore = pd.DataFrame(gameBoxScore)
gameBoxScore = gameBoxScore.rename(columns={0: 'Game', 1: 'GameId', 2: 'BoxScore Breakdown', 3: 'HomeTeam Code', 4: 'HomeTeam Name', 5: 'HomeTeam Nickname', 6: 'AwayTeam Code', 7: 'AwayTeam Name', 8: 'AwayTeam Nickname' })


# --------------------------- Connecting to the database ---------------------------

#method 1
# Connection to ms sql using pyodbc
#driver = 'ODBC DRIVER 13 for SQL Server'
#server = 'servername'
#database = 'dbname'
#username = 'uid'
#password = 'pwd'
#conn  = pyodbc.connect(r'DRIVER={ODBC DRIVER 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
#cursor = conn.cursor() # Request a cursor from the connection that can be used for queries.

#method 2
# connection to ms sql using sqlalchemy 
engine = create_engine('mssql+pyodbc://uid:pwd@hostname')


# --------------------------- Writing to the database ---------------------------

## replace all data in the dabatase - drop and create/ insert
gameDetails.to_sql('GameDetails', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)
gameBoxScore.to_sql('GameBoxScore', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)

playergameSummary.to_sql('PlayerGameSummary', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)
gamePlays.to_sql('GamePlays', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)

teams.to_sql('Teams', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)
players.to_sql('Players', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)

