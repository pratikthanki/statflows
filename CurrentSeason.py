import requests
import json
import logging
import pyodbc
from sqlalchemy import create_engine
import time
from datetime import datetime, timedelta
from Settings import Current_Season_url1, Current_Season_url2, Current_Season_url3, Current_Season_url4, sql_config, \
    sql_server_connection


def get_data(base_url):
    try:
        rqst = requests.request('GET', base_url)
        print(str(rqst.status_code), base_url)
        return rqst.json()
    except ValueError as e:
        print(e)


print(datetime.utcnow())

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
date_offset = now - timedelta(days=30)

game_rqst = get_data(Current_Season_url1)

games = []
for i in game_rqst['lscd']:
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

game_detail = []
game_pbp = []
for i in list_of_games:
    try:
        summary_url = '{0}{1}_gamedetail.json'.format(Current_Season_url2, i)
        summary_data = get_data(base_url=summary_url)
        game_detail.append(summary_data)

        pbp_url = '{0}{1}_full_pbp.json'.format(Current_Season_url3, i)
        pbp_data = get_data(base_url=pbp_url)
        game_pbp.append(pbp_data)
    except ValueError as e:
        print(i, e)


def game_detail_stats(prop):
    lst = []
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
                    lst.append(c)

    return lst


game_vls = game_detail_stats('vls')
game_hls = game_detail_stats('hls')
player_game_summary = game_vls + game_hls

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

list_of_game_dates = [i['DateString'] for i in games]
match_days = sorted(set(list_of_game_dates))

print(str(len(match_days)), 'match days found')

box_scores = []
for i in match_days:
    try:
        url = '{0}{1}.json'.format(Current_Season_url4, i)
        data = get_data(base_url=url)
        box_scores.append(data)
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

# --------------------------- Writing to the database ---------------------------
print('---------- Inserting records to the database ----------')

conn = sql_server_connection(sql_config)
cursor = conn.cursor()

player_table_columns = ', '.join(['PlayerID', 'LastName', 'FirstName'])
team_table_columns = ', '.join(['TeamCode', 'TeamID'])
game_table_columns = ', '.join(['HomeScore', 'AwayTeamID', 'HomeTeamID', 'GameID', 'Date', 'AwayScore', 'Venue', \
                                'GameCode', 'DateString'])

cursor.executemany(
    'INSERT INTO Staging_Players ({0}) VALUES(?,?,?)'.format(player_table_columns),
    [player.values() for player in players])
cursor.execute(
    'INSERT INTO Players ({0}) SELECT {0} FROM Staging_Players WHERE NOT EXISTS (SELECT {0} FROM Players WHERE Staging_Players.PlayerID=Players.PlayerID)'.format(
        player_table_columns))

cursor.executemany(
    'INSERT INTO Staging_Teams ({0}) VALUES(?,?)'.format(team_table_columns), [team.values() for team in teams])
cursor.execute(
    'INSERT INTO Teams({0}) SELECT {0} FROM Staging_Teams WHERE NOT EXISTS (SELECT {0} FROM Teams WHERE Staging_Teams.TeamID=Teams.TeamID)'.format(
        team_table_columns))

# cursor.executemany(
#     'INSERT INTO Staging_Games([GameID],[GameCode],[Venue],[Date],[DateString]) VALUES(?,?,?,?,?)',
#     gamestbl.values.tolist())
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
conn.commit()
print('---------- All Staging data deleted ----------')
