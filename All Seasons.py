import requests
import json 
import pandas as pd
import pyodbc
import uuid

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import *

from Links import *


ms_sql = ms_sql
# engine = create_engine('mssql+pyodbc://' + ms_sql)


mysql = my_sql
# engine = create_engine('mysql+mysqlconnector://' + my_sql)


cursor = engine.connect()



teams = ['hawks', 'celtics', 'cavaliers', 'pelicans', 'bulls', 'mavericks', 'nuggets', 'warriors', 'rockets', 'clippers', 'lakers', 'heat', 'bucks', 'timberwolves', 'nets', 'knicks', 'magic', 'pacers', '76ers', 'suns', 'trail_blazers', 'kings', 'spurs', 'thunder', 'raptors', 'jazz', 'grizzlies', 'wizards', 'pistons', 'hornets']



schedule_json = []
url1 = All_Seasons_url1
for x in range(2014, 2015):
    for t in teams:
        try:
            scheduleRequest = requests.get(url1 + str(x) + '/teams/' + str(t) + '_schedule.json')
            print(str(x) + ' ' + str(t) + ' request complete')
            scheduleRequest = scheduleRequest.json()
            schedule_json.append([scheduleRequest])
        except ValueError:
            print(str(x) + ' ' + str(t) + ' JSON decoding failed')


# empty lists to append empty lists with general game details
gameIDs = []
gameCode = []
venue = []
gameDate = []


import datetime
minDate = datetime.datetime(2016, 10, 24, 0, 0)
maxDate = datetime.datetime(2017, 6, 19, 0, 0)

from datetime import datetime, timedelta
for i in schedule_json:
    for j in i:
        for k in j['gscd']['g']:
#            if datetime.strptime(k['gdte'], '%Y-%m-%d') >= minDate and datetime.strptime(k['gdte'], '%Y-%m-%d') <= maxDate:
                gameIDs.append(k['gid'])
                gameCode.append(k['gcode'])
                venue.append(k['an'])
                gameDate.append(k['gdte'])
            
dateString = []
for line in gameCode:
    dateString.append(line.split('/')[0])

# pandas dataframe with all game general data
gameDetails = pd.DataFrame({'GameID':gameIDs, 'GameCode':gameCode, 'Venue':venue, 'Date':gameDate, 'DateString': dateString}) # final dataframe
gameDetails = gameDetails.drop_duplicates()
print(str(len(gameDetails['GameID'])) + ' Game IDs Found')


# --------------------------------------------------------------------------------------------------------------

#gameDetails.to_sql('Staging_Games', engine, flavor=None, schema='dbo', if_exists='append', index=None)

#cursor.execute('''INSERT INTO [Games]([GameID], [Date], [DateString], [GameCode], [Venue]) 
#	SELECT [GameID], [Date], [DateString], [GameCode], [Venue] FROM [Staging_Games] WHERE NOT EXISTS (SELECT [GameID], [Date], [DateString], [GameCode],[Venue] FROM [dbo].[Games] WHERE [Staging_Games].[GameID]=[Games].GameID)''')

#cursor.execute('DELETE FROM Staging_Games')
#conn.commit()


# ------------------------------------------------------------ Player Game Summary ------------------------------------------------------------

# game summary data by player by game, looping through all gameIDs up till today
gameSummaryStats = []
url2 = All_Seasons_url2
for x in range(2014, 2015):
    for i in gameDetails['GameID']:
        try:
            gamedetailRequest = requests.get(url2 + str(x) + '/scores/gamedetail/' + str(i) + '_gamedetail.json')
            print(i + ' ' + str(gamedetailRequest.status_code))
            #gamedetailRequest.raise_for_status()
            gamedetailRequest = gamedetailRequest.json()
            gameSummaryStats.append(gamedetailRequest)
        except ValueError:
            print(i + ' Game caused decoding fail')

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

#playergameSummary.columns = ['Ast','Blk', 'Blka', 'Court', 'Dreb', 'Fbpts', 'Fbptsa', 'Fbptsm', 'Fga', 'Fgm', 'Fn', 'Fta', 'Ftm', 'GameID', 'Ln', 'Mid', 'Min', 'Num', 'Oreb', 'Pf', 'PlayerID', 'Pip', 'Pipa', 'Pipm', 'Pm', 'Pos', 'Pts', 'Reb', 'Status', 'Stl', 'Ta', 'Tf', 'TeamID', 'Tov', 'Tpa', 'Tpm', 'Id']

#playergameSummary['Memo'] = None
#playergameSummary['Sec'] = None
#playergameSummary['Totsec'] = None



# ------------------------------------------------------------ Create Player Team DF ------------------------------------------------------------

