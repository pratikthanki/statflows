import os
import pyodbc
import time
import logging
import pandas as pd
import logging
import requests
from nba_settings import headers
from shared_config import uid, pwd


class SqlConnection:
    def __init__(self, database):
        self.server = 'localhost'
        self.port = 1433
        self.database = database
        self.username = uid
        self.password = pwd
        self.driver = '{/usr/local/lib/libtdsodbc.so}'
        self.prod_driver = 'FreeTDS'
        self.autocommit = True
        self.conn = self.sql_server_connection()
        self.cursor = self.conn.cursor()

    def sql_server_connection(self):
        try:
            return pyodbc.connect(
                driver=self.driver,
                server=self.server,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                tds_version='7.4',
                autocommit=self.autocommit
            )

        except Exception as e:
            logging.info(e)

    def load_data(self, query, columns=None):
        self.cursor.execute(query)

        if not columns:
            return

        rows = self.cursor.fetchall()

        sql_data = []
        for row in rows:
            sql_data.append(list(row))

        df = pd.DataFrame(sql_data, columns=columns)

        return df

    def create_table(self, table_name, table_columns):
        create_table_query = '''
            CREATE TABLE [dbo].[{0}]
            (
            {1}, 
            [LastUpdated] [datetime] NOT NULL DEFAULT (getdate())
            )
        '''

        self.cursor.execute(create_table_query.format(
            table_name,
            create_table_columns_statement(table_columns)
        ))
        print(f'Table created: {table_name}')

    def drop_table(self, table_name):
        query = 'DROP TABLE {0}'
        self.cursor.execute(query.format(table_name))

    def check_if_table_exists(self, table_name, table_columns=None, override=False, create=True):
        if override:
            self.drop_table(table_name)

        query = "IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = N'{0}') SELECT 1 ELSE SELECT 0"
        table_check = self.load_data(query.format(table_name), ['A'])

        if table_check['A'].loc[0] == 0 and create:
            self.create_table(table_name, table_columns)

    def insert_data(self, table_name, data, key_columns=None, verbose=1):
        all_keys = set().union(*(d.keys() for d in data))

        self.check_if_table_exists(table_name, all_keys)

        if key_columns:
            query = 'SELECT * INTO #temp FROM ( VALUES {0} ) AS s ( {1} ) ' \
                    'MERGE INTO [{6}].[dbo].[{2}] as Target ' \
                    'USING #temp AS Source ' \
                    '{3} ' \
                    'WHEN NOT MATCHED THEN INSERT ( {1} ) VALUES ( {4} ) ' \
                    'WHEN MATCHED THEN UPDATE SET {5}; ' \
                    'DROP TABLE #temp; '.format(values_statement(data),
                                                columns_statement(data),
                                                table_name,
                                                on_statement(data, key_columns),
                                                source_columns_statement(data),
                                                set_statement(data, key_columns),
                                                self.database)

        else:
            query = 'INSERT INTO [dbo].[{0}] ( {1} )' \
                    'SELECT {1} FROM ( VALUES {2} ) AS s ( {1} )'.format(table_name,
                                                                         columns_statement(data),
                                                                         values_statement(data))


        self.cursor.execute(query)
        self.conn.commit()
        logging.info('{0}: {1} rows inserted'.format(table_name, len(data)))

        if verbose > 0:
            print('{0}: {1} rows inserted'.format(table_name, len(data)))


def get_data(base_url, h=headers):
    try:
        rqst = requests.request('GET', base_url, headers=h)
        print(rqst.status_code, base_url)
        return rqst.json()
    except ValueError as e:
        logging.info(e)


def create_logger(file_name):
    log_file = file_name.replace('.py', '.log')
    log_dir = os.path.join(os.getcwd(), 'logs')

    folder, log = log_file.split('/')[-2:]
    log_path = os.path.join(log_dir, folder)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    logging.basicConfig(filename=os.path.join(log_path, log),
                        filemode='a',
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)

    logging.info('Task started')


def create_table_columns_statement(lst):
    if lst:
        return ', '.join(['[' + i + '] [varchar](255) NULL' for i in lst])


def convert_hex_to_rgba(team_colours):
    return [tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4)) for colour in team_colours]


def remove_duplicates(lst):
    return [dict(t) for t in {tuple(d.items()) for d in lst}]


def values_statement(lst):
    if lst:
        _ = [tuple([str(l).replace("'", "") for l in ls.values()])
             for ls in lst]
        return ','.join([str(i) for i in _])


def columns_statement(lst):
    if lst:
        return ', '.join([['[' + i + ']' for i in l.keys()] for l in lst][0])


def source_columns_statement(lst):
    if lst:
        return ', '.join([['Source.[' + i + ']' for i in l.keys()] for l in lst][0])


def update_statement(lst):
    if lst:
        return ', '.join([['[' + i + ']=Source.[' + i + ']' for i in l.keys()] for l in lst][0])


def on_statement(lst, key_columns):
    if 'LastUpdated' not in key_columns[0] and lst:
        return 'ON ' + ' AND '.join(
            [['Target.[' + i + ']=Source.[' + i + ']' for i in l.keys() if i in key_columns] for l in lst][0])
    else:
        return ''


def set_statement(lst, key_columns):
    return ', '.join([['[' + i + ']=Source.[' + i + ']' for i in l.keys() if i not in key_columns] for l in lst][0])


def insert_statement(table_name, columns):
    return f'''
CREATE TABLE [dbo].[{table_name}]
{columns}
,LastUpdated DATETIME2 GETDATE()    
'''
