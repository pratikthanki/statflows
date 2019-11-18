import time
import requests
import logging
from shared_modules import SqlConnection, create_logger, get_data
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
    for x in range(2018, 2020):
        seasons.append(str(x) + '-' + str(x + 1)[2:4])
    return seasons


def convert(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))


def draft_history(nba_sql):
    draft_history_data = get_data(draft_combine_1)

    drafts = []
    for i in draft_history_data['resultSets']:
        for row in i['rowSet']:
            drafts.append(row)

    draft_keys = draft_history_data['resultSets'][0]['headers']
    drafts = [dict(zip(draft_keys, draft_val)) for draft_val in drafts]

    nba_sql.insert_data('DraftHistory', drafts, ['TEAM_ID', 'PERSON_ID'])


def combine_stats(data, activity_type, nba_sql):
    result_list = []
    headers_list = []

    for i in data:
        for j in i['resultSets']:
            for rows in j['rowSet']:
                if len(j['rowSet']) > 0 and (j['name'] == 'Results' or j['name'] == 'DraftCombineStats'):
                    result_list.append(rows + [i['parameters']['SeasonYear']])
                    headers_list = j['headers'] + ['Season_Year']

    table_name = activity_type.replace('draftcombine', '')
    data = [dict(zip(headers_list, result)) for result in result_list]

    nba_sql.insert_data(table_name, data, ['Season_Year', 'PLAYER_ID'])


def combine_results(activity_type, nba_sql):
    draft_data = []
    for s in get_seasons():
        params = {
            'LeagueID': '00',
            'SeasonYear': str(s)
        }

        url = f'{draft_combine_2}{activity_type}'

        drill_request = requests.request('GET', url, headers=headers, params=params)
        draft_data.append(drill_request.json())

        print(s, activity_type, drill_request.status_code)
        time.sleep(1)

    combine_stats(draft_data, activity_type, nba_sql)


def main():
    create_logger(__file__)
    logging.info('Task started')

    nba_sql = SqlConnection(database='nba')

    draft_history(nba_sql)

    for activity in activity_types:
        combine_results(activity, nba_sql)


if __name__ == '__main__':
    main()
