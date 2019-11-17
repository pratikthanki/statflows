import pyodbc
import logging
import requests
from shared_config import sql_config
from nba_settings import standings_1, headers
from shared_modules import sql_server_connection, execute_sql, create_logger


def get_standings(cursor):
    standings_request = requests.request('GET', standings_1, headers=headers)
    standings_request = standings_request.json()

    standings = []
    for i in standings_request['payload']['standingGroups']:
        for j in i['teams']:
            print(j['profile']['id'])
            standings.append({
                'Abbr': j['profile']['abbr'],
                'Conference': j['profile']['conference'],
                'TeamId': j['profile']['id'],
                'TeamName': j['profile']['name'],
                'ConfRank': j['standings']['confRank'],
                'Wins': j['standings']['wins'],
                'Losses': j['standings']['losses'],
                'Streak': j['standings']['streak'],
                'Win%': j['standings']['winPct'],
                'DivLosses': j['standings']['divLoss'],
                'DivWins': j['standings']['divWin'],
                'DivRank': j['standings']['divRank'],
                'Last10': j['standings']['last10'],
                'HomeWins': j['standings']['homeWin'],
                'HomeLosses': j['standings']['homeLoss'],
                'RoadWins': j['standings']['roadWin'],
                'RoadLosses': j['standings']['roadLoss'],
                'RoadStreak': j['standings']['roadStreak'],
                'HomeStreak': j['standings']['homeStreak']
            })

    execute_sql('LeagueStandings', standings, ['TeamName'], cursor)


def main():
    create_logger(__file__)
    logging.info('Task started')

    conn, cursor = sql_server_connection(sql_config, 'nba')

    cursor.execute('DELETE FROM LeagueStandings')
    get_standings(cursor)

    conn.commit()

    logging.info('Task completed')


if __name__ == '__main__':
    main()
