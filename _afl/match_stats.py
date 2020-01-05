import time
import requests
import logging
from shared_modules import create_logger, get_data, MongoConnection, SqlConnection
from afl_settings import match_stats_1, match_stats_2, flatten, get_token


# Request of all Rounds and Seasons 2001 - Present
def get_round_stats(headers, sql):
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

    sql.insert_data('Games', games_list, ['MatchID'])

    match_ids = [i['MatchID'] for i in games_list]

    get_player_stats(match_ids, sql)
    get_team_stats(match_ids, sql)


# AFL Player Match Stats by Season and Round /playerStats
def get_player_stats(match_ids, sql):
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

    rows = []
    for season in match_list:
        for team in ['homeTeam', 'awayTeam']:
            for games in season[team]['playerStats']:
                row = flatten(games)
                row['MatchID'] = season['matchId']
                row['TeamID'] = season[team]['team']['teamId']

                rows.append(row)

    sql.insert_data('PlayerSummary', rows, ['MatchID', 'TeamID', 'playerId'])


# AFL Team Stats by Season and Round /teamStats
def get_team_stats(match_ids, sql):
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

    rows = []

    for season in team_stats_list:
        for team in ['homeTeam', 'awayTeam']:
            row = flatten(season[team]['stats'])
            row['MatchID'] = season['matchId']
            row['TeamID'] = (season[team]['teamId'])

            rows.append(row)

    sql.insert_data('TeamSummary', rows, ['MatchID', 'TeamID'])


def main():
    create_logger(__file__)

    logging.info('Task started')

    sql = SqlConnection('afl')
    headers = get_token()

    get_round_stats(headers, sql)


if __name__ == '__main__':
    main()
