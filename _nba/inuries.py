import os
import logging
import requests
import pandas as pd
from shared_modules import sql_server_connection, execute_sql, create_logger
from shared_config import sql_config


def parse_excel(injury_file):
    df = pd.read_excel(injury_file, sheet_name='Game by Game - CONFIDENTIAL')
    df['Stats'] = ['Fully Fit' if x.startswith('L') or x.startswith('W') else x for x in df.Stats.values]

    df.rename(columns={'Stats': 'Status'}, inplace=True)

    df = df.to_dict('records')
    return df


def main():
    create_logger('nba_log_injuries')
    logging.info('Task started')

    conn, cursor = sql_server_connection(sql_config, database='nba')

    os.chdir('_nba/')
    injury_file = [file for file in os.listdir() if 'CONFIDENTIAL' in file][0]
    df = parse_excel(injury_file)

    execute_sql('LatestInjuries', df, ['Team', 'Name', 'Date'], cursor)
    conn.commit()


if __name__ == '__main__':
    main()
