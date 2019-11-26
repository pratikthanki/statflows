import logging
import time
from datetime import datetime, timedelta
from shared_modules import create_logger, get_data, remove_duplicates, MongoConnection
from nba_settings import current_season_1, current_season_2, current_season_3


def get_schedule(url, offset):
    game_rqst = get_data(url)
    now = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
    date_offset = now - timedelta(days=offset)

    game = []
    for i in game_rqst['lscd']:
        for j in i['mscd']['g']:
            if date_offset <= datetime.strptime(j['gdte'], '%Y-%m-%d') < now:
                game.append({
                    'GameID': j['gid'],
                    'GameCode': j['gcode'],
                    'Venue': j['an'],
                    'Date': j['gdte'],
                    'DateString': j['gcode'].split('/')[0],
                    'AwayTeamID': j['v']['tid'],
                    'AwayScore': j['v']['s'],
                    'HomeTeamID': j['h']['tid'],
                    'HomeScore': j['h']['s']
                })
    return game


def get_game_stats(url, url_prop, games):
    game_stats = []
    list_of_games = [i['GameID'] for i in games]
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

    mongodb_connector.insert_documents(nba_db, nba_db['match_stats'], lst)
    roster_details(lst, mongodb_connector, nba_db)


def game_pbp_stats(game_json):
    play_by_play = []
    for i in game_json:
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

    return play_by_play


def roster_details(game_json, mongodb_connector, nba_db):
    players = [{'PlayerID': i['pid'], 'LastName': i['ln'], 'FirstName': i['fn']} for i in game_json]
    teams = [{'TeamID': i['tid'], 'TeamCode': i['ta']} for i in game_json]

    players = remove_duplicates(players)
    teams = remove_duplicates(teams)

    mongodb_connector.insert_documents(nba_db, nba_db['players'], players)
    mongodb_connector.insert_documents(nba_db, nba_db['teams'], teams)


def main():
    create_logger(__file__)
    logging.info('Task started')

    mongodb_connector = MongoConnection()
    nba_db = mongodb_connector.db_connect('nba')

    season = '2019'

    # for season in ['2016', '2017', '2018']:
    #     print(f'Getting data for {season} season')

    games = get_schedule(current_season_1.format(season), offset=14)
    mongodb_connector.insert_documents(nba_db, nba_db['games'], games)

    game_detail_json = get_game_stats(current_season_2.format(season), 'gamedetail', games)
    game_detail_stats(game_detail_json, mongodb_connector, nba_db)

    game_pbp_json = get_game_stats(current_season_3.format(season), 'full_pbp', games)
    play_by_play = game_pbp_stats(game_pbp_json)
    mongodb_connector.insert_documents(nba_db, nba_db['match_pbp'], play_by_play)

    logging.info('Task completed')


if __name__ == '__main__':
    main()
