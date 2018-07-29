import os
import sys
import re
import requests
import json
import pandas as pd
import numpy as np
import pyodbc
from sqlalchemy import create_engine


os.chdir('C:\\Users\\PratikThanki\\OneDrive - EDGE10 (UK) Ltd\\Pratik\\Python\\statflows-nba')
from Links import *

# --------------------------- Connecting & writing to database ---------------------------

#engine = create_engine(ms_sql)
engine = create_engine(my_sql)

cursor = engine.connect()



# get today's date, for use later when getting Id's
import time
from datetime import datetime, timedelta

now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
yesterday = datetime.today() - timedelta(days=1)
yesterday = datetime.strptime(yesterday.strftime("%Y-%m-%d"), "%Y-%m-%d")


headers = headers

"""
League ID: NBA = 00     ABA = 01
Season: Format: NNNN-NN (eg. 2016-17)
Season Type: One of - "Regular Season", "Pre Season", "Playoffs", "All-Star", "All Star", "Preseason"
"""

# --------------------------- Draft Pick History ---------------------------


url1 = Draft_Combine_url1
drafthistoryRequest = requests.get(url1, headers=headers).json()


drafthistory = []
for i in drafthistoryRequest['resultSets']:
    for row in i['rowSet']:
        drafthistory.append(row)


draft = pd.DataFrame(drafthistory)

drafthistoryHeaders = drafthistoryRequest['resultSets'][0]['headers']
drafthistoryHeaders = [item.replace("'", ' ') for item in drafthistoryHeaders]
draft.columns = [drafthistoryHeaders]

<<<<<<< HEAD
#draft.to_sql('draftcombine_results', engine, flavor=None, schema='dbo', if_exists='replace', index=None, chunksize=1000)
=======

# --------------------------- Connecting & writing to database ---------------------------

# engine = create_engine('mssql+pyodbc://' + ms_sql)
engine = create_engine('mysql+mysqlconnector://' + str(my_sql))
cursor = engine.connect()

draft.to_sql('Draft_Results', engine, flavor=None, schema='nbadata', if_exists='replace', index=None, chunksize=1000)
>>>>>>> 563a793dcf76c684e84ad6f47f4f7b9f42862f36


# --------------------------- Combine Activities Request ---------------------------

combineActivityType = ['draftcombinedrillresults', 'draftcombinenonstationaryshooting', 'draftcombineplayeranthro', 'draftcombinespotshooting', 'draftcombinestats']

seasons = []
for x in range(2000, 2018):
    seasons.append(str(x) + '-' + str(x+1)[2:4])

url2 = Draft_Combine_url2
def combineResults(paramName):
    emptyList = []
    for s in seasons:
<<<<<<< HEAD
        drillRequest = requests.get(url2 + str(paramName) + '?LeagueID=00&SeasonYear=' + str(s), headers=headers)
        print(s, str(drillRequest.status_code))
        emptyList.append(drillRequest.json())
=======
        drillRequest = requests.get(url2 + str(paramName) + '?LeagueID=00&SeasonYear=' + s, headers=headers)
        print(s + ' ' + str(drillRequest.status_code))
        drillRequest = drillRequest.json()
        emptyList.append(drillRequest)
        time.sleep(1)
>>>>>>> 563a793dcf76c684e84ad6f47f4f7b9f42862f36

    return emptyList

<<<<<<< HEAD

drillresults = combineResults('draftcombinedrillresults')
stationaryshooting = combineResults('draftcombinenonstationaryshooting')
playeranthro = combineResults('draftcombineplayeranthro')
spotshooting = combineResults('draftcombinespotshooting')
stats = combineResults('draftcombinestats')


# --------------------------- Combine Activities Parse ---------------------------

=======
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
>>>>>>> 563a793dcf76c684e84ad6f47f4f7b9f42862f36

def convert(word):
        import re
        return ''.join(x.capitalize() or '_' for x in word.split('_'))


def combineStats(resultName, summaries, resultList, headersList):
    for i in summaries:
        for j in i['resultSets']:
            for rows in j['rowSet']:
                if len(j['rowSet']) > 0 and (j['name'] == 'Results' or j['name'] == 'DraftCombineStats'):
                    resultList.append(rows + [i['parameters']['SeasonYear']])
                    headersList.append(j['headers'] + ['Season_Year'])


def parseWrite(dbTableName, combineList):
    resultList = []
    headersList = []
    combineStats(dbTableName, combineList, resultList, headersList)
    resultList = pd.DataFrame(resultList)
<<<<<<< HEAD

    h = []
    if len(headersList) > 0:
        for column in headersList[-1]:
            h.append(convert(column))

    resultList.columns = h
    resultList.to_sql(dbTableName, engine, flavor=None, schema='nbadata', if_exists='replace', index=None, chunksize=1000)
    return resultList


parseWrite('DrillResults', drillresults)
parseWrite('NonStationaryShooting', stationaryshooting)
parseWrite('PlayerAnthro', playeranthro)
parseWrite('SpotShooting', spotshooting)
parseWrite('Stats', stats)
=======
    resultList.columns = [headersList[0]]
    resultList.to_sql(dbTableName, engine, flavor=None, schema='nbadata', if_exists='replace', index=None, chunksize=1000)

>>>>>>> 563a793dcf76c684e84ad6f47f4f7b9f42862f36

parseWrite('Draft_DrillResults', draftcombinedrillresults)
parseWrite('Draft_NonStationaryShooting', draftcombinenonstationaryshooting)
parseWrite('Draft_PlayerAnthro', draftcombineplayeranthro)
parseWrite('Draft_SpotShooting', draftcombinespotshooting)
parseWrite('Draft_Stats', draftcombinestats)