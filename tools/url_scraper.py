import requests
from datetime import datetime, timedelta
import json

urls = []

for i in range(400):
    url = f"https://notice-doll-jp.enish-games.com/news/detail?target_os=pc&world=1&language=ja&account_id=0&id={i}"
    response = requests.get(url)
    if response.content != b'':
        urls.append(url)


        

# 開始日と終了日を設定
start_date = datetime(2024, 4, 5)  # 2024年5月1日
end_date = datetime.now()  # 2025年4月6日


# 日付ごとにループ
current_date = start_date
while current_date <= end_date:
    # 日付を'YYMMDD'形式に変換
    date_str = current_date.strftime('%y%m%d')
    
    url = f"https://www.lastmemories.io/news/{date_str}"
    response = requests.get(url)
    if response.status_code == 200:
        urls.append(url)
    
    # 次の日に進む
    current_date += timedelta(days=1)

with open('urls.json', 'w', encoding='utf-8') as f:
    json.dump(urls, f, ensure_ascii=False, indent=2)

