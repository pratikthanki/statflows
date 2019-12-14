import logging
from nba_settings import standings_1
from shared_modules import create_logger, MongoConnection, get_data


def get_standings(mongodb_connector):
    standings_request = get_data(base_url=standings_1)
    nba_db = mongodb_connector.db_connect('nba')

    standings = []
    for i in standings_request['payload']['standingGroups']:
        for j in i['teams']:
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

    nba_db['standings'].drop()
    mongodb_connector.insert_documents(nba_db, nba_db['standings'], standings)


def main():
    create_logger(__file__)
    logging.info('Task started')

    mongodb_connector = MongoConnection(project='match-stats')

    get_standings(mongodb_connector)

    logging.info('Task completed')


if __name__ == '__main__':
    main()
