import requests
import json
import pandas as pd
import numpy as np
import pyodbc
import uuid
from sqlalchemy import create_engine
import time
from datetime import datetime, timedelta
from Settings import *


now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
dateOffset = now - timedelta(days=7)
# yesterday = datetime.today() - timedelta(days=1)
# yesterday = datetime.strptime(yesterday.strftime("%Y-%m-%d"), "%Y-%m-%d")
# minDate = datetime.datetime(2018, 10, 10, 0, 0)
# maxDate = datetime.datetime(2018, 2, 7, 0, 0)

# --------------------------- Connecting to the database ---------------------------


def SQLServerConnection(config):
    conn_str = (
        'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}')

    conn = pyodbc.connect(
        conn_str.format(**config)
    )

    return conn


conn = SQLServerConnection(sqlconfig)
cursor = conn.cursor()

# --------------------------- General Game Data for use in other calls ---------------------------

# initial GET request for full season schedule for the 2017 season
try:
    scheduleRequest = requests.get(Current_Season_url1).json()
except ValueError as e:
    print(e)


games = []
print('Looking back since', dateOffset)

for i in scheduleRequest['lscd']:
    for j in i['mscd']['g']:
        if datetime.strptime(j['gdte'], "%Y-%m-%d") >= dateOffset and datetime.strptime(j['gdte'], "%Y-%m-%d") < now:
            games.append([j['gid']] + [j['gcode']] + [j['an']] + [j['gdte']] + [j['gcode'].split(
                '/')[0]] + [j['v']['tid']] + [j['v']['s']] + [j['h']['tid']] + [j['h']['s']])


# pandas dataframe with all game general data
games = pd.DataFrame(games)
games.columns = ['GameID', 'GameCode', 'Venue', 'Date',
                 'DateString', 'AwayTeamID', 'AwayScore', 'HomeTeamID', 'HomeScore']

gamestbl = games[['GameID', 'GameCode', 'Venue', 'Date', 'DateString']].copy()
print('Games:', len(games))

# cursor.executemany('INSERT INTO Staging_Games([GameID],[GameCode],[Venue],[Date],[DateString],[AwayTeamID],[AwayScore],[HomeTeamID],[HomeScore]) VALUES(?,?,?,?,?,?,?,?,?)', games.values.tolist())

# --------------------------- Game Summary per Player per Game ---------------------------
# game summary data by player by game, looping through all gameIDs up till today
gameSummaryStats = []
url2 = Current_Season_url2
for i in games['GameID']:
    try:
        gamedetailRequest = requests.get(url2 + i + '_gamedetail.json')
        print(i, str(gamedetailRequest.status_code))
        # gamedetailRequest.raise_for_status()
        gamedetailRequest = gamedetailRequest.json()
        gameSummaryStats.append(gamedetailRequest)
    except ValueError as e:
        print(i, e)


# condensed version using function to call game stats for vls and hls
def getSummary(prop, summaries, gameList, idList):
    for a in gameSummaryStats:
        for b in [a['g']]:
            if 'pstsg' not in b[prop]:
                print('issue with game:', b['gid'])
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

#vls_Id = pd.DataFrame(vls_Id)
#hls_Id = pd.DataFrame(hls_Id)
#game_vls['Id'] = vls_Id
#game_hls['Id'] = hls_Id

gameStaging = [game_vls, game_hls]
playergameSummary = pd.concat(gameStaging)  # final dataframe
playergameSummary['Id'] = None

playergameSummary.columns = ['Ast', 'Blk', 'Blka', 'Court', 'Dreb', 'Fbpts', 'Fbptsa', 'Fbptsm', 'Fga', 'Fgm', 'Fn', 'Fta', 'Ftm', 'GameID', 'Ln', 'Memo', 'Mid', 'Min',
                             'Num', 'Oreb', 'Pf', 'PlayerID', 'Pip', 'Pipa', 'Pipm', 'Pm', 'Pos', 'Pts', 'Reb', 'Sec', 'Status', 'Stl', 'Ta', 'Tf', 'TeamID', 'Totsec', 'Tov', 'Tpa', 'Tpm', 'Id']

