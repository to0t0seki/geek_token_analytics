import requests
import time
import sys
from typing import Dict, Any
from datetime import datetime
from src.data_access.database_client import DatabaseClient


def create_normalized_tables(db_client: DatabaseClient) -> None:
    """正規化されたテーブルを作成する"""
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS geek_transactions_oasys (
        block_number INTEGER NOT NULL,
        log_index INTEGER NOT NULL,
        tx_hash VARCHAR(66),
        timestamp TIMESTAMP(6),
        from_address VARCHAR(42),
        to_address VARCHAR(42),
        value NUMERIC(65,0),
        method VARCHAR(20),
        type VARCHAR(20),
        PRIMARY KEY (block_number, log_index)
    );
    """
    db_client.execute(create_transactions_table)

 

    create_index_timestamp = """
    CREATE INDEX IF NOT EXISTS idx_gt_timestamp ON geek_transactions_oasys(timestamp);
    """
    result = db_client.execute(create_index_timestamp)
    if result > 0:
        print("timestampインデックスが作成されました")
        

    
    create_index_from_address = """
    CREATE INDEX IF NOT EXISTS idx_gt_from_address ON geek_transactions_oasys(from_address);
    """
    result = db_client.execute(create_index_from_address)
    if result > 0:
        print("from_addressインデックスが作成されました")

    
    create_index_to_address = """
    CREATE INDEX IF NOT EXISTS idx_gt_to_address ON geek_transactions_oasys(to_address);
    """
    result = db_client.execute(create_index_to_address)
    if result > 0:
        print("to_addressインデックスが作成されました")

def insert_normalized_data(db_client: DatabaseClient, data: Dict[str, Any]) -> None:
    try:
        """正規化されたデータを挿入する"""

        params = {
            'block_number': data['block_number'],
            'log_index': data['log_index'],
            'tx_hash': data['tx_hash'],
            'timestamp': data['timestamp'],
            'from_address': data['from_address'],
            'to_address': data['to_address'],
            'value': data['value'],
            'method': data['method'],
            'type': data['type']
        }

        insert_transfer_detail_query = """
        INSERT INTO geek_transactions_oasys (block_number, log_index, tx_hash, timestamp, from_address, to_address, value, method, type)
        VALUES (%(block_number)s, %(log_index)s, %(tx_hash)s, %(timestamp)s, %(from_address)s, %(to_address)s, %(value)s, %(method)s, %(type)s)
        ON CONFLICT (block_number, log_index) DO NOTHING
        """
        result = db_client.execute(insert_transfer_detail_query, params)
        if result > 0:
            # print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} データを挿入しました: {params}")
            pass
        elif result == 0:
            # print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} データは既に存在します: {params}")
            pass
        else:
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} データを挿入できませんでした: {result}")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} insert_normalized_data中にエラーが発生しました: {e}")

def get_letest_transaction():
    try:
        db_client = DatabaseClient()
        query = """
        SELECT block_number, log_index
        FROM geek_transactions_oasys
        ORDER BY block_number DESC, log_index DESC
        limit 1
        """
        return db_client.fetch_one(query)
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} get_letest_transaction中にエラーが発生しました: {e}")


def get_geek_data(params: dict = {}):
    requests_count = 0
    url = "https://explorer.oasys.games/api/v2/tokens/0x7CF763C9Ff650BF9e2EEbEE43bBC539c799d4566/transfers"
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
                # time.sleep(1)  # APIレート制限を考慮
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
    url = "https://explorer.oasys.games/api/v2/tokens/0x7CF763C9Ff650BF9e2EEbEE43bBC539c799d4566/transfers"
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
                # time.sleep(1)  # APIレート制限を考慮
            else:
                print("すべてのデータを取得しました")
                break

    except Exception as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
    finally:
        print(f"合計 {requests_count} 回のAPIリクエストを送信しました")
        print(f"合計 {record_count} 件のデータを挿入しました")


def create_trigger() -> None:
    print("create_triggerを実行します")
    try:
        query = """
        DROP TRIGGER IF EXISTS trg_insert_geek_transactions ON geek_transactions;


        CREATE OR REPLACE FUNCTION insert_daily_changes() RETURNS TRIGGER AS $$
        BEGIN
            BEGIN   
                RAISE NOTICE 'トリガーが発火しました: block_number=%, log_index=%', 
                NEW.block_number, 
                NEW.log_index;
           
                -- from_addressの処理（マイナス値）
                INSERT INTO daily_changes (date, address, change)
                VALUES (
                    (NEW.timestamp + interval '5 hours')::date,  -- timestampを+5時間してdate型に変換
                    NEW.from_address,
                    -NEW.value  -- マイナス値として設定
                )
                ON CONFLICT (date, address) 
                DO UPDATE SET change = daily_changes.change + EXCLUDED.change;

                -- to_addressの処理（プラス値）
                INSERT INTO daily_changes (date, address, change)
                VALUES (
                    (NEW.timestamp + interval '5 hours')::date,  -- timestampを+5時間してdate型に変換
                    NEW.to_address,
                    NEW.value  -- プラス値として設定
                )
                ON CONFLICT (date, address) 
                DO UPDATE SET change = daily_changes.change + EXCLUDED.change;

                RETURN NEW;

            EXCEPTION WHEN OTHERS THEN
                RAISE EXCEPTION 'トリガー内でエラーが発生しました: block_number=%, log_index=%, error: %', 
                    NEW.block_number, 
                    NEW.log_index,
                    SQLERRM;
            END;
        END;
        $$
        LANGUAGE plpgsql;

        CREATE TRIGGER trg_insert_geek_transactions
        AFTER INSERT ON geek_transactions
        FOR EACH ROW
        EXECUTE FUNCTION insert_daily_changes();
        """
        client = DatabaseClient()
        client.execute(query)
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_trigger中にエラーが発生しました: {e}")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_triggerが正常に実行されました")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        get_geek_data()
    elif len(sys.argv) >= 2:
        if sys.argv[1] == "resume":
            resume_geek_data(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "create_trigger":
            create_trigger()
    else:
        print("引数が不正です")


