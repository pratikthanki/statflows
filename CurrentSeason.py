import requests
import json
import pandas as pd
import numpy as np
import pyodbc
import uuid
import json
from sqlalchemy import create_engine
import time
from datetime import datetime, timedelta
from Settings import Current_Season_url1, Current_Season_url2, Current_Season_url3, Current_Season_url4, sqlconfig

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
date_offset = now - timedelta(days=30)


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

try:
    games_rqst = requests.request('GET', Current_Season_url1)
    games_rqst = games_rqst.json()
except ValueError as e:
    print(e)

games = []
for i in games_rqst['lscd']:
    for j in i['mscd']['g']:
        if date_offset <= datetime.strptime(j['gdte'], "%Y-%m-%d") < now:
            games.append({
                'GameID': j['gid'],
                'GameCode': j['gcode'],
                'Venue': j['an'],
                'Date': j['gdte'],
                'DateString': j['gcode'].split('/')[0],
                'AwayTeamID': j['v']['tid'],
                'AwayScore': j['v']['s'],
                'HomeTeamID': j['h']['tid'],
                'HomeScore': j['h']['s']
            })

list_of_games = [i['GameID'] for i in games]

# --------------------------- Game Summary per Player per Game ---------------------------

game_detail = []
for i in list_of_games:
    try:
        game_detail_rqst = requests.request('GET', '{0}{1}_gamedetail.json'.format(Current_Season_url2, i))
        print(i, str(game_detail_rqst.status_code), '{0}{1}_gamedetail.json'.format(Current_Season_url2, i))
        game_detail_rqst = game_detail_rqst.json()
        game_detail.append(game_detail_rqst)
    except ValueError as e:
        print(i, e)


# # condensed version using function to call game stats for vls and hls
def game_detail_stats(prop):
    empty_list = []
    for a in game_detail:
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
                    empty_list.append(c)

    return empty_list


game_vls = game_detail_stats('vls')
game_hls = game_detail_stats('hls')

player_game_summary = game_vls + game_hls

# --------------------------- Game Plays - full event breakdown in the game ---------------------------

game_pbp = []
for i in list_of_games:
    try:
        game_pbp_rqst = requests.request('GET', '{0}{1}_full_pbp.json'.format(Current_Season_url3, i))
        print(i, str(game_pbp_rqst.status_code), '{0}{1}_full_pbp.json'.format(Current_Season_url3, i))
        game_pbp_rqst = game_pbp_rqst.json()
        game_pbp.append(game_pbp_rqst)
        pass
    except ValueError as e:
        print(i, e)

play_by_play = []
for i in game_pbp:
    for j in i['g']['pd']:
        for k in j['pla']:
            if 'pla' not in j:
                print('issue with game:', i['g']['gid'])
                pass
            else:
                k['period'] = j['p']
                k['gid'] = i['g']['gid']
                k['mid'] = i['g']['mid']
                play_by_play.append(k)


# --------------------------- Create Player + Team Dicts ---------------------------

def remove_duplicates(lst):
    return [dict(t) for t in {tuple(d.items()) for d in lst}]


players = [
    {'PlayerID': i['pid'], 'LastName': i['ln'], 'FirstName': i['fn']} for i in player_game_summary
]

teams = [
    {'TeamID': i['tid'], 'TeamCode': i['ta']} for i in player_game_summary
]

players = remove_duplicates(players)
teams = remove_duplicates(teams)

# --------------------------- Game Box Score ---------------------------

# game box score descriptons by game, looping through all gameIDs up till today

list_of_game_dates = [i['DateString'] for i in games]

match_days = sorted(set(list_of_game_dates))
print(str(len(match_days)), 'match days found')

box_scores = []
for i in match_days:
    try:
        box_score_rqst = requests.request('GET', '{0}{1}.json'.format(Current_Season_url4, i))
        print(i, str(box_score_rqst.status_code), '{0}{1}.json'.format(Current_Season_url4, i))
        box_score_rqst = box_score_rqst.json()
        box_scores.append(box_score_rqst)
    except ValueError as e:
        print(i, e)

game_box_scores = []
for i in box_scores:
    if int(i['result_count']) > 0:
        for j in i['results']:
            if 'Game' and 'GameID' and 'Breakdown' in j:
                game_box_scores.append({
                    'Game': [j['Game']],
                    'GameID': [j['GameID']],
                    'BoxScoreBreakdown': [j['Breakdown']],
                    'HomeTeamCode': [j['HomeTeam']['triCode']],
                    'HomeTeamName': [j['HomeTeam']['teamName']],
                    'HomeTeamNickname': [j['HomeTeam']['teamNickname']],
                    'AwayTeamCode': [j['VisitorTeam']['triCode']],
                    'AwayTeamName': [j['VisitorTeam']['teamName']],
                    'AwayTeamNickname': [j['VisitorTeam']['teamNickname']]
                })

print(game_box_scores)


# # --------------------------- Writing to the database ---------------------------
# print('---------- Writing to NBA database ----------')
#
# print(players.values.tolist())

