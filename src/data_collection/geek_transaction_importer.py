import requests
import time
from typing import Dict, Any
from src.data_access.client import DatabaseClient


def create_normalized_tables(db_client: DatabaseClient) -> None:
    """正規化されたテーブルを作成する"""
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS geek_transactions (
        block_number INT NOT NULL,
        log_index INT NOT NULL,
        tx_hash VARCHAR(66),
        timestamp DATETIME(6),
        from_address VARCHAR(42),
        to_address VARCHAR(42),
        value DECIMAL(65,0),
        method VARCHAR(20),
        type VARCHAR(20),
        PRIMARY KEY (block_number, log_index)
    );
    """
    db_client.execute(create_transactions_table)

    # インデックスが存在するか確認
    index_exists = db_client.fetch_one("""
    SHOW INDEX FROM geek_transactions WHERE Key_name = 'idx_gt_timestamp';
    """)

    if not index_exists:
        create_index_timestamp = """
        CREATE INDEX idx_gt_timestamp ON geek_transactions(timestamp);
        """
        db_client.execute(create_index_timestamp)
        print("timestampインデックスが作成されました")
        

    index_exists = db_client.fetch_one("""
    SHOW INDEX FROM geek_transactions WHERE Key_name = 'idx_gt_from_address';
    """)

    if not index_exists:
        create_index_from_address = """
        CREATE INDEX idx_gt_from_address ON geek_transactions(from_address);
        """
        db_client.execute(create_index_from_address)
        print("from_addressインデックスが作成されました")

    index_exists = db_client.fetch_one("""
    SHOW INDEX FROM geek_transactions WHERE Key_name = 'idx_gt_to_address';
    """)

    if not index_exists:
        create_index_to_address = """
        CREATE INDEX idx_gt_to_address ON geek_transactions(to_address);
        """
        db_client.execute(create_index_to_address)
        print("to_addressインデックスが作成されました")

def insert_normalized_data(db_client: DatabaseClient, data: Dict[str, Any]) -> None:
    """正規化されたデータを挿入する"""

    insert_transfer_detail_query = """
    INSERT IGNORE INTO geek_transactions (block_number, log_index, tx_hash, timestamp, from_address, to_address, value, method, type)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    db_client.execute_params(insert_transfer_detail_query, (data['block_number'], data['log_index'], data['tx_hash'], data['timestamp'], data['from_address'], data['to_address'], data['value'], data['method'], data['type']))
    
def get_letest_transaction():
    db_client = DatabaseClient()
    query = """
    SELECT block_number, log_index
    FROM geek_transactions
    ORDER BY block_number DESC, log_index DESC
    limit 1
    """
    return db_client.fetch_one(query)


def get_geek_data(params: dict = {}):
    requests_count = 0
    url = f"https://explorer.geekout-pte.com/api/v2/tokens/0x3741FcB5792673eF220cCc0b95B5B8C38c5f2723/transfers"
    db_client = DatabaseClient()
    create_normalized_tables(db_client)
    latest_block_number, latest_log_index = get_letest_transaction() if get_letest_transaction() else (0, 0)
    record_count = 0
    
    try:
        while True: 
            data = requests.get(url, params=params, timeout=10).json()
            requests_count += 1

            print(f"APIリクエスト {requests_count} 回目: {len(data['items'])} 件のデータを取得")
            for item in data['items']:
                # 既存のデータに到達した場合は終了
                if item['block_number'] < latest_block_number or \
                   (item['block_number'] == latest_block_number and item['log_index'] < latest_log_index):
                    print("既存のデータに到達しました")
                    return
                

                transaction = {
                    'block_number': item['block_number'],
                    'log_index': item['log_index'],
                    'tx_hash': item['tx_hash'],
                    'timestamp': item['timestamp'].replace('T', ' ').replace('Z', ''),
                    'from_address': item['from']['hash'],
                    'to_address': item['to']['hash'],
                    'value': item['total']['value'],
                    'method': item['method'],
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


def resume_geek_data(block_number, log_index):
    requests_count = 0
    url = f"https://explorer.geekout-pte.com/api/v2/tokens/0x3741FcB5792673eF220cCc0b95B5B8C38c5f2723/transfers"
    db_client = DatabaseClient()
    create_normalized_tables(db_client)
    record_count = 0
    params = {
        'block_number': block_number,
        'index': log_index
    }
        
    try:
        while True: 
            data = requests.get(url, params=params, timeout=10).json()
            requests_count += 1

            print(f"APIリクエスト {requests_count} 回目: {len(data['items'])} 件のデータを取得")
            for item in data['items']:
                transaction = {
                    'block_number': item['block_number'],
                    'log_index': item['log_index'],
                    'tx_hash': item['tx_hash'],
                    'timestamp': item['timestamp'].replace('T', ' ').replace('Z', ''),
                    'from_address': item['from']['hash'],
                    'to_address': item['to']['hash'],
                    'value': item['total']['value'],
                    'method': item['method'],
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
    # response = get_geek_data({'block_number': 1433326, 'index': 1})
    # print(generate_url_with_params(params={'block_number': 1433326, 'log_index': 1}))
    get_geek_data()
    # resume_geek_data(2180939, 2)
    # calculate_today_balances()