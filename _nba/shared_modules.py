import os
import pyodbc
import logging
import pandas as pd
import logging
import requests
from shared_config import server_uid, server_pwd


class SqlConnection:
    def __init__(self, database):
        self.server = '192.168.1.13'
        self.port = 1433
        self.database = database
        self.username = ENV['uid']
        self.password = ENV['pwd']
        self.prod_driver = 'sql_server'
        self.local_driver = '{/usr/local/lib/libmsodbcsql.13.dylib}'
        self.autocommit = True
        # self.conn = self.sql_server_connection()
        # self.cursor = self.conn.cursor()

    def sql_server_connection(self):
        try:
            return pyodbc.connect(
                DRIVER='FreeTDS',
                # DRIVER=self.local_driver,
                TDS_Version='8.0',
                ClientCharset='UTF8',
                PORT=self.port,
                SERVER=self.server,
                DATABASE=self.database,
                UID=self.username,
                PWD=self.password
            )

        except Exception as e:
            logging.info(e)

    def load_data(self, query, columns=None):
        conn = self.sql_server_connection()
        cursor = conn.cursor()
        cursor.execute(query)

        if not columns:
            return

        rows = cursor.fetchall()
        sql_data = []

        for row in rows:
            sql_data.append(list(row))

        df = pd.DataFrame(sql_data)
        df.columns = columns

        return df

    def insert_data(self, table_name, data, key_columns):
        query = 'SELECT * INTO #temp FROM ( VALUES {0} ) AS s ( {1} ) ' \
                'MERGE INTO {2} as Target ' \
                'USING #temp AS Source ' \
                '{3} ' \
                'WHEN NOT MATCHED THEN INSERT ( {1} ) VALUES ( {4} ) ' \
                'WHEN MATCHED THEN UPDATE SET {5}; ' \
                'DROP TABLE #temp; '.format(values_statement(data),
                                            columns_statement(data),
                                            table_name,
                                            on_statement(data, key_columns),
                                            source_columns_statement(data),
                                            set_statement(data, key_columns))

        self.cursor.execute(query)
        logging.info('{0}: {1} rows inserted'.format(table_name, len(data)))


def sql_server_connection(config, database):
    config['database'] = database
    try:
        query = 'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'.format(
            **config)
        conn = pyodbc.connect(query)
        cursor = conn.cursor()

        return conn, cursor
    except Exception as e:
        logging.info(e)


def load_data(query, sql_config, database, columns):
    sql_data = []
    conn, cursor = sql_server_connection(sql_config, database)

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        pass
    except Exception as e:
        print(e)
        rows = pd.read_sql(query, conn)

    for row in rows:
        sql_data.append(list(row))

    df = pd.DataFrame(sql_data)
    df.columns = columns

    return df


def get_data(base_url):
    try:
        rqst = requests.request('GET', base_url)
        return rqst.json()
    except ValueError as e:
        logging.info(e)


def execute_sql(table_name, data, key_columns, sql_cursor):
    query = 'SELECT * INTO #temp FROM ( VALUES {0} ) AS s ( {1} ) ' \
            'MERGE INTO {2} as Target ' \
            'USING #temp AS Source ' \
            '{3} ' \
            'WHEN NOT MATCHED THEN INSERT ( {1} ) VALUES ( {4} ) ' \
            'WHEN MATCHED THEN UPDATE SET {5}; ' \
            'DROP TABLE #temp; '.format(values_statement(data),
                                        columns_statement(data),
                                        table_name,
                                        on_statement(data, key_columns),
                                        source_columns_statement(data),
                                        set_statement(data, key_columns))

    sql_cursor.execute(query)
    logging.info('Table {0} updated: {1} records'.format(table_name, len(data)))
    print('Table {0} updated: {1} records'.format(table_name, len(data)))


def create_logger(file_name):
    logging.basicConfig(filename=file_name,
                        filemode='a',
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG)


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