# Players, Teams, Games
# cursor.executemany(
#     'INSERT INTO Staging_Players (FirstName, LastName, PlayerID) VALUES(?,?,?)', players.values.tolist())
# cursor.execute('''INSERT INTO Players (PlayerID, FirstName, LastName)
# 	SELECT PlayerID, FirstName, LastName FROM Staging_Players
# 		WHERE NOT EXISTS (SELECT PlayerID, FirstName, LastName FROM Players
# 			WHERE Staging_Players.PlayerID=Players.PlayerID)''')
#
# cursor.executemany(
#     'INSERT INTO Staging_Teams (TeamCode, TeamID) VALUES(?,?)', teams.values.tolist())
# cursor.execute('''INSERT INTO Teams(TeamID,TeamCode)
# 	SELECT TeamID,TeamCode FROM Staging_Teams
# 		WHERE NOT EXISTS (SELECT TeamID,TeamCode FROM Teams
# 			WHERE Staging_Teams.TeamID=Teams.TeamID)''')
#
# cursor.executemany(
#     'INSERT INTO Staging_Games([GameID],[GameCode],[Venue],[Date],[DateString]) VALUES(?,?,?,?,?)',
#     gamestbl.values.tolist())
#
# cursor.execute(''' INSERT INTO Games([GameID],[GameCode],[Venue],[Date],[DateString])
#     SELECT [GameID],[GameCode],[Venue],[Date],[DateString] FROM Staging_Games
#         WHERE NOT EXISTS ( SELECT [GameID],[GameCode],[Venue],[Date],[DateString] FROM Games
#             WHERE Staging_Games.[GameID] = Games.[GameID] )''')
#
# cursor.executemany(
#     'INSERT INTO Staging_GameBoxScore([Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname]) VALUES(?,?,?,?,?,?,?,?,?)',
#     game_box_scores.values.tolist())
# cursor.execute('''INSERT INTO GameBoxScore([Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname])
#     SELECT [Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname] FROM Staging_GameBoxScore
#         WHERE NOT EXISTS (SELECT [Game],[GameID],[BoxScoreBreakdown],[HomeTeamCode],[HomeTeamName],[HomeTeamNickname],[AwayTeamCode],[AwayTeamName],[AwayTeamNickname] FROM GameBoxScore
#             WHERE Staging_GameBoxScore.GameID = GameBoxScore.GameID)''')
#
# print('---------- Players, Teams and Games written ----------')
#
# cursor.executemany(
#     'INSERT INTO Staging_PlayerGameSummary(Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm,Id) VALUES(?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?,?,?,?, ?,?,?,?)',
#     player_game_summary.values.tolist())
#
# cursor.execute('''INSERT INTO PlayerGameSummary( Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm)
# 	SELECT Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm FROM Staging_PlayerGameSummary
# 		WHERE NOT EXISTS ( SELECT Ast,Blk,Blka,Court,Dreb,Fbpts,Fbptsa,Fbptsm,Fga,Fgm,Fn,Fta,Ftm,GameID,Ln,Memo,Mid,Min,Num,Oreb,Pf,PlayerID,Pip,Pipa,Pipm,Pm,Pos,Pts,Reb,Sec,Status,Stl,Ta,Tf,TeamID,Totsec,Tov,Tpa,Tpm FROM PlayerGameSummary
# 			WHERE Staging_PlayerGameSummary.GameID=PlayerGameSummary.GameID AND Staging_PlayerGameSummary.PlayerID=PlayerGameSummary.PlayerID AND Staging_PlayerGameSummary.TeamID=PlayerGameSummary.TeamID)''')
#
# print('---------- Player Game Summary written ----------')
#
# cursor.executemany(
#     'INSERT INTO Staging_GamePlays(ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs,Id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
#     game_plays.values.tolist())
#
# cursor.execute('''INSERT INTO GamePlays(ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs)
# 	SELECT ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs FROM Staging_GamePlays
# 		WHERE NOT EXISTS (SELECT ClockTime,Description,EPId,EType,Evt,GameID,HS,LocationX,LocationY,MId,MType,OftId,OpId,Opt1,Opt2,Ord,Period,PlayerID,TeamID,Vs FROM GamePlays
# 			WHERE Staging_GamePlays.TeamID=GamePlays.TeamID AND Staging_GamePlays.GameID=GamePlays.GameID AND Staging_GamePlays.PlayerID=GamePlays.PlayerID AND Staging_GamePlays.Evt=GamePlays.Evt)''')
#
# print('---------- Game Plays written ----------')
#
# cursor.execute('TRUNCATE TABLE Staging_Players')
# cursor.execute('TRUNCATE TABLE Staging_Teams')
# cursor.execute('TRUNCATE TABLE Staging_Games')
# cursor.execute('TRUNCATE TABLE Staging_GamePlays')
# cursor.execute('TRUNCATE TABLE Staging_PlayerGameSummary')
#
# conn.commit()
# print('---------- All Staging data deleted ----------')
