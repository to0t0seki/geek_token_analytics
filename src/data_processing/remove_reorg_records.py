import requests
import time
from src.data_access.database_client import DatabaseClient

def get_reorg_blocks_from_api(params: dict = {}):
    reorg_blocks = []
    requests_count = 0
    url = f"https://explorer.geekout-pte.com/api/v2/blocks?type=reorg"
    record_count = 0
    try:
        while True: 
            data = requests.get(url, params=params, timeout=10).json()
            requests_count += 1

            print(f"APIリクエスト {requests_count} 回目: {len(data['items'])} 件のデータを取得")
            for item in data['items']:
                reorg_blocks.append(item['height'])
                record_count += 1

            if data['next_page_params'] is not None:
                params.update(data['next_page_params'])
                print(f"次のページのデータを取得します: {params}")
                time.sleep(1)  # APIレート制限を考慮
            else:
                print("すべてのデータを取得しました")
                break
        return reorg_blocks
    except Exception as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
    finally:
        print(f"合計 {requests_count} 回のAPIリクエストを送信しました")
        print(f"合計 {record_count} 件のデータを取得しました")



def find_reorg_records_from_db(db_client: DatabaseClient, reorg_blocks: list):
    try:
        print(f"{len(reorg_blocks)} 件のブロックを検索します")
        params = (reorg_blocks,)
        query = f"SELECT * FROM geek_transactions where block_number = ANY(%s)"
        df = db_client.query_to_df(query, params)
        print(f"{len(df)} 件のトランザクションを取得しました")
        return df
    except Exception as e:
        print(f"find_reorg_records_from_db中にエラーが発生しました: {e}")
        return None



def check_transaction_from_api(tx_hash_list: list):
    reorg_tx_hash_list = []
    try:
        for tx_hash in tx_hash_list:
            print(f"{tx_hash} をチェックします")
            url = f"https://explorer.geekout-pte.com/api/v2/transactions/{tx_hash}"
            data = requests.get(url, timeout=10).json()
            message = data.get('message')
            if message is not None:
                print(f"{tx_hash} はリオーガニゼーションです")
                reorg_tx_hash_list.append(tx_hash)
        return reorg_tx_hash_list
            
    except Exception as e:
        print(f"check_transaction_from_api中にエラーが発生しました: {e}")
        return None

def check_record_count_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            db_client = DatabaseClient()
            query = "SELECT COUNT(*) FROM geek_transactions"
            count, = db_client.fetch_one(query)
            print(f"削除前のレコード数: {count}")
            result = func(*args, **kwargs)
            query = "SELECT COUNT(*) FROM geek_transactions"
            count, = db_client.fetch_one(query)
            print(f"削除後のレコード数: {count}")
        except Exception as e:
            print(f"check_record_count_decorator中にエラーが発生しました: {e}")
            return None
    return wrapper

@check_record_count_decorator
def delete_reorg_records_from_db(db_client: DatabaseClient, tx_hash: list):
    try:
        print(f"{len(tx_hash)}件のトランザクションを削除します")
        query = f"DELETE FROM geek_transactions WHERE tx_hash = ANY(%s)"
        db_client.execute(query, tuple(tx_hash))
    except Exception as e:
        print(f"delete_reorg_records_from_db中にエラーが発生しました: {e}")


def cleanup_reorg_records():
    client = DatabaseClient()
    reorg_blocks = get_reorg_blocks_from_api()
    if not reorg_blocks:
        print("reorg_blocksが取得できませんでした")
        return
    
    df = find_reorg_records_from_db(client, reorg_blocks)
    if df.empty:
        print("削除対象のレコードがありませんでした")
        return
    
    tx_hash_list = df['tx_hash'].to_list()
    reorg_tx_hash_list = check_transaction_from_api(tx_hash_list)
    if len(reorg_tx_hash_list) > 0:
        print(f"{len(reorg_tx_hash_list)}件のリオーガニゼーションを削除します")
        delete_reorg_records_from_db(client, reorg_tx_hash_list)
    else:
        print("リオーガニゼーションであるtxはありませんでした")



if __name__ == "__main__":
    cleanup_reorg_records()

