from sqlalchemy import create_engine
from Settings import *
import pandas as pd
import tensorflow as tf

# test tf has been downloaded correctly 
hello = tf.constant('Hello, TensorFlow!')
sess = tf.Session()
print(sess.run(hello))

engine = create_engine('mssql+pyodbc://' + ms_sql)
cursor = engine.connect()

playerGameSummary = pd.read_sql('select top 100 * from PlayerGameSummary', engine)


