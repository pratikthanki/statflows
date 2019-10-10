import time
import requests
from shared_config import sql_config
from shared_modules import sql_server_connection, execute_sql
from afl_settings import match_stats_1, match_stats_2, flatten, get_token

headers = get_token()

# Request of all Rounds and Seasons 2001 - Present
games_json = []
for season in range(2019, 2020):
    for round in range(1, 28):
        try:
            games_request = requests.get(match_stats_1 + str(season) + '014' + "%02d" % round, headers=headers)
            print(season, round, games_request.status_code)
            games_request = games_request.json()
            games_json.append(games_request)
            pass
        except ValueError as e:
            print(season, round, e)

games_list = []
for round in games_json:
    for matches in round['items']:
        games_list.append({
            'RoundID': round['roundId'],
            'MatchName': matches['match']['name'],
            'Date': matches['match']['date'],
            'VenueID': matches['match']['venue'],
            'MatchID': matches['match']['matchId'],
            'HomeTeamID': matches['match']['homeTeamId'],
            'AwayTeamID': matches['match']['awayTeamId'],
            'HomeTeamName': matches['match']['homeTeam']['name'],
            'AwayTeamName': matches['match']['awayTeam']['name'],
            'VenueName': matches['venue']['name'],
            'TimeZone': matches['venue']['timeZone'],
            'RoundName': matches['round']['name'],
            'Year': matches['round']['year']
        })

match_ids = [i['MatchID'] for i in games_list]

# AFL Player Match Stats by Season and Round /playerStats
match_list = []
for match in match_ids:
    try:
        match_request = requests.get(match_stats_2 + match + '/playerStats', headers=headers)
        print(str(match), match_request.status_code)
        match_request = match_request.json()
        match_list.append(match_request)
        time.sleep(0.5)
        pass
    except ValueError:
        print(match, 'Match Error')


def player_stats(team):
    rows = []

    for season in match_list:
        for games in season[team]['playerStats']:
            row = flatten(games)
            row['MatchID'] = season['matchId']
            row['TeamID'] = season[team]['team']['teamId']

            rows.append(row)

    return rows


home_player_stats = player_stats('homeTeam')
away_player_stats = player_stats('awayTeam')
all_player_stats = home_player_stats + away_player_stats

# AFL Team Stats by Season and Round /teamStats
team_stats_list = []
for match in match_ids:
    try:
        team_stats_request = requests.get(match_stats_2 + match + '/teamStats', headers=headers)
        print(str(match), team_stats_request.status_code)
        team_stats_request = team_stats_request.json()
        team_stats_list.append(team_stats_request)
        time.sleep(0.5)
        pass
    except ValueError as e:
        print(match, e)


def team_stats(team):
    rows = []

    for season in team_stats_list:
        row = flatten(season[team]['stats'])
        row['MatchID'] = season['matchId']
        row['TeamID'] = (season[team]['teamId'])

        rows.append(row)

    return rows


home_team_stats = team_stats('homeTeam')
away_team_stats = team_stats('awayTeam')
all_team_stats = home_team_stats + away_team_stats

try:
    conn = sql_server_connection(sql_config, 'afl')
    cursor = conn.cursor()
except Exception as e:
    print(e)
# logging.info(e)

execute_sql('Games', games_list, ['MatchID'], cursor)
execute_sql('PlayerSummary', all_player_stats, ['MatchID', 'TeamID', 'playerId'], cursor)
execute_sql('TeamSummary', all_team_stats, ['MatchID', 'TeamID'], cursor)
