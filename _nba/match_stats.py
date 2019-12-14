import logging
import time
from datetime import datetime, timedelta
from shared_modules import create_logger, get_data, MongoConnection
from nba_settings import current_season_1, current_season_2, current_season_3, mongo_details

upsert_keys = {
    'games': ['game_id'],
    'match_stats': ['gid', 'tid'],
    'pbp': ['gid', 'pid', 'tid']
}


def get_schedule(url, mongodb_connector, nba_db, offset):
    game_rqst = get_data(url)

    now = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
    date_offset = now - timedelta(days=offset)

    games = []
    for i in game_rqst['lscd']:
        for j in i['mscd']['g']:
            game_date = datetime.strptime(j['gdte'], '%Y-%m-%d')
            if game_date < now:
                games.append({
                    'game_id': j['gid'],
                    'game_code': j['gcode'],
                    'venue': j['an'],
                    'date': j['gdte'],
                    'date_string': j['gcode'].split('/')[0],
                    'away_team_id': j['v']['tid'],
                    'away_score': j['v']['s'],
                    'home_team_id': j['h']['tid'],
                    'home_score': j['h']['s']
                })

    mongodb_connector.insert_documents(nba_db, nba_db['games'], games, upsert_keys['games'])
    return [i['game_id'] for i in games]


def get_game_stats(url, url_prop, list_of_games):
    game_stats = []
    for i in list_of_games:
        try:
            stats_url = '{0}{1}_{2}.json'.format(url, i, url_prop)
            stats_req = get_data(base_url=stats_url)
            game_stats.append(stats_req)
        except ValueError as e:
            logging.error(i, e)

    return game_stats


def game_detail_stats(game_json, mongodb_connector, nba_db):
    lst = []
    for a in game_json:
        if a is None:
            continue
        for b in [a['g']]:
            for prop in ['vls', 'hls']:
                if 'pstsg' not in b[prop]:
                    logging.warning(f"'pstsg' not in game_id: {b['gid']}")
                    continue

                for c in b[prop]['pstsg']:
                    c['gid'] = b['gid']
                    c['mid'] = b['mid']
                    c['tid'] = b[prop]['tid']
                    c['ta'] = b[prop]['ta']
                    lst.append(c)

    mongodb_connector.insert_documents(nba_db, nba_db['match_stats'], lst, upsert_keys['match_stats'])


def game_pbp_stats(game_json, mongodb_connector, nba_db):
    for i in game_json:
        play_by_play = []
        if i is None:
            continue
        for j in i['g']['pd']:
            for k in j['pla']:
                if 'pla' not in j:
                    logging.warning(f"'pla' not in game_id: {i['g']['gid']}")
                    continue

                k['period'] = j['p']
                k['gid'] = i['g']['gid']
                k['mid'] = i['g']['mid']
                play_by_play.append(k)

        mongodb_connector.insert_documents(nba_db, nba_db['match_pbp'], play_by_play, upsert_keys['pbp'])


def update_stats(mongodb_connector, season):
    nba_db = mongodb_connector.db_connect('nba')

    games = get_schedule(current_season_1.format(season), mongodb_connector, nba_db, offset=10)

    game_detail_json = get_game_stats(current_season_2.format(season), 'gamedetail', games)
    game_detail_stats(game_detail_json, mongodb_connector, nba_db)

    game_pbp_json = get_game_stats(current_season_3.format(season), 'full_pbp', games)
    game_pbp_stats(game_pbp_json, mongodb_connector, nba_db)


def main():
    create_logger(__file__)

    logging.info('Task started')

    mongodb_connector = MongoConnection(project='match-stats')
    update_stats(mongodb_connector=mongodb_connector, season='2019')

    logging.info('Task completed')


if __name__ == '__main__':
    main()
