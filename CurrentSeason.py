import requests
import logging
import logging.handlers
import time
from datetime import datetime, timedelta
from Settings import Current_Season_url1, Current_Season_url2, Current_Season_url3, Current_Season_url4, sql_config
from py_modules import sql_server_connection, values_statement, columns_statement, source_columns_statement, \
    update_statement, on_statement, set_statement, execute_sql

logging.basicConfig(filename='nba_log',
                    filemode='a',
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)

logging.info('Task started')


def get_data(base_url):
    try:
        rqst = requests.request('GET', base_url)
        return rqst.json()
    except ValueError as e:
        logging.info(e)


now = datetime.strptime(time.strftime("%Y-%m-%d"), "%Y-%m-%d")
date_offset = now - timedelta(days=30)

game_rqst = get_data(Current_Season_url1)

games = []
for i in game_rqst['lscd']:
    for j in i['mscd']['g']:
        if date_offset <= datetime.strptime(j['gdte'], "%Y-%m-%d") < now:
            games.append({
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

list_of_games = [i['GameID'] for i in games]

game_detail = []
game_pbp = []
for i in list_of_games:
    try:
        summary_url = '{0}{1}_gamedetail.json'.format(Current_Season_url2, i)
        summary_data = get_data(base_url=summary_url)
        game_detail.append(summary_data)

        pbp_url = '{0}{1}_full_pbp.json'.format(Current_Season_url3, i)
        pbp_data = get_data(base_url=pbp_url)
        game_pbp.append(pbp_data)
    except ValueError as e:
        logging.info(i, e)


def game_detail_stats(prop):
    lst = []
    for a in game_detail:
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


game_vls = game_detail_stats('vls')
game_hls = game_detail_stats('hls')
player_game_summary = game_vls + game_hls

play_by_play = []
for i in game_pbp:
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


def remove_duplicates(lst):
    return [dict(t) for t in {tuple(d.items()) for d in lst}]


players = [
    {'PlayerID': i['pid'], 'LastName': i['ln'], 'FirstName': i['fn']} for i in player_game_summary
]

teams = [
    {'TeamID': i['tid'], 'TeamCode': i['ta']} for i in player_game_summary
]

players = remove_duplicates(players)
teams = remove_duplicates(teams)

try:
    conn = sql_server_connection(sql_config)
    cursor = conn.cursor()
except Exception as e:
    logging.info(e)

execute_sql('Teams', teams, ['TeamID'], cursor)
execute_sql('Players', players, ['PlayerID'], cursor)
execute_sql('Schedule', games, ['GameID'], cursor)
execute_sql('GamePlays', play_by_play, ['evt', 'gid', 'gid', 'pid', 'tid'], cursor)
execute_sql('PlayerGameSummary', player_game_summary, ['pid', 'gid', 'tid'], cursor)

conn.commit()
logging.info('Task completed')