# --------------------------- Game Plays - full event breakdown in the game ---------------------------
# game summary data by player by game, looping through all gameIDs up till today

gamePlaybyPlay = []
url3 = Current_Season_url3
for i in games['GameID']:
    try:
        gamePlotRequest = requests.get(url3 + i + '_full_pbp.json')
        print(i, str(gamePlotRequest.status_code))
        # gamePlotRequest.raise_for_status()
        gamePlotRequest = gamePlotRequest.json()
        gamePlaybyPlay.append(gamePlotRequest)
        pass
    except ValueError as e:
        print(i, e)


PlaybyPlay = []
idList = []
for i in gamePlaybyPlay:
    for j in i['g']['pd']:
        for k in j['pla']:
            if 'pla' not in j:
                print('issue with game:', i['g']['gid'])
                pass
            else:
                k['period'] = j['p']
                k['gid'] = i['g']['gid']
                k['mid'] = i['g']['mid']
                PlaybyPlay.append(k)
                idList.append(str(uuid.uuid4()))


gamePlays = pd.DataFrame(PlaybyPlay)  # final dataframe
gamePlays['Id'] = idList

gamePlays.columns = ['ClockTime', 'Description', 'EPId', 'EType', 'Evt', 'GameID', 'HS', 'LocationX',
                     'LocationY', 'MId', 'MType', 'OftId', 'OpId', 'Opt1', 'Opt2', 'Ord', 'Period', 'PlayerID', 'TeamID', 'Vs', 'Id']

# --------------------------- Create Player Team DF ---------------------------

players = pd.DataFrame(
    {'PlayerID': playergameSummary['PlayerID'], 'LastName': playergameSummary['Ln'], 'FirstName': playergameSummary['Fn']})
players = players.dropna(how='any')
players = players.drop_duplicates(['PlayerID'], keep='first')

teams = pd.DataFrame(
    {'TeamID': playergameSummary['TeamID'], 'TeamCode': playergameSummary['Ta']})
teams = teams.drop_duplicates(['TeamID'], keep='first')

# --------------------------- Game Box Score ---------------------------

# game box score descriptons by game, looping through all gameIDs up till today

dateSTR = sorted(set(games['DateString'].values.tolist()))
print(str(len(dateSTR)), 'matchdays found')


gameBoxScore_staging = []
url4 = Current_Season_url4
for i in dateSTR:
    try:
        gameBoxScoreRequest = requests.get(url4 + str(i) + '.json')
        print(i, str(gameBoxScoreRequest.status_code))
        # gameBoxScoreRequest.raise_for_status()
        gameBoxScoreRequest = gameBoxScoreRequest.json()
        gameBoxScore_staging.append(gameBoxScoreRequest)
    except ValueError as e:
        print(i, e)


gameBoxScore = []
for i in gameBoxScore_staging:
    if int(i['result_count']) > 0:
        for j in i['results']:
            if 'Game' and 'GameID' and 'Breakdown' in j:
                #                if len(j['GameID']) == int(10) and j['Breakdown'] is not None:
                gameBoxScore.append([j['Game']] + [j['GameID']] + [j['Breakdown']] + [j['HomeTeam']['triCode']] + [j['HomeTeam']['teamName']] + [
                                    j['HomeTeam']['teamNickname']] + [j['VisitorTeam']['triCode']] + [j['VisitorTeam']['teamName']] + [j['VisitorTeam']['teamNickname']])

gameBoxScore = pd.DataFrame(gameBoxScore)
gameBoxScore = gameBoxScore.rename(columns={0: 'Game', 1: 'GameID', 2: 'BoxScoreBreakdown', 3: 'HomeTeamCode',
                                            4: 'HomeTeamName', 5: 'HomeTeamNickname', 6: 'AwayTeamCode', 7: 'AwayTeamName', 8: 'AwayTeamNickname'})


# --------------------------- Writing to the database ---------------------------
print('---------- Writing to NBA database ----------')

