import datetime
import requests
import collections
from shared_modules import create_logger, get_data, SqlConnection
from nfl_settings import base_url, stat_types, headers, upsert_keys


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_stats(data, sql, table_name):
    output = []
    for week in data:
        for stats in week['stats']:
            output.append(flatten(stats))

    # some dicts contains keys that others don't, so this check for and adds NULL records
    sorted_data = []
    all_keys = frozenset().union(*output)
    for row in output:
        for k in all_keys:
            if k not in row:
                row[k] = None

        sorted_data.append(collections.OrderedDict(sorted(row.items())))

    sql.insert_data(table_name, sorted_data, upsert_keys)


def get_stats(season, stat, sql):
    play_stats = []
    for week in range(1, 24, 1):
        season_phase = 'REG' if week <= 17 else 'POST'
        url = f'{base_url}/{stat}?season={season}&seasonType={season_phase}&week={week}'

        query = requests.request('GET', url, headers=headers)

        print(query.status_code, stat, season, week)
        play_stats.append(query.json())

    parse_stats(play_stats, sql, stat)


def bulk_writer(sql):
    for season in range(2015, 2020, 1):
        for stat in stat_types:
            get_stats(season, stat, sql)


def current_season():
    today = datetime.datetime.now()
    if today.month > 3 and today.day > 0:
        season = today.year
    else:
        season = today.year - 1
    return season


def main():
    create_logger(__file__)

    sql = SqlConnection('NFL')

    season = current_season()
    for stat in stat_types:
        get_stats(season, stat, sql)


if __name__ == '__main__':
    main()
