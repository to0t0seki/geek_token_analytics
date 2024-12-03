import requests
import time
from src.data_access.client import DatabaseClient



#opne,High,low,close,volume,usdtvolume
def fetch_ohlcv_from_bitget(unix_time: int):
    url = f'https://api.bitget.com/api/v2/spot/market/history-candles?endTime={unix_time}&symbol=GEEKUSDT&granularity=1h&limit=200'
    response = requests.get(url).json()
    if response['msg'] == 'success':
        print(f"fetched {len(response['data'])} rows")
        return response['data']
    else:
        print(f"failed to fetch ohlcv: {response['msg']}")
        return None


def aggregate_ohlcv_history(fetch_ohlcv_func = fetch_ohlcv_from_bitget) -> list:
    current_time = int(time.time()*1000)
    start_time = 1727881200000
    ohlcv_list = []
    existing_timestamps = set()

    while start_time < current_time + 60*60*24*8*1000:
        tmp_list = fetch_ohlcv_func(start_time)
        for ohlcv in tmp_list:
            if ohlcv[0] not in existing_timestamps: 
                ohlcv_list.append(ohlcv[:7])
                existing_timestamps.add(ohlcv[0])
            else:
                print(f"skip {ohlcv[0]}")

        start_time += 60*60*24*8*1000

    return ohlcv_list


def create_ohlcv_1h():
    create_ohlcv_1h_table = """
    CREATE TABLE IF NOT EXISTS ohlcv_1h (
        timestamp TEXT PRIMARY KEY,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        usdt_volume REAL
    )
    """
    db_client = DatabaseClient()
    db_client.execute_ddl(create_ohlcv_1h_table)

    create_index_query = """
    CREATE INDEX IF NOT EXISTS idx_ohlcv_1h_timestamp ON ohlcv_1h(timestamp);
    """
    db_client.execute_ddl(create_index_query)


def insert_ohlcv_1h(ohlcv_list: list):
    insert_ohlcv_1h_query = """
    INSERT OR IGNORE INTO ohlcv_1h (timestamp, open, high, low, close, volume, usdt_volume) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    db_client = DatabaseClient()
    inserted_rows = db_client.execute_many(insert_ohlcv_1h_query, ohlcv_list)
    skipped_rows = len(ohlcv_list) - inserted_rows
    print(f"inserted {inserted_rows} rows, skipped {skipped_rows} rows")

def run():
    ohlcv_list = aggregate_ohlcv_history()
    insert_ohlcv_1h(ohlcv_list)

def ohlcv_1h_to_csv(csv_file: str = 'ohlcv_1h.csv'):
    db_client = DatabaseClient()
    df = db_client.query_to_df("SELECT * FROM ohlcv_1h")
    df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    run()
    # create_ohlcv_1h()
    # ohlcv_1h_to_csv()

