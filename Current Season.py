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
from Links import *
import mysql.connector



# get today's date, for use later when getting Id's
import time
from datetime import datetime, timedelta

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
yesterday = datetime.today() - timedelta(days=1)
yesterday = datetime.strptime(yesterday.strftime("%Y-%m-%d"), "%Y-%m-%d")

import datetime
minDate = datetime.datetime(2018, 2, 9, 0, 0)
#maxDate = datetime.datetime(2018, 2, 7, 0, 0)


# --------------------------- Connecting to the database ---------------------------
# connection to ms sql using sqlalchemy 

# ms_sql = ms_sql
# engine = create_engine('mssql+pyodbc://' + ms_sql)


engine = create_engine('mysql+mysqlconnector://' + str(my_sql))
cursor = engine.connect()


# initial GET request for full season schedule for the 2017 season
url1 = Current_Season_url1
try:
    scheduleRequest = requests.get(url1).json()
except ValueError:
    print('JSON decoding failed')

type(scheduleRequest)



# --------------------------- General Game Data for use in other calls ---------------------------

# empty lists to append empty lists with general game details
gameIDs = []
gameCode = []
venue = []
gameDate = []


from datetime import datetime, timedelta
for i in scheduleRequest['lscd']:
    for j in i['mscd']['g']:
        # if datetime.strptime(j['gdte'], "%Y-%m-%d") >= minDate and datetime.strptime(j['gdte'], "%Y-%m-%d") < now:
        if datetime.strptime(j['gdte'], "%Y-%m-%d") < now:
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
url2 = Current_Season_url2
for i in gameDetails['GameID']:
    try:
        gamedetailRequest = requests.get(url2 + i + '_gamedetail.json')
        print(i + ' - ' + str(gamedetailRequest.status_code))
        #gamedetailRequest.raise_for_status()
        gamedetailRequest = gamedetailRequest.json()
        gameSummaryStats.append(gamedetailRequest)
    except ValueError:
        print(i + ' - Game caused decoding fail')


# condensed version using function to call game stats for vls and hls
def getSummary(prop, summaries, gameList, idList):
    for a in gameSummaryStats:
        for b in [a['g']]:
            if 'pstsg' not in b[prop]:
                print('issue with game: ' + b['gid'])
                pass
            else:
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
url3 = Current_Season_url3
for i in gameDetails['GameID']:
    try:
        gamePlotRequest = requests.get(url3 + i + '_full_pbp.json')
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
            if 'pla' not in j:
                print('issue with game: ' + i['g']['gid'])
                pass
            else:
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

   
# --------------------------- Game Box Score ---------------------------


# game box score descriptons by game, looping through all gameIDs up till today
dateSTR = sorted(set(dateSTR))
print(str(len(dateSTR)) + ' matchdays found')


gameBoxScore_staging = []
url4 = Current_Season_url4
for i in dateSTR:
    try:
        gameBoxScoreRequest = requests.get(url4 + str(i) + '.json')
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


# --------------------------- Writing to the database ---------------------------


# players.to_sql('Staging_Players', engine, flavor=None, schema='nbadata', if_exists='append', index=None, chunksize=10000)

# cursor.execute('''INSERT INTO Players (PlayerID, FirstName, LastName) 
# 	SELECT PlayerID, FirstName, LastName FROM Staging_Players 
# 		WHERE NOT EXISTS (SELECT PlayerID, FirstName, LastName FROM Players 
# 			WHERE Staging_Players.PlayerID=Players.PlayerID)''')

# cursor.execute('DELETE FROM Staging_Players')




# teams.to_sql('Staging_Teams', engine, flavor=None, schema='nbadata', if_exists='append', index=None, chunksize=10000)

# cursor.execute('''INSERT INTO Teams(TeamID,TeamCode) 
# 	SELECT TeamID,TeamCode FROM Staging_Teams 
# 		WHERE NOT EXISTS (SELECT TeamID,TeamCode FROM Teams 
# 			WHERE Staging_Teams.TeamID=Teams.TeamID)''')

# cursor.execute('DELETE FROM Staging_Teams')




# gameDetails.to_sql('Staging_Games', engine, flavor=None, schema='nbadata', if_exists='append', index=None)

# cursor.execute('''INSERT INTO Games(GameID, Date, DateString, GameCode, Venue) 
# 	SELECT GameID, Date, DateString, GameCode, Venue FROM Staging_Games 
#         WHERE NOT EXISTS (SELECT GameID, Date, DateString, GameCode, Venue FROM Games 
#             WHERE Staging_Games.GameID=Games.GameID)''')

# cursor.execute('DELETE FROM Staging_Games')


# --------------------------- Game Summary per Player per Game ---------------------------

# playergameSummary.to_sql('Staging_PlayerGameSummary', engine, flavor=None, schema='nbadata', if_exists='append', index=None, chunksize=10000)

# cursor.execute('''INSERT INTO PlayerGameSummary( Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm) 
# 	SELECT Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm FROM Staging_PlayerGameSummary 
# 		WHERE NOT EXISTS ( SELECT Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm FROM PlayerGameSummary 
# 			WHERE Staging_PlayerGameSummary.GameID=PlayerGameSummary.GameID AND Staging_PlayerGameSummary.PlayerID=PlayerGameSummary.PlayerID AND Staging_PlayerGameSummary.TeamID=PlayerGameSummary.TeamID)''')

# cursor.execute('DELETE FROM Staging_PlayerGameSummary')


# --------------------------- Game Plays ---------------------------

# gamePlays.to_sql('Staging_GamePlays', engine, flavor=None, schema='nbadata', if_exists='append', index=None, chunksize=10000)

# cursor.execute('''INSERT INTO GamePlays(ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs) 
# 	SELECT ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs FROM Staging_GamePlays 
# 		WHERE NOT EXISTS (SELECT ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs FROM GamePlays 
# 			WHERE Staging_GamePlays.TeamID=GamePlays.TeamID AND Staging_GamePlays.GameID=GamePlays.GameID AND Staging_GamePlays.PlayerID=GamePlays.PlayerID AND Staging_GamePlays.Evt=GamePlays.Evt)''')

# cursor.execute('DELETE FROM Staging_GamePlays')

# cursor.execute('COMMIT;')


