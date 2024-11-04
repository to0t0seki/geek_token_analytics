import json
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from datetime import timedelta
import pytz

def view_deposit_geek():
    # データを読み込む
    with open('data/raw/0x205e_transactions.json','r') as f:
        data = json.load(f)

    # methodがxgeekToGeekのデータをnewdataリストに格納  
    newdata = []
    for tx in data:
        if tx['method'] == 'xgeekToGeek' and tx['result'] == 'success':
            newdata.append({
                'hash': tx['hash'],
                'from_hash': tx['from']['hash'],
                'timestamp': datetime.fromisoformat(tx['timestamp'].replace('Z','+00:00')),
                'value': Decimal(int(tx['raw_input'][10:74],16))/Decimal(10**18)
            })
           

    #デバッグ用
    # address = '0xD56a823971228F7a066dE58263f345C090597CD9'
    # takaaddress = [item for item in newdata if address in item['from_hash']]

    # JST4時を日付の区切りとして、日付ごとにデータを集計
    total_data = defaultdict(Decimal)
    for item in newdata:
        total_data[(item['timestamp'] + timedelta(hours=5)).date()] += item['value']
        #デバッグ用
        # if item['timestamp'] + timedelta(hours=5) > datetime(2024, 10, 19,tzinfo=pytz.UTC):
        #     print(f"{item['timestamp'] + timedelta(hours=5)}:{item['from_hash']} {item['value'].quantize(Decimal('1'))}")
        
        

    # 日付ごとのデータを出力
    for date, value in total_data.items():
        print(date, value.quantize(Decimal('1')))

view_deposit_geek()
            








