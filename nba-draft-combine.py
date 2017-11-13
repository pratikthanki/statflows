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

headers = {'user-agent': 'headers'}

"""
League ID: NBA = 00     ABA = 01

Season: Format: NNNN-NN (eg. 2016-17)

Season Type: One of - "Regular Season", "Pre Season", "Playoffs", "All-Star", "All Star", "Preseason"

"""

# --------------------------- Draft Pick History ---------------------------


drafthistoryURL = 'url'


drafthistoryRequest = requests.get(drafthistoryURL, headers=headers).json()

drafthistory = []
for i in drafthistoryRequest['resultSets']:
    for row in i['rowSet']:
        drafthistory.append(row)


draft = pd.DataFrame(drafthistory)

drafthistoryHeaders = drafthistoryRequest['resultSets'][0]['headers']
draft.columns = [drafthistoryHeaders]


# --------------------------- Connecting & writing to database ---------------------------

engine = create_engine('mssql+pyodbc://uid:pwd@hostname')

draft.to_sql('DraftResults', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)


# --------------------------- Combine Activities Request ---------------------------

combineActivityType = ['draftcombinedrillresults', 'draftcombinenonstationaryshooting', 'draftcombineplayeranthro', 'draftcombinespotshooting', 'draftcombinestats']

seasons = []
for x in range(2000, 2018):
    seasons.append(str(x) + '-' + str(x+1)[2:4])

def combineResults(paramName, emptyList):
    for s in seasons:
        drillRequest = requests.get('url', headers=headers)
        print(s + ' ' + str(drillRequest.status_code))
        drillRequest = drillRequest.json()
        emptyList.append(drillRequest)


draftcombinedrillresults = []
combineResults('draftcombinedrillresults', draftcombinedrillresults)

draftcombinenonstationaryshooting = []
combineResults('draftcombinenonstationaryshooting', draftcombinenonstationaryshooting)

draftcombineplayeranthro = []
combineResults('draftcombineplayeranthro', draftcombineplayeranthro)

draftcombinespotshooting = []
combineResults('draftcombinespotshooting', draftcombinespotshooting)

draftcombinestats = []
combineResults('draftcombinestats', draftcombinestats)


# --------------------------- Combine Activities Parse ---------------------------

def combineStats(resultName, summaries, resultList, headersList):
    for i in summaries:
        for j in i['resultSets']:
            for rows in j['rowSet']:
                if len(j['rowSet']) > 0 and j['name'] == 'Results':
                    resultList.append(rows + [i['parameters']['SeasonYear']])
                    headersList.append(j['headers'] + ['SeasonYear'])


def parseWrite(dbTableName, combineList):
    resultList = []
    headersList = []
    combineStats(dbTableName, combineList, resultList, headersList)
    resultList = pd.DataFrame(resultList)
    resultList.columns = [headersList[0]]
    resultList.to_sql(dbTableName, engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)

parseWrite('DraftCombineDrillResults', draftcombinedrillresults)
parseWrite('DraftCombineNonStationaryShooting', draftcombinenonstationaryshooting)
parseWrite('DraftCombinePlayerAnthro', draftcombineplayeranthro)
parseWrite('DraftCombineSpotShooting', draftcombinespotshooting)
parseWrite('DraftCombineStats', draftcombinestats)

