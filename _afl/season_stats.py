import requests
from afl_settings import season_stats_1, get_token
from shared_config import sql_config
from shared_modules import sql_server_connection, execute_sql
from afl_settings import match_stats_1, match_stats_2, flatten, get_token


headers = get_token()

# Season Summary Stats, with all aggregations of key metrics and averages
teams_json = []
for season in range(2018, 2020):
    for round in range(1, 28):
        try:
            team_request = requests.get(
                season_stats_1 + str(season) + '014&roundId=CD_R' + str(season) + '014' + "%02d" % round,
                headers=headers)
            print(season, round, team_request.status_code)
            team_request = team_request.json()
            teams_json.append(team_request)
            pass
        except ValueError:
            print(season, round, 'Round Error')

stats_totals = []
stats_averages = []

# teams_json[0]['lists'][0]['stats']['averages']

for seasons in teams_json:
    for rounds in seasons['lists']:
        print(rounds)


try:
    conn = sql_server_connection(sql_config, 'afl')
    cursor = conn.cursor()
except Exception as e:
    print(e)
# logging.info(e)

