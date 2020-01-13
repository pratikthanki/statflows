import requests
import collections
import pandas as pd
from shared_modules import create_logger, get_data, MongoConnection
from nfl_settings import base_url, stat_types, headers, mongo_details, upsert_keys

pd.set_option('max_columns', 50)
pd.set_option('max_rows', 600)
pd.set_option('max_width', 1000)


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_stats(data, mongodb_connector, nfl_db):
    output = []
    for week in data:
        for stats in week['stats']:
            output.append(flatten(stats))

    # mongodb_connector.insert_documents(nfl_db, nfl_db['match_pbp'], output, upsert_keys)


def get_stats(season, stat, mongodb_connector, nfl_db):
    play_stats = []
    for week in range(1, 23):
        season_phase = 'REG' if week <= 17 else 'POST'
        url = f'{base_url}/{stat}?season={season}&seasonType={season_phase}&week={week}'

        query = requests.request('GET', url, headers=headers)

        print(season, week, query.status_code)
        play_stats.append(query.json())

    parse_stats(play_stats, mongodb_connector, nfl_db)


def main():
    create_logger(__file__)

    project = 'match-stats'
    mongodb_connector = MongoConnection(project=project)
    nfl_db = mongodb_connector.db_connect('nfl')

    season = 2019
    for stat in stat_types:
        get_stats(season, stat, mongodb_connector, nfl_db)


if __name__ == '__main__':
    main()
