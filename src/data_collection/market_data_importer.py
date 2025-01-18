import requests
import time
from src.data_access.client import DatabaseClient
from datetime import datetime



#open,high,low,close,volume,usdt_volume
def fetch_ohlcv_from_bitget(unix_time: int):
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} fetch_ohlcv_from_bitgetが開始されました")
        unix_time = int(unix_time*1000)
        url = f'https://api.bitget.com/api/v2/spot/market/history-candles?endTime={unix_time}&symbol=GEEKUSDT&granularity=1h&limit=200'
        response = requests.get(url).json()
        if response['msg'] == 'success':
            print(f"fetched {len(response['data'])} rows")
            return response['data']
        else:
            print(f"failed to fetch ohlcv: {response['msg']}")
            return None
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} fetch_ohlcv_from_bitget中にエラーが発生しました: {e}")


def aggregate_ohlcv_history(fetch_ohlcv_func = fetch_ohlcv_from_bitget,start_time = 1727190000) -> None:
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} aggregate_ohlcv_historyが開始されました")
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
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} aggregate_ohlcv_history中にエラーが発生しました: {e}")


def create_ohlcv_1h():
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_ohlcv_1hが開始されました")
        create_ohlcv_1h_table = """
            CREATE TABLE IF NOT EXISTS ohlcv_1h (
                timestamp timestamp PRIMARY KEY,
                open NUMERIC(20,8),
                high NUMERIC(20,8),
                low NUMERIC(20,8),
                close NUMERIC(20,8),
                volume NUMERIC(20,8),
                usdt_volume NUMERIC(20,8)
            );
        """
        db_client = DatabaseClient()
        result = db_client.execute(create_ohlcv_1h_table)
        if result > 0:
            print("ohlcv_1hテーブルが作成されました")
        else:
            print("ohlcv_1hテーブルが作成されませんでした")
 
        create_index_timestamp = """
        CREATE INDEX IF NOT EXISTS idx_ohlcv_1h_timestamp ON ohlcv_1h(timestamp);
        """
        result = db_client.execute(create_index_timestamp)
        if result > 0:
            print("timestampインデックスが作成されました")
        else:
            print("timestampインデックスが作成されませんでした")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_ohlcv_1h中にエラーが発生しました: {e}")


def insert_ohlcv_1h(db_client: DatabaseClient, ohlcv_list: list):
    params = {
        'timestamp': ohlcv_list[0],
        'open': ohlcv_list[1],
        'high': ohlcv_list[2],
        'low': ohlcv_list[3],
        'close': ohlcv_list[4],
        'volume': ohlcv_list[5],
        'usdt_volume': ohlcv_list[6]
    }
    insert_ohlcv_1h_query = """
    INSERT INTO ohlcv_1h (timestamp, open, high, low, close, volume, usdt_volume) 
    VALUES (to_timestamp(%(timestamp)s), %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(usdt_volume)s)
    ON CONFLICT (timestamp) DO NOTHING
    """
    try:
        
        row_count = db_client.execute(insert_ohlcv_1h_query, params)
        if row_count > 0:
            print(ohlcv_list[0])
            print(f"inserted {row_count} rows")

    except Exception as e:
        print(f"Error during insertion: {e}")
        print(f"Sample data: {ohlcv_list[0]}")
 
def ohlcv_1h_to_csv(csv_file: str = 'ohlcv_1h.csv'):
    db_client = DatabaseClient()
    df = db_client.query_to_df("SELECT * FROM ohlcv_1h")
    df.to_csv(csv_file, index=False)



def get_latest_ohlcv_1h(client: DatabaseClient):
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} get_latest_ohlcv_1hが開始されました")
        check_table_exists_query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'ohlcv_1h')"
        result = client.fetch_one(check_table_exists_query)
        if not result[0]:
            print("ohlcv_1hテーブルが存在しません")
            return None
        
        check_exists_query = "SELECT EXISTS(SELECT 1 FROM ohlcv_1h)"
        result = client.fetch_one(check_exists_query)
        if not result[0]:
            print("ohlcv_1hテーブルにデータが存在しません")
            return None

        result = client.fetch_one("SELECT * FROM ohlcv_1h ORDER BY timestamp DESC LIMIT 1")
        unixtime = int(result[0].timestamp())
        return unixtime
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} get_latest_ohlcv_1h中にエラーが発生しました: {e}")

def fetch_ohlcv(client: DatabaseClient = DatabaseClient()):
    result_time = get_latest_ohlcv_1h(client)
    if result_time is None:
        aggregate_ohlcv_history()
    else:
        aggregate_ohlcv_history(start_time=result_time)


if __name__ == "__main__":
    fetch_ohlcv()



