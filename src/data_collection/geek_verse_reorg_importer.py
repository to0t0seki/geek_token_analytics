import requests
import time
from typing import Dict, Any
from src.data_access.client import DatabaseClient

def create_normalized_tables(db_client: DatabaseClient) -> None:
    """正規化されたテーブルを作成する"""
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS reorg_blocks (
        height INT NOT NULL,
        block_hash VARCHAR(66),
        timestamp DATETIME(6),
        PRIMARY KEY (height),
        tx_count INT,
        transaction_count INT,
        type VARCHAR(20)
    );
    """
    db_client.execute(create_transactions_table)


def insert_normalized_data(db_client: DatabaseClient, data: Dict[str, Any]) -> None:
    """正規化されたデータを挿入する"""

    insert_transfer_detail_query = """
    INSERT IGNORE INTO reorg_blocks (height, block_hash, timestamp, tx_count, transaction_count, type)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    db_client.execute(insert_transfer_detail_query, (data['height'], data['block_hash'], data['timestamp'], data['tx_count'], data['transaction_count'], data['type']))
    
def get_letest_block():
    db_client = DatabaseClient()
    query = """
    SELECT height
    FROM reorg_blocks
    ORDER BY height DESC
    limit 1
    """
    return db_client.fetch_one(query)


def get_reorg_data(params: dict = {}):
    requests_count = 0
    url = "https://explorer.geekout-pte.com/api/v2/blocks?type=reorg"
    db_client = DatabaseClient()
    create_normalized_tables(db_client)
    latest_height = get_letest_block() if get_letest_block() else (0)
    record_count = 0
    
    try:
        while True: 
            data = requests.get(url, params=params, timeout=10).json()
            requests_count += 1

            print(f"APIリクエスト {requests_count} 回目: {len(data['items'])} 件のデータを取得")
            for item in data['items']:
                # 既存のデータに到達した場合は終了
                if item['height'] < latest_height:
                    print("既存のデータに到達しました")
                    return
                

                transaction = {
                    'height': item['height'],
                    'block_hash': item['hash'],
                    'timestamp': item['timestamp'].replace('T', ' ').replace('Z', ''),
                    'tx_count': item['tx_count'],
                    'transaction_count': item['transaction_count'],
                    'type': item['type']
                }
                insert_normalized_data(db_client, transaction)
                record_count += 1

            if data['next_page_params'] is not None:
                params.update(data['next_page_params'])
                print(f"次のページのデータを取得します: {params}")
                time.sleep(1)  # APIレート制限を考慮
            else:
                print("すべてのデータを取得しました")
                break

    except Exception as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
    finally:
        print(f"合計 {requests_count} 回のAPIリクエストを送信しました")
        print(f"合計 {record_count} 件のデータを挿入しました")




if __name__ == "__main__":
    get_reorg_data()
  