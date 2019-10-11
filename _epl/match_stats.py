import requests
import time
from epl_settings import match_stats_1, headers
from shared_modules import execute_sql

first_game = 38313
last_game = 38687

# Ccontinue from this point to get all remaining games
match_json = []
for id in range(first_game, last_game + 1):
    try:
        match_request = requests.get(match_stats_1 + str(id), headers=headers)
        print(str(id), match_request.status_code)
        match_request = match_request.json()
        match_json.append(match_request)
        time.sleep(0.5)
        pass
    except Exception as e:
        print(str(id), e)


def flatten_dict(d):
    def expand(key, value):
        if isinstance(value, dict):
            return [(key + '_' + k, v) for k, v in flatten_dict(value).items()]
        else:
            return [(key, value)]

    items = [item for k, v in d.items() for item in expand(k, v)]

    return dict(items)


teams = []
team = {}
match_id = []
for i in match_json:
    for j in i['entity']['teams']:
        team = flatten_dict(j)
        teams.append(team)
        if 'label' not in i['entity']['kickoff']:
            print(i['entity']['id'])
        else:
            match_id.append({
                'match_id': i['entity']['id'],
                'match_Date': i['entity']['kickoff']['label'],
                'season': i['entity']['gameweek']['compSeason']['label'],
                'ground_Name': i['entity']['ground']['name'],
                'ground_id': i['entity']['ground']['id'],
                'competition_Name': i['entity']['gameweek']['compSeason']['competition']['description'],
                'competition_id': i['entity']['gameweek']['compSeason']['competition']['id'],
                'team_id': team['team_id']
            })

stats = []
for i in match_json:
    if 'data' not in i:
        print(i['entity']['id'])
    else:
        for j in i['data']:
            value = str(j)
            for stat in i['data'][value]['M']:
                stats.append({
                    'metric': stat['name'],
                    'value': stat['value'],
                    'teamId': value,
                    'matchId': i['entity']['id']
                })

# matchid.to_sql('match', engine, if_exists='replace', index=False, chunksize=10000)
# teams.to_sql('teams', engine, if_exists='replace', index=False, chunksize=10000)
# stats.to_sql('stats', engine, if_exists='replace', index=False, chunksize=10000)
