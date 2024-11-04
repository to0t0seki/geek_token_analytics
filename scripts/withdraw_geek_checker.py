import json
from decimal import Decimal
from datetime import datetime,timezone
from collections import defaultdict
from datetime import timedelta

#出金ギークを計算
def view_withdraw_geek():
    # データを読み込む
    with open('data/raw/0x205e_transactions.json', 'r') as file:
        data = json.load(file)
    
    #methodがexportTokenのデータをnewdataに格納
    newdata = []
    for tx in data:
        if tx['method'] == 'exportToken' and tx['result'] == 'success' :
            newdata.append({
                'hash': tx['hash'],
                'from_hash': tx['from']['hash'],
                'timestamp': datetime.fromisoformat(tx['timestamp'].replace('Z','+00:00')),
                'value': Decimal(int(tx['raw_input'][74:138],16))/Decimal(10**18)
            })

    #デバッグ用
    # address = '0xD56a823971228F7a066dE58263f345C090597CD9'
    # takaaddress = [item for item in newdata if address in item['from_hash']]

    # JST4時を日付の区切りとして、日付ごとにデータを集計
    total_data = defaultdict(Decimal)
    for item in newdata:
        total_data[(item['timestamp'] + timedelta(hours=5)).date()] += item['value']

    # 日付ごとのデータを出力
    for date, value in total_data.items():
        print(date, value)

    return newdata

data = view_withdraw_geek()



    


