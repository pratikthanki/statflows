import requests
import pandas as pd
from datetime import datetime
from Settings import sql_config, sql_server_connection, load_data, SpeedLoads_url1, headers

conn = sql_server_connection(sql_config)

query = '''
    SELECT 
     [GameID]
    ,[GameCode]
    ,[Venue]
    ,[Date]
    ,[DateString]
    ,[AwayTeamID]
    ,[AwayScore]
    ,[HomeTeamID]
    ,[HomeScore]
    FROM [nba].[dbo].[Schedule]
'''

games = load_data(query)
games.columns = ['GameId', 'GameCode', 'Venue', 'Date', 'DateStr', 'AwayTeamID', 'AwayScore', 'HomeTeamID', 'HomeScore']

params = {
    'StartRange': '0'
    , 'EndRange': '28800'
    , 'StartPeriod': '1'
    , 'EndPeriod': '10'
    , 'RangeType': '0'
    , 'Season': '2018-19'
    , 'SeasonType': 'Playoffs'
    , 'GameID': '0041800406'
}

get_data = requests.request('GET', SpeedLoads_url1, headers=headers, params=params)
get_data = get_data.json()
results = get_data['resultSets']

df = pd.DataFrame(
    data=results[0]['rowSet'],
    columns=results[0]['headers']
)

print(df)
