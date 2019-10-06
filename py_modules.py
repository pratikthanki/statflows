import pyodbc
import logging
import pandas as pd


def sql_server_connection(config):
    return pyodbc.connect(
        'DRIVER={driver};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'.format(**config)
    )


def load_data(query, sql_config):
    sql_data = []
    conn = sql_server_connection(sql_config)

    cursor = conn.cursor()

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

    return df


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
    return ' AND '.join(
        [['Target.[' + i + ']=Source.[' + i + ']' for i in l.keys() if i in key_columns] for l in lst][0])


def set_statement(lst, key_columns):
    return ', '.join([['[' + i + ']=Source.[' + i + ']' for i in l.keys() if i not in key_columns] for l in lst][0])


def execute_sql(table_name, data, key_columns, sql_cursor):
    sql_cursor.execute('MERGE INTO {0} as Target '
                       'USING (SELECT * FROM '
                       '(VALUES {1}) '
                       'AS s ({2}) '
                       ') AS Source '
                       'ON {3} '
                       'WHEN NOT MATCHED THEN '
                       'INSERT ({2}) VALUES ({4}) '
                       'WHEN MATCHED THEN '
                       'UPDATE SET {5}; '.format(table_name,
                                                 values_statement(data),
                                                 columns_statement(data),
                                                 on_statement(data, key_columns),
                                                 source_columns_statement(data),
                                                 set_statement(data, key_columns))
                       )
    logging.info('Table {0} updated: {1} records'.format(table_name, len(data)))