# players.to_sql('Staging_Players', engine, schema='dbo', if_exists='append', index=None, chunksize=10000)
# teams.to_sql('Staging_Teams', engine, schema='dbo', if_exists='append', index=None, chunksize=10000)
# gameBoxScore.to_sql('GameBoxScore', engine, schema='dbo', if_exists='append', index=None, chunksize=10000)
# playergameSummary.to_sql('Staging_PlayerGameSummary', engine, schema='dbo', if_exists='append', index=None, chunksize=10000)
# gamePlays.to_sql('Staging_GamePlays', engine, schema='dbo', if_exists='append', index=None, chunksize=10000)


# Players, Teams, Games
cursor.executemany(
    'INSERT INTO Staging_Players (FirstName, LastName, PlayerID) VALUES(?,?,?)', players.values.tolist())
cursor.execute('''INSERT INTO Players (PlayerID, FirstName, LastName) 
	SELECT PlayerID, FirstName, LastName FROM Staging_Players 
		WHERE NOT EXISTS (SELECT PlayerID, FirstName, LastName FROM Players 
			WHERE Staging_Players.PlayerID=Players.PlayerID)''')


cursor.executemany(
    'INSERT INTO Staging_Teams (TeamCode, TeamID) VALUES(?,?)', teams.values.tolist())
cursor.execute('''INSERT INTO Teams(TeamID,TeamCode) 
	SELECT TeamID,TeamCode FROM Staging_Teams 
		WHERE NOT EXISTS (SELECT TeamID,TeamCode FROM Teams 
			WHERE Staging_Teams.TeamID=Teams.TeamID)''')


cursor.executemany(
    'INSERT INTO Staging_Games([GameID],[GameCode],[Venue],[Date],[DateString]) VALUES(?,?,?,?,?)', gamestbl.values.tolist())

cursor.execute(''' INSERT INTO Games([GameID],[GameCode],[Venue],[Date],[DateString])
    SELECT [GameID],[GameCode],[Venue],[Date],[DateString] FROM Staging_Games
        WHERE NOT EXISTS ( SELECT [GameID],[GameCode],[Venue],[Date],[DateString] FROM Games
            WHERE Staging_Games.[GameID] = Games.[GameID] )''')


cursor.executemany(
    'INSERT INTO Staging_GameBoxScore([Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname]) VALUES(?,?,?,?,?,?,?,?,?)', gameBoxScore.values.tolist())
cursor.execute('''INSERT INTO GameBoxScore([Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname])
    SELECT [Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname] FROM Staging_GameBoxScore
        WHERE NOT EXISTS (SELECT [Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname] FROM GameBoxScore
            WHERE Staging_GameBoxScore.GameID = GameBoxScore.GameID)''')


print('---------- Players, Teams and Games written ----------')


cursor.executemany('INSERT INTO Staging_PlayerGameSummary(Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm,Id) VALUES(?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?, ?,?,?,?)', playergameSummary.values.tolist())

cursor.execute('''INSERT INTO PlayerGameSummary( Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm) 
	SELECT Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm FROM Staging_PlayerGameSummary 
		WHERE NOT EXISTS ( SELECT Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm FROM PlayerGameSummary 
			WHERE Staging_PlayerGameSummary.GameID=PlayerGameSummary.GameID AND Staging_PlayerGameSummary.PlayerID=PlayerGameSummary.PlayerID AND Staging_PlayerGameSummary.TeamID=PlayerGameSummary.TeamID)''')


print('---------- Player Game Summary written ----------')


cursor.executemany('INSERT INTO Staging_GamePlays(ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs,Id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', gamePlays.values.tolist())

cursor.execute('''INSERT INTO GamePlays(ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs) 
	SELECT ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs FROM Staging_GamePlays 
		WHERE NOT EXISTS (SELECT ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs FROM GamePlays 
			WHERE Staging_GamePlays.TeamID=GamePlays.TeamID AND Staging_GamePlays.GameID=GamePlays.GameID AND Staging_GamePlays.PlayerID=GamePlays.PlayerID AND Staging_GamePlays.Evt=GamePlays.Evt)''')


print('---------- Game Plays written ----------')

cursor.execute('DELETE FROM Staging_Players')
cursor.execute('DELETE FROM Staging_Teams')
cursor.execute('DELETE FROM Staging_Games')
cursor.execute('DELETE FROM Staging_GamePlays')
cursor.execute('DELETE FROM Staging_PlayerGameSummary')

conn.commit()
print('---------- All Staging data deleted ----------')
