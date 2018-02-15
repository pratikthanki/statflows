import os
import sys
import requests
import json
import pandas as pd
import numpy as np
import pyodbc
from Links import *


from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import *

# get today's date, for use later when getting Id's
import time
from datetime import datetime, timedelta

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
yesterday = datetime.today() - timedelta(days=1)
yesterday = datetime.strptime(yesterday.strftime("%Y-%m-%d"), "%Y-%m-%d")



ms_sql = ms_sql
# engine = create_engine('mssql+pyodbc://' + ms_sql)


mysql = mysql
# engine = create_engine('mysql+mysqlconnector://' + mysql)


cursor = engine.connect()




# Create dataframe from sql table in database
Players = pd.read_sql("select * from [dbo].[Players]", conn)
Teams = pd.read_sql("select * from [dbo].[Teams]", conn)

PlayerId = Players['PlayerID']

TeamsId = []
for i in Teams['TeamID']:
    if int(len(str(i))) == 10:
        TeamsId.append(i)


headers = headers

# --------------------------- Player stats by season ---------------------------


url1 = Player_Team_Legacy_url1
playerStats = []
for i in PlayerId:
    try:
        playerStatsRequest = requests.get(url1 + str(i), headers=headers)
        print(str(i) + ' - ' + str(playerStatsRequest.status_code))
    #    playerStatsRequest.raise_for_status()
        playerStatsRequest = playerStatsRequest.json()
        playerStats.append(playerStatsRequest)
        pass
    except ValueError as e:
        print(str(i) + ' ' + str(e))


def seasonStats(resultName, summaries, resultList, headersList):
    for i in summaries:
        for j in i['resultSets']:
            for rows in j['rowSet']:
                if len(j['rowSet']) > 0 and j['name'] == resultName:
                    resultList.append(rows)
                    headersList.append(j['headers'])


# ------------------------ Parse and write tables to database ------------------------

def parseWrite(dbTableName):
    resultList = []
    headersList = []
    seasonStats(dbTableName, playerStats, resultList, headersList)
    resultList = pd.DataFrame(resultList)
    resultList.columns = [headersList[0]]
    resultList.to_sql(dbTableName, engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)

parseWrite('SeasonTotalsRegularSeason')
parseWrite('CareerTotalsRegularSeason')

parseWrite('SeasonTotalsPostSeason')
parseWrite('CareerTotalsPostSeason')

parseWrite('SeasonTotalsAllStarSeason')
parseWrite('CareerTotalsAllStarSeason')

parseWrite('SeasonTotalsCollegeSeason')
parseWrite('CareerTotalsCollegeSeason')


# --------------------------- Team stats by season ---------------------------


url2 = Player_Team_Legacy_url2
teamStats = []
for i in TeamsId:
    try:
        teamStatsRequest = requests.get(url2 + str(i), headers=headers)
        print(str(i) + ' - ' + str(teamStatsRequest.status_code))
        #teamStatsRequest.raise_for_status()
        teamStatsRequest = teamStatsRequest.json()
        teamStats.append(teamStatsRequest)
        pass
    except ValueError

TeamSeasons = []
teamSeason_headers = []
seasonStats('TeamStats', teamStats, TeamSeasons, teamSeason_headers)
teamSeason_headers = teamSeason_headers[0]
TeamSeasons = pd.DataFrame(TeamSeasons)
TeamSeasons.columns = [teamSeason_headers]
TeamSeasons.to_sql('TeamLegacyStats', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)

