import os
import logging
import time
from datetime import datetime, timedelta
from shared_modules import create_logger, get_data, SqlConnection
from nba_settings import current_season_1, current_season_2, current_season_3
from nba_modules import current_nba_season

upsert_keys = {
    'games': ['game_id'],
    'game_stats': ['gid', 'tid'],
    'game_pbp': ['gid', 'pid', 'tid']
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
            if date_offset_str < game_date < now:
                games.append({
                    'game_id': j['gid'],
                    'game_code': j['gcode'],
                    'venue': j['an'],
                    'date': j['gdte'],
                    'away_team_id': j['v']['tid'],
                    'away_score': j['v']['s'],
                    'home_team_id': j['h']['tid'],
                    'home_score': j['h']['s'],
                    'season': current_nba_season(game_date)
                })

    if len(games) == 0:
        logging.info('No games to import')
        print(f'0 new games to import between; {date_offset_str} - {now}')
        raise SystemExit(0)

    sql.insert_data('games', games, upsert_keys['games'])
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


def game_detail_stats(game_json, sql):
    for a in game_json:
        stats = []
        if a is None:
            continue
        for b in [a['g']]:
            for prop in ['vls', 'hls']:
                if 'pstsg' not in b[prop] or 'tstsg' not in b[prop]:
                    logging.warning(f"'pstsg'/'tstsg' not in game_id: {b['gid']}")
                    continue

                for c in b[prop]['pstsg']:
                    c['gid'] = b['gid']
                    c['mid'] = b['mid']
                    c['tid'] = b[prop]['tid']
                    c['ta'] = b[prop]['ta']
                    stats.append(c)
        try:
            sql.insert_data('game_stats', stats, upsert_keys['game_stats'])
        except Exception as e:
            print(e)
            print(stats)


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

                k['period'] = j['p']
                k['gid'] = i['g']['gid']
                k['mid'] = i['g']['mid']
                play_by_play.append(k)

        try:
            sql.insert_data('game_pbp', play_by_play, upsert_keys['game_pbp'])
        except Exception as e:
            print(e)
            print(play_by_play)


def update_stats(season, logger):
    logger.info(f'Season: {season}')

    sql = SqlConnection('NBA')

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