players = pd.DataFrame({'PlayerID': playergameSummary['PlayerID'], 'LastName': playergameSummary['Ln'], 'FirstName': playergameSummary['Fn']})
players = players.sort_values(['PlayerID'])
players = players.drop_duplicates(['PlayerID'], keep='first')


playerTable = 'Players'
playerStaging = 'Staging_Players'
playerQuery = '[PlayerID], [FirstName], [LastName]'

#players.to_sql(playerStaging, engine, flavor=None, schema='dbo', if_exists='append', index=None)

#cursor.execute('''INSERT INTO [''' + playerTable + '''](''' + playerQuery + ''') 
#	SELECT ''' + playerQuery + ''' FROM [''' + playerStaging + '''] WHERE NOT EXISTS (SELECT ''' + playerQuery + ''' FROM [dbo].[''' + playerTable + '''] WHERE [''' + playerStaging + '''].[PlayerID]=['''+ playerTable +'''].PlayerID)''')

#cursor.execute('DELETE FROM ' + playerStaging)
#conn.commit()




teams = pd.DataFrame({'TeamID': playergameSummary['TeamID'], 'TeamCode': playergameSummary['Ta']})
teams = teams.drop_duplicates(['TeamID'], keep='first')


teamTable = 'Teams'
teamStaging = 'Staging_Teams'
teamQuery = '[TeamID], [TeamCode]'

#teams.to_sql(teamStaging, engine, flavor=None, schema='dbo', if_exists='append', index=None)

#cursor.execute('''INSERT INTO [''' + teamTable + '''](''' + teamQuery + ''') 
#	SELECT ''' + teamQuery + ''' FROM [''' + teamStaging + '''] WHERE NOT EXISTS (SELECT ''' + teamQuery + ''' FROM [dbo].[''' + teamTable + '''] WHERE [''' + teamStaging + '''].[TeamID]=['''+ teamTable +'''].[TeamID])''')

#cursor.execute('DELETE FROM ' + teamStaging)
#conn.commit()




# ------------------------------------------------------------ Game Plays ------------------------------------------------------------

# game summary data by player by game, looping through all gameIDs up till today

gamePlaybyPlay = []
url3 = All_Seasons_url3
for x in range(2014, 2018):
    for i in gameDetails['GameID']:
        try:
            gamePlotRequest = requests.get(url3 + str(x) + '/scores/pbp/' + str(i) + '_full_pbp.json')
            print(str(x) + ' ' + str(i) + ' ' + str(gamePlotRequest.status_code))
            #gamePlotRequest.raise_for_status()
            gamePlotRequest = gamePlotRequest.json()
            gamePlaybyPlay.append(gamePlotRequest)
            pass
        except ValueError:
            print(str(x) + ' ' + str(i) + ' Request Failed')

    
##print(gamePlaybyPlay) # list
##gamePlaybyPlay[0]['g']['pd'][0]['p']

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

gamePlays.columns = ['ClockTime', 'Description', 'EPId', 'EType', 'Evt', 'GameID', 'HS', 'LocationX', 'LocationY', 'MId', 'MType', 'OftId', 'OpId', 'Opt1', 'Opt2', 'Period', 'PlayerID', 'TeamID', 'Vs', 'Id']


# ------------------------------------------------------------ Game Box Score ------------------------------------------------------------

# game box score descriptons by game, looping through all gameIDs up till today
dateString = sorted(set(dateString))
print(str(len(dateString)) + ' matchdays found')


gameBoxScore_staging = [] 
url4 = All_Seasons_url4
for i in dateString:
    try:
        gameBoxScoreRequest = requests.get(url4 + str(i) + '.json')
        print(i + ' - ' + str(gameBoxScoreRequest.status_code))
        #gameBoxScoreRequest.raise_for_status()
        gameBoxScoreRequest = gameBoxScoreRequest.json()
        gameBoxScore_staging.append(gameBoxScoreRequest)
        pass
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

#gameBoxScore.to_sql('Games_BoxScore', engine, flavor=None, schema='nbadata', if_exists='append', index=None, chunksize=10000)



# ------------------------------------------------------------------------------------------------------------------------


#playergameSummary.to_sql('Staging_PlayerGameSummary', engine, flavor=None, schema='dbo', if_exists='append', index=None, chunksize=10000)

