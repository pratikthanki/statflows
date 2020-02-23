import time
import requests
import logging
from shared_modules import SqlConnection, create_logger, get_data
from nba_settings import draft_combine_1, draft_combine_2, headers, referer_default

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


def draft_history(sql, headers):
    draft_history_data = get_data(draft_combine_1, headers)

    drafts = []
    for i in draft_history_data['resultSets']:
        for row in i['rowSet']:
            drafts.append(row)

    draft_keys = draft_history_data['resultSets'][0]['headers']
    drafts = [dict(zip(draft_keys, draft_val)) for draft_val in drafts]

    sql.insert_data('draft_history', drafts, ['PERSON_ID', 'SEASON', 'TEAM_ID'])


def combine_stats(data, activity_type, sql):
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

    sql.insert_data(f'draft_{table_name.lower()}', data, ['PLAYER_ID', 'SeasonYear'])


def combine_results(activity_type, sql, headers):
    for season in get_seasons():
        draft_data = []
        params = {
            'LeagueID': '00',
            'SeasonYear': str(season)
        }

        url = f'{draft_combine_2}{activity_type}'

        drill_request = requests.request('GET', url, headers=headers, params=params)
        draft_data.append(drill_request.json())

        print(drill_request.status_code, season, activity_type)
        time.sleep(1)

        combine_stats(draft_data, activity_type, sql)


def main():
    create_logger(__file__)
    logging.info('Task started')

    sql = SqlConnection('NBA')

    headers['Referer'] = referer_default

    draft_history(sql, headers)

    for activity in activity_types:
        combine_results(activity, sql, headers)


if __name__ == '__main__':
    main()
