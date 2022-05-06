from lib2to3.pgen2.pgen import DFAState
from unittest import result
import requests
import gzip
import json
import datetime
import time as tm
from tqdm import tqdm
import pandas as pd

import datetime
from dateutil.relativedelta import relativedelta

api_url = 'https://api.syosetu.com/novelapi/api/'
interval = 2
max_st = 2000
max_search_num = 2500
start_date = datetime.date(2015, 1, 1)
end_date = datetime.date(2022, 4, 1)

def convert_period_into_timestamp(start_date:str, end_date:str):
  start_date


def get_all_novel_info():
  df = pd.DataFrame()

  date_list = []
  m = start_date
  while m <= end_date:
    date_list.append(m)
    m = m + relativedelta(months=1)

  for date in tqdm(date_list):
    # 月初め0:00:00-月末23:59:59を取得
    start_date_time = datetime.datetime.combine(date, datetime.time())
    end_d = date + relativedelta(months=1) - datetime.timedelta(days=1)
    end_date_time = datetime.datetime.combine(end_d, datetime.time(23,59,59))
    print(f'{start_date_time} - {end_date_time}')

    # timestampを取得
    start_date_time = str(start_date_time.timestamp())
    end_date_time = str(end_date_time.timestamp())
    # print(f'{start_date_time} - {end_date_time}')
    lastup = f'{start_date_time}-{end_date_time}'

    # 作品数を取得
    payload = {'out': 'json','gzip':5,'of':'n','lim':1, 'order': 'hyoka', 'lastup': lastup}
    res = requests.get(api_url, params=payload).content
    r =  gzip.decompress(res).decode("utf-8") 
    allcount = json.loads(r)[0]["allcount"]
    print(allcount)

    # 作品数とmax_search_numの判定
    if max_search_num < allcount:
      limit_st = max_st
    else:
      limit_st = allcount

    st = 0
    while st <= limit_st:
      payload = {
        'out': 'json', 'gzip': 5, 'lim': 500, 'order': 'hyoka', 
        'lastup': lastup, 'st': st
        }
      
      cnt = 0
      while cnt < 5:
        try:
          res = requests.get(api_url, params=payload, timeout=30).content
          break
        except:
          print('Connection Error')
          cnt = cnt + 1
          tm.sleep(120)
        
      r = gzip.decompress(res).decode('utf-8')
      df_temp = pd.read_json(r)
      df_temp = df_temp.drop(0)
      df = pd.concat([df, df_temp])

      st += 500
      tm.sleep(interval)
  return df

result = get_all_novel_info()
result.to_csv('all_novel_info_20220505.csv', index=False)