#cursor.execute('''INSERT INTO [PlayerGameSummary]( [Ast],[Blk],[Blka],[Court],[Dreb],[Fbpts],[Fbptsa],[Fbptsm],[Fga],[Fgm],[Fn],[Fta],[Ftm],[GameID],[Ln],[Memo],[Mid],[Min],[Num],[Oreb],[Pf],[PlayerID],[Pip],[Pipa],[Pipm],[Pm],[Pos],[Pts],[Reb],[Sec],[Status],[Stl],[Ta],[Tf],[TeamID],[Totsec],[Tov],[Tpa],[Tpm]) 
#	SELECT [Ast],[Blk],[Blka],[Court],[Dreb],[Fbpts],[Fbptsa],[Fbptsm],[Fga],[Fgm],[Fn],[Fta],[Ftm],[GameID],[Ln],[Memo],[Mid],[Min],[Num],[Oreb],[Pf],[PlayerID],[Pip],[Pipa],[Pipm],[Pm],[Pos],[Pts],[Reb],[Sec],[Status],[Stl],[Ta],[Tf],[TeamID],[Totsec],[Tov],[Tpa],[Tpm]  FROM [Staging_PlayerGameSummary] 
#		WHERE NOT EXISTS (
#			SELECT [Ast],[Blk],[Blka],[Court],[Dreb],[Fbpts],[Fbptsa],[Fbptsm],[Fga],[Fgm],[Fn],[Fta],[Ftm],[GameID],[Ln],[Memo],[Mid],[Min],[Num],[Oreb],[Pf],[PlayerID],[Pip],[Pipa],[Pipm],[Pm],[Pos],[Pts],[Reb],[Sec],[Status],[Stl],[Ta],[Tf],[TeamID],[Totsec],[Tov],[Tpa],[Tpm]  FROM [dbo].[PlayerGameSummary] 
#				WHERE [Staging_PlayerGameSummary].[GameID]=[PlayerGameSummary].[GameID] AND [Staging_PlayerGameSummary].[PlayerID]=[PlayerGameSummary].[PlayerID] AND [Staging_PlayerGameSummary].[TeamID]=[PlayerGameSummary].[TeamID])''')


#cursor.execute('DELETE FROM Staging_PlayerGameSummary')
#conn.commit()


# ------------------------------------------------------------------------------------------------------------------------



#gamePlays.to_sql('Staging_GamePlays', engine, flavor=None, schema='dbo', if_exists='append', index=None, chunksize=10000)

#gameplaysTable = 'GamePlays'
#gameplaysStaging = 'Staging_GamePlays'
#gameplaysQuery = '[Ast],[Blk],[Blka],[Court],[Dreb],[Fbpts],[Fbptsa],[Fbptsm],[Fga],[Fgm],[Fn],[Fta],[Ftm],[GameID],[Ln],[Memo],[Mid],[Min],[Num],[Oreb],[Pf],[PlayerID],[Pip],[Pipa],[Pipm],[Pm],[Pos],[Pts],[Reb],[Sec],[Status],[Stl],[Ta],[Tf],[TeamID],[Totsec],[Tov],[Tpa],[Tpm],[Id]'

#gamePlays.to_sql(gameplaysStaging, engine, flavor=None, schema='dbo', if_exists='append', index=None, chunksize=10000)


#cursor.execute('''INSERT INTO [''' + gameplaysTable + '''](''' + gameplaysQuery + ''') 
#	SELECT ''' + gameplaysQuery + ''' FROM [''' + gameplaysStaging + '''] WHERE NOT EXISTS (SELECT ''' + gameplaysQuery + ''' FROM [dbo].[''' + gameplaysTable + '''] WHERE [''' + gameplaysStaging + '''].[TeamID]=['''+ gameplaysTable +'''].[TeamID])''')

#cursor.execute('DELETE FROM ' + gameplaysStaging)
#conn.commit()



# ------------------------------------------------------------------------------------------------------------------------

# games = pd.read_sql('Select * from Games', engine)
# games['Season'] = np.where(
#     (games['Date'] >= datetime.date(2017, 9, 1)) & (games['Date'] < datetime.date(2018, 7, 31)), '2017-2018', np.where(
#         (games['Date'] >= datetime.date(2016, 9, 1)) & (games['Date'] < datetime.date(2017, 7, 31)), '2016-2017', np.where(
#             (games['Date'] >= datetime.date(2015, 9, 1)) & (games['Date'] < datetime.date(2016, 7, 31)), '2015-2016', np.where( 
#                 (games['Date'] >= datetime.date(2014, 9, 1)) & (games['Date'] < datetime.date(2015, 7, 31)), '2014-2015', None
#             ))))

# games['Season Phase'] = np.where(
#     games['GameID'].astype(str).str.startswith('11'), 'Pre-Season', np.where(
#         games['GameID'].astype(str).str.startswith('21'), 'Regular Season', np.where(
#             games['GameID'].astype(str).str.startswith('41'), 'Post Season', None)))
# games.to_sql('Staging_Games', engine, if_exists='append', index=None, chunksize=1000)

