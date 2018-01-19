import numpy as np
import pandas as pd
import pyodbc
import luminol


# Connection to ms sql using pyodbc
driver = 'ODBC DRIVER 13 for SQL Server'
server = 's'
database = 'd'
username = 'u'
password = 'p'
conn  = pyodbc.connect(r'DRIVER={ODBC DRIVER 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)


# Request a cursor from the connection that can be used for queries
cursor= conn.cursor() 


# Create dataframe from sql table in database
ts, ts2 = pd.read_sql("select * from [dbo].[PlayerGameSummary]", conn)


# Conduct anomaly detection on a single time series ts.
detector = luminol.anomaly_detector.AnomalyDetector(ts)
anomalies = detector.get_anomalies()


# if there is anomaly, correlate the first anomaly period with a secondary time series ts2.
if anomalies:
    time_period = anomalies[0].get_time_window()
    correlator = luminol.correlator.Correlator(ts, ts2, time_period)


#print the correlation coefficient
print(correlator.get_correlation_result().coefficient)