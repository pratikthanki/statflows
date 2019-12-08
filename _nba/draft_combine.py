import time
import requests
import logging
from shared_modules import MongoConnection, create_logger, get_data
from nba_settings import draft_combine_1, draft_combine_2, headers, mongo_details

"""
League ID: NBA = 00     ABA = 01
Season: Format: NNNN-NN (eg. 2016-17)
Season Type: One of - "Regular Season", "Pre Season", "Playoffs", "All-Star", "All Star", "Preseason"
"""

activity_types = [
    'draftcombinedrillresults',
    'draftcombinenonstationaryshooting',
    'draftcombineplayeranthro',
    'draftcombinespotshooting'
    # 'draftcombinestats'
]


def get_seasons():
    seasons = []
    for x in range(2000, 2020):
        seasons.append(str(x) + '-' + str(x + 1)[2:4])
    return seasons


def draft_history(mongodb_connector, nba_db):
    draft_history_data = get_data(draft_combine_1)

    drafts = []
    for i in draft_history_data['resultSets']:
        for row in i['rowSet']:
            drafts.append(row)

    draft_keys = draft_history_data['resultSets'][0]['headers']
    drafts = [dict(zip(draft_keys, draft_val)) for draft_val in drafts]

    mongodb_connector.insert_documents(nba_db, nba_db['draft_history'], drafts, ['PERSON_ID', 'SEASON', 'TEAM_ID'])


def combine_stats(data, activity_type, mongodb_connector, nba_db):
    result_list = []
    headers_list = []

    for i in data:
        for j in i['resultSets']:
            for rows in j['rowSet']:
                if len(j['rowSet']) > 0 and (j['name'] == 'Results' or j['name'] == 'DraftCombineStats'):
                    result_list.append(rows + [i['parameters']['SeasonYear']])
                    headers_list = j['headers'] + ['SeasonYear']

    table_name = activity_type.replace('draftcombine', '')
    data = [dict(zip(headers_list, result)) for result in result_list]

    mongodb_connector.insert_documents(nba_db, nba_db[table_name], data, ['PLAYER_ID', 'SeasonYear'])


def combine_results(activity_type, mongodb_connector, nba_db):
    for season in get_seasons():
        draft_data = []
        params = {
            'LeagueID': '00',
            'SeasonYear': str(season)
        }

        url = f'{draft_combine_2}{activity_type}'

        drill_request = requests.request('GET', url, headers=headers, params=params)
        draft_data.append(drill_request.json())

        print(season, activity_type, drill_request.status_code)
        time.sleep(1)

        combine_stats(draft_data, activity_type, mongodb_connector, nba_db)


def main():
    create_logger(__file__)
    logging.info('Task started')

    mongodb_connector = MongoConnection(project='draft-combine')

    nba_db = mongodb_connector.db_connect('nba')

    draft_history(mongodb_connector, nba_db)

    for activity in activity_types:
        combine_results(activity, mongodb_connector, nba_db)


if __name__ == '__main__':
    main()
