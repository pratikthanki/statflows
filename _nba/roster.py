import time
import requests
from teams import TEAMS
from shared_modules import MongoConnection, create_logger
from nba_modules import current_nba_season
from nba_settings import current_roster_1, headers, mongo_details


def current_roster(mongodb_connector):
    nba_db = mongodb_connector.db_connect('nba')
    roster_col = nba_db['roster']

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

    team_rosters = [dict(zip(data_headers, player)) for team in roster_lst for player in team]

    mongodb_connector.insert_documents(nba_db, roster_col, team_rosters)


def main():
    create_logger(__file__)

    mongodb_connector = MongoConnection(project='draft-combine')

    current_roster(mongodb_connector)


if __name__ == '__main__':
    main()
