import os
import sys
import requests
import json
import pandas as pd
import numpy as np
import pyodbc
import uuid
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError 



# get today's date, for use later when getting Id's
import time
from datetime import datetime, timedelta

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
yesterday = datetime.today() - timedelta(days=1)
yesterday = datetime.strptime(yesterday.strftime("%Y-%m-%d"), "%Y-%m-%d")

import datetime
myDate = datetime.datetime(2017, 12, 22, 0, 0)



# initial GET request for full season schedule for the 2017 season
try:
    scheduleRequest = requests.get(r'URL').json()
except ValueError:
    print('JSON decoding failed')

#type(scheduleRequest)



# --------------------------- General Game Data for use in other calls ---------------------------

# empty lists to append empty lists with general game details
gameIDs = []
gameCode = []
venue = []
gameDate = []


from datetime import datetime, timedelta
for i in scheduleRequest['lscd']:
    for j in i['mscd']['g']:
        if datetime.strptime(j['gdte'], "%Y-%m-%d") >= myDate and datetime.strptime(j['gdte'], "%Y-%m-%d") < now: # !! check to see correct date is being applied !!
            gameIDs.append(j['gid'])
            gameCode.append(j['gcode'])
            venue.append(j['an'])
            gameDate.append(j['gdte'])
           

dateSTR = []
for line in gameCode:
    dateSTR.append(line.split('/')[0])

# pandas dataframe with all game general data
gameDetails = pd.DataFrame({'GameID':gameIDs, 'GameCode':gameCode, 'Venue':venue, 'Date':gameDate, 'DateString': dateSTR}) # final dataframe
print(str(len(gameIDs)) + ' Game IDs Found')



# --------------------------- Game Summary per Player per Game ---------------------------

# game summary data by player by game, looping through all gameIDs up till today
gameSummaryStats = [] 
for i in gameDetails['GameID']:
    try:
        gamedetailRequest = requests.get(r'URL' + i + '_gamedetail.json')
        print(i + ' - ' + str(gamedetailRequest.status_code))
        #gamedetailRequest.raise_for_status()
        gamedetailRequest = gamedetailRequest.json()
        gameSummaryStats.append(gamedetailRequest)
    except ValueError:
        print(i + ' - Game caused decoding fail')

#print(gameSummaryStats) # list

# condensed version using function to call game stats for vls and hls
def getSummary(prop, summaries, gameList, idList):
    for a in gameSummaryStats:
        for b in [a['g']]:
            for c in b[prop]['pstsg']:
                    c['gid'] = b['gid']
                    c['mid'] = b['mid']
                    c['tid'] = b[prop]['tid']
                    c['ta'] = b[prop]['ta']
                    idList.append(str(uuid.uuid4()))
                    gameList.append(c)



game_vls = []
game_hls = []
vls_Id = []
hls_Id = []
getSummary('vls', gameSummaryStats, game_vls, vls_Id)
getSummary('hls', gameSummaryStats, game_hls, hls_Id)

game_vls = pd.DataFrame(game_vls)
game_hls = pd.DataFrame(game_hls)

vls_Id = pd.DataFrame(vls_Id)
hls_Id = pd.DataFrame(hls_Id)

game_vls['Id'] = vls_Id
game_hls['Id'] = hls_Id


gameStaging = [game_vls, game_hls]
playergameSummary = pd.concat(gameStaging) # final dataframe
playergameSummary.dtypes


playergameSummary.columns = ['Ast','Blk', 'Blka', 'Court', 'Dreb', 'Fbpts', 'Fbptsa', 'Fbptsm', 'Fga', 'Fgm', 'Fn', 'Fta', 'Ftm', 'GameID', 'Ln', 'Memo', 'Mid', 'Min', 'Num', 'Oreb', 'Pf', 'PlayerID', 'Pip', 'Pipa', 'Pipm', 'Pm', 'Pos', 'Pts', 'Reb', 'Sec', 'Status', 'Stl', 'Ta', 'Tf', 'TeamID', 'Totsec', 'Tov', 'Tpa', 'Tpm', 'Id']


# --------------------------- Game Plays - full event breakdown in the game ---------------------------

# game summary data by player by game, looping through all gameIDs up till today

gamePlaybyPlay = []
for i in gameDetails['GameID']:
    try:
        gamePlotRequest = requests.get(r'URL' + i + '_full_pbp.json')
        print(i + ' - ' + str(gamePlotRequest.status_code))
        #gamePlotRequest.raise_for_status()
        gamePlotRequest = gamePlotRequest.json()
        gamePlaybyPlay.append(gamePlotRequest)
        pass
    except ValueError:
        print(i + ' - Game caused decoding fail')

    
#print(gamePlaybyPlay) # list
#gamePlaybyPlay[0]['g']['pd'][0]['p']

