import requests
import datetime
import time
from teams import TEAMS
from nba_settings import current_roster_1, headers
from shared_config import sql_config
from shared_modules import sql_server_connection, execute_sql


def current_nba_season():
    today = datetime.date.today()
    if today.month in (7, 8, 9, 10, 11, 12):
        y = datetime.date.today().year
        current_season = str(y) + '-' + str(y + 1)[-2:]
    else:
        y = today.year
        current_season = str(y - 1) + '-' + str(y)[-2:]

    return current_season


def current_roster():
    current_season = current_nba_season()
    teams = [TEAMS[i]['id'] for i in TEAMS.keys()]

    data_headers = []
    roster_lst = []
    failed_responses = []
    for t in teams:
        try:
            url = '{0}{1}&TeamID={2}'.format(current_roster_1, str(current_season), str(t))
            roster_rqst = requests.request('GET', url, headers=headers)

            print(t, roster_rqst.status_code)

            roster = roster_rqst.json()
            roster_lst.append(roster['resultSets'][0]['rowSet'])

            data_headers = roster['resultSets'][0]['headers']

            time.sleep(3)
            pass
        except Exception as e:
            print(t, e)
            failed_responses.append(t)

    return [dict(zip(data_headers, player)) for team in roster_lst for player in team]


def main():
    team_rosters = current_roster()
    conn, cursor = sql_server_connection(sql_config, 'nba')

    execute_sql('TeamRosters', team_rosters, ['TeamID'], cursor)
    conn.commit()


if __name__ == '__main__':
    main()
