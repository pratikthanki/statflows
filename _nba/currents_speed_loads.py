import requests
from nba_settings import speed_load_1, headers
from shared_modules import load_data

try:
    conn = sql_server_connection(sql_config)
    cursor = conn.cursor()
except Exception as e:
    logging.info(e)

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

games = load_data(query, sql_config)
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