PlaybyPlay = []
idList = []
for i in gamePlaybyPlay:
    for j in i['g']['pd']:
        for k in j['pla']:
            k['period'] = j['p']
            k['gid'] = i['g']['gid']
            k['mid'] = i['g']['mid']
            PlaybyPlay.append(k)
            idList.append(str(uuid.uuid4()))


gamePlays = pd.DataFrame(PlaybyPlay) # final dataframe
gamePlays['Id'] = idList
gamePlays.dtypes

gamePlays.columns = ['ClockTime', 'Description', 'EPId', 'EType', 'Evt', 'GameID', 'HS', 'LocationX', 'LocationY', 'MId', 'MType', 'OftId', 'OpId', 'Opt1', 'Opt2', 'Ord', 'Period', 'PlayerID', 'TeamID', 'Vs', 'Id']

# --------------------------- Create Player Team DF ---------------------------

players = pd.DataFrame({'PlayerID': playergameSummary['PlayerID'], 'LastName': playergameSummary['Ln'], 'FirstName': playergameSummary['Fn']})
players = players.dropna(how='any')
players = players.drop_duplicates(['PlayerID'], keep='first')


teams = pd.DataFrame({'TeamID': playergameSummary['TeamID'], 'TeamCode': playergameSummary['Ta']})
teams = teams.drop_duplicates(['TeamID'], keep='first')



# --------------------------- Player Info Rwquest ---------------------------

#headers = {'user-agent': 'PostmanRuntime/6.4.1'}

#playerInfo = []
#for i in players['Player ID']:
#    playerInfoRequest = requests.get(r'URL' + str(i), headers=headers)
#    #playerInfoRequest.raise_for_status()
#    playerInfoRequest = playerInfoRequest.json()
#    playerInfo.append(playerInfoRequest)

    
# --------------------------- Game Box Score ---------------------------


# game box score descriptons by game, looping through all gameIDs up till today
dateSTR = sorted(set(dateSTR))
print(str(len(dateSTR)) + ' matchdays found')


gameBoxScore_staging = [] 
for i in dateSTR:
    try:
        gameBoxScoreRequest = requests.get(r'URL' + str(i) + '.json')
        print(i + ' - ' + str(gameBoxScoreRequest.status_code))
        #gameBoxScoreRequest.raise_for_status()
        gameBoxScoreRequest = gameBoxScoreRequest.json()
        gameBoxScore_staging.append(gameBoxScoreRequest)
    except ValueError:
        print(i + ' - Game caused decoding fail')

    
#print(gameBoxScore_staging) # list

gameBoxScore = []
for i in gameBoxScore_staging:
    if int(i['result_count']) > 0:
        for j in i['results']:
            if 'Game' and 'GameID' and 'Breakdown' in j:
#                if len(j['GameID']) == int(10) and j['Breakdown'] is not None:
                    gameBoxScore.append([j['Game']] + [j['GameID']] + [j['Breakdown']] + [j['HomeTeam']['triCode']] + [j['HomeTeam']['teamName']] + [j['HomeTeam']['teamNickname']] + [j['VisitorTeam']['triCode']] + [j['VisitorTeam']['teamName']] + [j['VisitorTeam']['teamNickname']])

gameBoxScore = pd.DataFrame(gameBoxScore)
gameBoxScore = gameBoxScore.rename(columns={0: 'Game', 1: 'GameID', 2: 'BoxScoreBreakdown', 3: 'HomeTeamCode', 4: 'HomeTeamName', 5: 'HomeTeamNickname', 6: 'AwayTeamCode', 7: 'AwayTeamName', 8: 'AwayTeamNickname' })


# --------------------------- Connecting to the database ---------------------------

#method 1
# Connection to ms sql using pyodbc
#driver = 'ODBC DRIVER 13 for SQL Server'
#server = 'nbadata.database.windows.net, 1433'
#database = 'nbadata'
#username = 'nbadata'
#password = 'Pa$$w0rd123'
#conn  = pyodbc.connect(r'DRIVER={ODBC DRIVER 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
#cursor = conn.cursor() # Request a cursor from the connection that can be used for queries.

#method 2
# connection to ms sql using sqlalchemy 
engine = create_engine('mssql+pyodbc://db:pwd@uid')


# --------------------------- Writing to the database ---------------------------

# append all data in the dabatase - drop and create/ insert

gameDetails.to_sql('Games', engine, flavor=None, schema='dbo', if_exists='append', index=None)
gameBoxScore.to_sql('GameBoxScore', engine, flavor=None, schema='dbo', if_exists='append', index=None)
playergameSummary.to_sql('PlayerGameSummary', engine, flavor=None, schema='dbo', if_exists='append', index=None)
gamePlays.to_sql('GamePlays', engine, flavor=None, schema='dbo', if_exists='append', index=None, chunksize=10000)


#teams.to_sql('Teams', engine, flavor=None, schema='dbo', if_exists='append', index=None)
#players.to_sql('Players', engine, flavor=None, schema='dbo', if_exists='append', index=None)

