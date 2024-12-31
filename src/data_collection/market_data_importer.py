import requests
import time
from src.data_access.client import DatabaseClient




#open,high,low,close,volume,usdt_volume
def fetch_ohlcv_from_bitget(unix_time: int):
    unix_time = int(unix_time*1000)
    url = f'https://api.bitget.com/api/v2/spot/market/history-candles?endTime={unix_time}&symbol=GEEKUSDT&granularity=1h&limit=200'
    response = requests.get(url).json()
    if response['msg'] == 'success':
        print(f"fetched {len(response['data'])} rows")
        return response['data']
    else:
        print(f"failed to fetch ohlcv: {response['msg']}")
        return None


def aggregate_ohlcv_history(fetch_ohlcv_func = fetch_ohlcv_from_bitget,start_time = 1727190000) -> None:
    start_time += 60*60*24*8
    create_ohlcv_1h()
    current_time = int(time.time())
    existing_timestamps = set()
    db_client = DatabaseClient()

    while start_time < current_time + 60*60*24*8:
        tmp_list = fetch_ohlcv_func(start_time)
        for ohlcv in tmp_list:
            ohlcv[0] = int(int(ohlcv[0])/1000)
            ohlcv[1:] = [float(x) for x in ohlcv[1:7]]
            if ohlcv[0] not in existing_timestamps: 
                insert_ohlcv_1h(db_client, ohlcv[:7])
                existing_timestamps.add(ohlcv[0])
        start_time += 60*60*24*8


def create_ohlcv_1h():
    create_ohlcv_1h_table = """
        CREATE TABLE IF NOT EXISTS ohlcv_1h (
            timestamp timestamp PRIMARY KEY,
            open DECIMAL(20,8),
            high DECIMAL(20,8),
            low DECIMAL(20,8),
            close DECIMAL(20,8),
            volume DECIMAL(20,8),
            usdt_volume DECIMAL(20,8)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    db_client = DatabaseClient()
    db_client.execute(create_ohlcv_1h_table)

   
    

    index_exists = db_client.fetch_one("""
    SHOW INDEX FROM ohlcv_1h WHERE Key_name = 'idx_ohlcv_1h_timestamp';
    """)

    if not index_exists:
        create_index_timestamp = """
        CREATE INDEX idx_ohlcv_1h_timestamp ON ohlcv_1h(timestamp);
        """
        db_client.execute(create_index_timestamp)
        print("timestampインデックスが作成されました")


def insert_ohlcv_1h(db_client: DatabaseClient, ohlcv_list: list):
    insert_ohlcv_1h_query = """
    INSERT IGNORE INTO ohlcv_1h (timestamp, open, high, low, close, volume, usdt_volume) VALUES (from_unixtime(%s), %s, %s, %s, %s, %s, %s)
    """
    try:
        
        cursor = db_client.execute_params(insert_ohlcv_1h_query, ohlcv_list)
        if cursor.rowcount > 0:
            print(ohlcv_list[0])
            print(f"inserted {cursor.rowcount} rows")

    except Exception as e:
        print(f"Error during insertion: {e}")
        print(f"Sample data: {ohlcv_list[0]}")
 


    

def ohlcv_1h_to_csv(csv_file: str = 'ohlcv_1h.csv'):
    db_client = DatabaseClient()
    df = db_client.query_to_df("SELECT * FROM ohlcv_1h")
    df.to_csv(csv_file, index=False)



def get_latest_ohlcv_1h():
    db_client = DatabaseClient()
    result = db_client.fetch_one("SELECT * FROM ohlcv_1h ORDER BY timestamp DESC LIMIT 1")
    unixtime = int(result[0].timestamp())
    return unixtime

def fetch_ohlcv():
    start_time = get_latest_ohlcv_1h()
    aggregate_ohlcv_history(start_time=start_time)

if __name__ == "__main__":
    fetch_ohlcv()



