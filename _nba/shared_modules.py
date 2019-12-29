import os
import pyodbc
import time
import logging
import pandas as pd
import logging
import requests
from urllib.parse import quote
from pymongo import MongoClient
from nba_settings import headers, sql_uid, sql_pwd, mongo_details


class SqlConnection:
    def __init__(self, database):
        self.server = '192.168.1.13'
        self.port = 1433
        self.database = database
        self.username = sql_uid
        self.password = sql_pwd
        self.prod_driver = 'sql_server'
        self.local_driver = '{/usr/local/lib/libmsodbcsql.13.dylib}'
        self.autocommit = True
        self.conn = self.sql_server_connection()
        self.cursor = self.conn.cursor()

    def sql_server_connection(self):
        try:
            return pyodbc.connect(
                # DRIVER='FreeTDS',
                DRIVER=self.local_driver,
                TDS_Version='8.0',
                ClientCharset='UTF8',
                PORT=self.port,
                SERVER=self.server,
                DATABASE=self.database,
                UID=self.username,
                PWD=self.password,
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

    def add_table_constraint(self, table_name):
        alter_table_query = 'ALTER TABLE [dbo].[{0}] ADD CONSTRAINT [last_updated_{0}] ' \
                            'DEFAULT (getdate()) FOR [LastUpdated]'
        self.cursor.execute(alter_table_query.format(table_name))

    def create_table(self, table_name, table_columns):
        create_table_query = '''
            CREATE TABLE [dbo].[{0}](
            {1}, [LastUpdated] [datetime] NOT NULL
            ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
        '''

        self.cursor.execute(create_table_query.format(
            table_name,
            create_table_columns_statement(table_columns)
        ))
        self.add_table_constraint(table_name)

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

    def insert_data(self, table_name, data, key_columns, verbose=0):
        all_keys = set().union(*(d.keys() for d in data))

        self.check_if_table_exists(table_name, all_keys)

        conn = self.sql_server_connection()
        cursor = conn.cursor()

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

        cursor.execute(query)
        conn.commit()
        logging.info('{0}: {1} rows inserted'.format(table_name, len(data)))

        if verbose > 0:
            print('{0}: {1} rows inserted'.format(table_name, len(data)))


class MongoConnection:
    def __init__(self, project):
        self.uid = mongo_details[project]['uid']
        self.pwd = quote(mongo_details[project]['pwd'], safe='')
        self.cluster = mongo_details[project]['cluster']
        self.params = 'ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority'
        self.conn_str = f'mongodb+srv://{self.uid}:{self.pwd}@{self.cluster}/test'
        self.client = MongoClient(f'{self.conn_str}?{self.params}')

    def api_str(self):
        return self.conn_str

    def db_connect(self, database):
        return self.client[database]

    def check_collection_exists(self, db, collection):
        if collection not in db.list_collection_names():
            return db.create_collection(name=collection)

    def insert_documents(self, db, collection, data, keys=None):
        collection_name = str(collection).replace(')', '').rpartition(', ')[-1]
        self.check_collection_exists(db, collection_name.replace("'", ""))

        start = time.time()

        collection.insert_many(data)
        print(f'Collection: {collection_name}; Docs inserted: {len(data)}; Time taken: {time.time() - start}')
        return

        # docs_skipped = 0
        # docs_inserted = 0
        # output = []

        # for doc in data:
        #     if keys:
        #         key_data = {key: doc[key] for key in keys if key in doc.keys()}
        #
        #         finder = collection.find(key_data)
        #         output = [row for row in finder]
        #
        #     if len(output) > 0:
        #         docs_skipped += 1
        #         continue
        #
        #     collection.insert_one(doc)
        #     docs_inserted += 1
        #
        # print(f'Collection: {collection_name}; Docs skipped: {docs_skipped}; '
        #       f'Docs inserted: {docs_inserted}; Time taken: {time.time() - start}')


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


def get_data(base_url, h=headers):
    try:
        rqst = requests.request('GET', base_url, headers=h)
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


def create_table_columns_statement(lst):
    if lst:
        return ', '.join(['[' + i + '] [varchar](max) NULL' for i in lst])


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
