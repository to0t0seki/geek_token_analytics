import requests
from src.logger import setup_logger
from src.data_access.database_client import DatabaseClient
from datetime import datetime, timedelta
from src.database.ohlcv_1h_repository import insert_ohlcv_1h_db
import pytz

logger = setup_logger(__name__)

def _add_unique_ohlcv_data(existing_data: list, new_data: list) -> list:
    """タイムスタンプが重複しないOHLCVデータを追加

    Args:
        existing_data: 既存のOHLCVデータ [[timestamp, ...], ...]
        new_data: 追加するOHLCVデータ [[timestamp, ...], ...]
    """
    existing_timestamps = {data[0] for data in existing_data}  # setで高速化
    unique_new_data = [data for data in new_data if data[0] not in existing_timestamps]
    existing_data.extend(unique_new_data)
    return existing_data

#open,high,low,close,volume,usdt_volume
def _fetch_ohlcv_from_bitget(unix_time: int) -> list:
    """endtimeから過去200件のデータを取得
    """
    url = f'https://api.bitget.com/api/v2/spot/market/history-candles?endTime={unix_time}&symbol=GEEKUSDT&granularity=1h&limit=200'
    response = requests.get(url)
    response.raise_for_status()
    response = response.json()
    if response['msg'] == 'success':
        return response['data']
    raise Exception(f"failed to fetch ohlcv: {response['msg']}")


def _fetch_latest_ohlcv_1h(client: DatabaseClient) -> datetime:
    """データベースから最新の日時datetime型で取得
    """
    latest_record_query = "SELECT * FROM ohlcv_1h ORDER BY timestamp DESC LIMIT 1"
    latest_record = client.fetch_one(latest_record_query)
    
    if not latest_record:
        raise Exception("ohlcv_1hテーブルにデータが存在しません")
    latest_datetime = latest_record[0]
    latest_datetime_utc = pytz.UTC.localize(latest_datetime)

    return latest_datetime_utc


def fetch_ohlcv_1h_from_bitget() -> list:
    """データベースから最新の日時から現在日時までのOHLCVデータを取得
    """
    latest_datetime_utc = _fetch_latest_ohlcv_1h(DatabaseClient())
    logger.info(f"fetch_ohlcv_1h_from_bitget: latest_datetime_utc: {latest_datetime_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    # latest_datetime_utc = datetime(2025, 1, 1, 0, 0, 0, 0, pytz.UTC)
    current_datetime_utc = datetime.now(pytz.UTC)
    if current_datetime_utc - latest_datetime_utc < timedelta(seconds=7200):
        raise Exception("No data available to insert")
    
    end_datetime = latest_datetime_utc + timedelta(seconds=60*60*201)

    ohlcv_data = []
    while end_datetime < current_datetime_utc:
        end_timestamp = int(end_datetime.timestamp()*1000)
        batch_ohlcv = _fetch_ohlcv_from_bitget(end_timestamp)
        ohlcv_data.extend(batch_ohlcv)
        end_datetime = end_datetime + timedelta(seconds=60*60*200)
    else:
        current_timestamp = int(current_datetime_utc.timestamp()*1000)
        batch_ohlcv = _fetch_ohlcv_from_bitget(current_timestamp)
        filtered_ohlcv = []
        latest_timestamp = int(latest_datetime_utc.timestamp()*1000)
        for ohlcv in batch_ohlcv:
            timestamp = int(ohlcv[0])
            if timestamp > latest_timestamp:
                filtered_ohlcv.append(ohlcv)
        ohlcv_data = _add_unique_ohlcv_data(ohlcv_data, filtered_ohlcv)
        logger.info(f"fetch_ohlcv_1h_from_bitget: ohlcv_data_length: {len(ohlcv_data)}")
        return ohlcv_data

def convert_ohlcv(ohlcv_list: list)->list:
    """OHLCVデータをデータベースに保存するために変換
    """
    new_ohlcv_list = []
    for ohlcv in ohlcv_list:
        new_ohlcv_list.append({
            'timestamp': int(int(ohlcv[0]) / 1000),
            'open': ohlcv[1],
            'high': ohlcv[2],
            'low': ohlcv[3],
            'close': ohlcv[4],
            'volume': ohlcv[5],
            'usdt_volume': ohlcv[6]
        })
    return new_ohlcv_list

def insert_ohlcv_1h(db_client: DatabaseClient, ohlcv_data: list) -> int:
    """OHLCVデータをデータベースに保存
    """
    inserted_count = insert_ohlcv_1h_db(db_client, ohlcv_data)
    logger.info(f"insert_ohlcv_1h: inserted_count: {inserted_count}")
    return inserted_count


def refresh_ohlcv_1h(db_client: DatabaseClient):
    ohlcv = fetch_ohlcv_1h_from_bitget()
    converted_ohlcv = convert_ohlcv(ohlcv)
    insert_ohlcv_1h(db_client, converted_ohlcv)



        



