import time
import requests
import datetime
import logging
from teams import TEAMS
from shared_modules import SqlConnection, create_logger
from nba_settings import current_roster_1, headers, Referer


def current_roster(current_season, team, sql):
    data_headers = []
    roster_lst = []
    failed_responses = []

    url = '{0}{1}&TeamID={2}'.format(current_roster_1, str(current_season), str(team))
    headers['Referer'] = Referer.format(team)
    try:
        roster_rqst = requests.request('GET', url, headers=headers)
        roster = roster_rqst.json()

        roster_lst.append(roster['resultSets'][0]['rowSet'])
        data_headers = [h.lower() for h in roster['resultSets'][0]['headers']]

        print(roster_rqst.status_code, team)

        time.sleep(3)

        pass
    except Exception as e:
        print(e, url)

    rosters = [dict(zip(data_headers, player)) for team in roster_lst for player in team]
    sql.insert_data('rosters', rosters)


def get_rosters():
    logging.info('Task started')

    sql = SqlConnection('NBA')
    current_season = '2019-20'
    team_ids = [TEAMS[i]['id'] for i in TEAMS.keys()]

    for team in team_ids:
        current_roster(current_season, team, sql)

    logging.info('Task completed')


def main():
    create_logger(__file__)

    get_rosters()


if __name__ == '__main__':
    main()
