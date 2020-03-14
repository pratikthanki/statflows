import os
import logging
import time
from datetime import datetime, timedelta
from shared_modules import create_logger, get_data, SqlConnection
from nba_settings import current_season_1, current_season_2, current_season_3
from nba_modules import current_nba_season


upsert_keys = {
    'games': ['game_id'],
    'game_stats': ['gid', 'tid', 'pid'],
    'game_pbp': ['gid', 'tid', 'pid', 'evt']
}


def get_schedule(url, logger, sql, offset=7):
    game_rqst = get_data(url)

    now = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
    date_offset_str = now - timedelta(days=offset)

    logger.info(f'Fetching games between: {date_offset_str} - {now}')

    games = []
    for i in game_rqst['lscd']:
        for j in i['mscd']['g']:
            game_date = datetime.strptime(j['gdte'], '%Y-%m-%d')
            # if date_offset_str < game_date < now:
            if game_date < date_offset_str:
                games.append({
                    'game_id': j['gid'],
                    'game_code': j['gcode'],
                    'venue': j['an'],
                    'date': j['gdte'],
                    'away_team_id': int(j['v']['tid']),
                    'away_score': check_score(j['v']['s']),
                    'home_team_id': int(j['h']['tid']),
                    'home_score': check_score(j['h']['s']),
                    'season': current_nba_season(game_date)
                })

    if len(games) == 0:
        logging.info('No games to import')
        print(f'0 new games to import between; {date_offset_str} - {now}')
        raise SystemExit(0)

    sql.insert_data('games', games, upsert_keys['games'])
    return [i['game_id'] for i in games if i['home_score'] != 0 and i['away_score'] != 0]


def check_score(score):
    return 0 if score == '' else int(score)


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


def game_detail_stats(game_json, sql):
    for a in game_json:
        stats = []
        if a is None:
            continue
        for b in [a['g']]:
            for prop in ['vls', 'hls']:
                if 'pstsg' not in b[prop] or 'tstsg' not in b[prop]:
                    logging.warning(
                        f"'pstsg'/'tstsg' not in game_id: {b['gid']}")
                    continue

                for c in b[prop]['pstsg']:
                    c['mid'] = int(b['mid'])
                    c['gid'] = int(b['gid'])
                    c['tid'] = int(b[prop]['tid'])
                    c['ta'] = b[prop]['ta']
                    stats.append(c)

        if stats:
            print(int(b['gid']))
            sql.insert_data('game_stats', stats, upsert_keys['game_stats'])


def game_pbp_stats(game_json, sql):
    for i in game_json:
        play_by_play = []
        if i is None:
            continue
        for j in i['g']['pd']:
            for k in j['pla']:
                if 'pla' not in j:
                    logging.warning(f"'pla' not in game_id: {i['g']['gid']}")
                    continue

                play_by_play.append({
                    'evt': int(k['evt']),
                    'cl': k['cl'],
                    'de': k['de'],
                    'locX': int(k['locX']),
                    'locY': int(k['locY']),
                    'opt1': int(k['opt1']),
                    'opt2': int(k['opt2']),
                    'mtype': int(k['mtype']),
                    'etype': int(k['etype']),
                    'opid': int(k['opid'].replace('', '0')),
                    'tid': int(k['tid']),
                    'pid': int(k['pid']),
                    'hs': int(k['hs']),
                    'vs': int(k['vs']),
                    'epid': int(k['epid'].replace('', '0')),
                    'oftid': int(k['oftid']),
                    'ord': int(k['ord']),
                    'period': int(j['p']),
                    'gid': i['g']['gid'],
                    'mid': int(i['g']['mid'])
                })

        if play_by_play:
            sql.insert_data('game_pbp', play_by_play, upsert_keys['game_pbp'])


def update_stats(season, logger):
    logger.info(f'Season: {season}')

    sql = SqlConnection('nba')

    games = get_schedule(current_season_1.format(season), logger, sql)

    game_detail_json = get_game_stats(current_season_2.format(season), 'gamedetail', games)
    game_detail_stats(game_detail_json, sql)

    game_pbp_json = get_game_stats(current_season_3.format(season), 'full_pbp', games)
    game_pbp_stats(game_pbp_json, sql)

    logging.info('Task completed')


def main():
    create_logger(__file__)

    os.environ['TZ'] = 'US/Eastern'

    update_stats(season='2019', logger=logging)


if __name__ == '__main__':
    main()
