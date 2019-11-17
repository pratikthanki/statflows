import time
import requests
import logging
from shared_config import sql_config
from shared_modules import sql_server_connection, execute_sql, create_logger, get_data
from nba_settings import draft_combine_1, draft_combine_2, headers

"""
League ID: NBA = 00     ABA = 01
Season: Format: NNNN-NN (eg. 2016-17)
Season Type: One of - "Regular Season", "Pre Season", "Playoffs", "All-Star", "All Star", "Preseason"
"""

activity_types = [
    'draftcombinedrillresults',
    'draftcombinenonstationaryshooting',
    'draftcombineplayeranthro',
    'draftcombinespotshooting',
    'draftcombinestats']


def get_seasons():
    seasons = []
    for x in range(2000, 2020):
        seasons.append(str(x) + '-' + str(x + 1)[2:4])
    return seasons


def convert(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def draft_history(cursor):
    draft_history_data = get_data(draft_combine_1)

    drafts = []
    for i in draft_history_data['resultSets']:
        for row in i['rowSet']:
            drafts.append(row)

    draft_keys = draft_history_data['resultSets'][0]['headers']
    drafts = [dict(zip(draft_keys, draft_val)) for draft_val in drafts]

    execute_sql('DraftHistory', drafts, ['TEAM_ID', 'PERSON_ID'], cursor)


def combine_stats(data):
    result_list = []
    headers_list = []

    for i in data:
        for j in i['resultSets']:
            for rows in j['rowSet']:
                if len(j['rowSet']) > 0 and (j['name'] == 'Results' or j['name'] == 'DraftCombineStats'):
                    result_list.append(rows + [i['parameters']['SeasonYear']])
                    headers_list.append(j['headers'] + ['Season_Year'])


def combine_results_request(activity_type):
    empty_list = []
    for s in get_seasons():
        params = {
            'LeagueID': '00',
            'SeasonYear': str(s)
        }

        url = f'{draft_combine_2}{activity_type}'

        drill_request = requests.request('GET', url, headers=headers, params=params)
        empty_list.append(drill_request.json())

        print(s, str(drill_request.status_code))
        time.sleep(1)

    combine_stats(empty_list)


def main():
    create_logger(__file__)
    logging.info('Task started')

    conn, cursor = sql_server_connection(sql_config, database='nba')

    draft_history(cursor)

    for activity in activity_types:
        combine_results_request(activity)


if __name__ == '__main__':
    main()
