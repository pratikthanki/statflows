import requests
import logging
import time
from datetime import datetime, timedelta
from shared_config import sql_config
from shared_modules import sql_server_connection, execute_sql, create_logger, get_data, remove_duplicates
from nba_settings import current_season_1, current_season_2, current_season_3


def get_schedule():
    game_rqst = get_data(current_season_1)
    now = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
    date_offset = now - timedelta(days=7)

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
            logging.info(i, e)

    return game_stats


def game_detail_stats(prop, game_json):
    lst = []
    for a in game_json:
        for b in [a['g']]:
            if 'pstsg' not in b[prop]:
                logging.info('**Issue with game:', b['gid'])
                pass
            else:
                for c in b[prop]['pstsg']:
                    c['gid'] = b['gid']
                    c['mid'] = b['mid']
                    c['tid'] = b[prop]['tid']
                    c['ta'] = b[prop]['ta']
                    lst.append(c)

    return lst


def game_pbp_stats(game_json):
    play_by_play = []
    for i in game_json:
        for j in i['g']['pd']:
            for k in j['pla']:
                if 'pla' not in j:
                    logging.info('**Issue with game:', i['g']['gid'])
                    pass
                else:
                    k['period'] = j['p']
                    k['gid'] = i['g']['gid']
                    k['mid'] = i['g']['mid']
                    play_by_play.append(k)
    return play_by_play


def roster_details(game_json):
    players = [
        {'PlayerID': i['pid'], 'LastName': i['ln'], 'FirstName': i['fn']} for i in game_json
    ]

    teams = [
        {'TeamID': i['tid'], 'TeamCode': i['ta']} for i in game_json
    ]

    players = remove_duplicates(players)
    teams = remove_duplicates(teams)

    return players, teams


def main():
    create_logger('nba_log')
    logging.info('Task started')

    datetime.utcnow().strftime('%Y-%m-%d')
    games = get_schedule()

    game_detail_json = get_game_stats(current_season_2, 'gamedetail', games)
    game_pbp_json = get_game_stats(current_season_3, 'full_pbp', games)

    game_vls = game_detail_stats('vls', game_detail_json)
    game_hls = game_detail_stats('hls', game_detail_json)
    player_game_summary = game_vls + game_hls

    play_by_play = game_pbp_stats(game_pbp_json)

    players, teams = roster_details(player_game_summary)

    conn, cursor = sql_server_connection(sql_config, database='nba')

    execute_sql('Teams', teams, ['TeamID'], cursor)
    execute_sql('Players', players, ['PlayerID', 'FirstName'], cursor)
    execute_sql('Schedule', games, ['GameID'], cursor)
    execute_sql('PlayerGameSummary', player_game_summary, ['pid', 'gid', 'tid'], cursor)
    execute_sql('GamePlays', play_by_play, ['evt', 'gid', 'gid', 'pid', 'tid'], cursor)

    conn.commit()
    logging.info('Task completed')


if __name__ == '__main__':
    main()
