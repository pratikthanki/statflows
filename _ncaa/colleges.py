import json 
import requests
import pandas as pd 



url = 'https://www.ncaa.com/sites/default/files/json/schools.json'
schools = requests.get(url)
schools.status_code
schools = schools.json()

school_list = []
for i in schools:
    school_list.append(i)

school_list = pd.DataFrame(school_list)

