import requests 
import pandas as pd
from Settings import * 

SpeedLoads_url1

getdata = requests.request('GET', SpeedLoads_url1, headers=headers)
getdata = getdata.json()

results = getdata['resultSets']

pd.DataFrame(data=results[0]['rowSet'], columns= results[0]['headers'])

