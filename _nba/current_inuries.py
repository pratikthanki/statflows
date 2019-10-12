import glob
import pandas as pd
from shared_modules import sql_server_connection
from shared_config import sql_config
import xlrd

conn = sql_server_connection(sql_config)
cursor = conn.cursor()

result = [i for i in glob.glob('*.{}'.format('xlsx'))]
print(result)

if any('CONFIDENTIAL' in i for i in result):
    injuryfile = i
    xls = xlrd.open_workbook(injuryfile, on_demand=True)

if 'Game by Game - CONFIDENTIAL' in xls.sheet_names():
    df = pd.read_excel(injuryfile, sheet_name='Game by Game - CONFIDENTIAL')

else:
    print('Sheet to Parse Not found, sheets available are - ', xls.sheet_names())

df['Stats'] = ['Fully Fit' if x.startswith('L') or x.startswith('W') else x for x in df.Stats.values]

latestStatus = df.sort_values(by=['Date']).drop_duplicates(subset='Name', keep='last')
latestStatus.rename(columns={'Stats': 'Status'}, inplace=True)

print('Writing to Database')

cursor.executemany('INSERT INTO LatestInjuries (Team ,Name ,Date ,Status) VALUES(?,?,?,?)',
                   latestStatus.values.tolist())
conn.commit()

print('Complete')
