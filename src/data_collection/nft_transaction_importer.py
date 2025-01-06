import requests
import time
from typing import Dict, Any
from src.data_access.client import DatabaseClient

def create_normalized_tables(db_client: DatabaseClient) -> None:
    """正規化されたテーブルを作成する"""
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS nft_transactions (
        block_number INTEGER NOT NULL,
        log_index INTEGER NOT NULL,
        tx_hash VARCHAR(66),
        timestamp TIMESTAMP(6),
        from_address VARCHAR(42),
        to_address VARCHAR(42),
        token_id VARCHAR(10),
        method VARCHAR(20),
        type VARCHAR(20),
        PRIMARY KEY (block_number, log_index)
    )
    """
    db_client.execute(create_transactions_table)


def insert_normalized_data(db_client: DatabaseClient, data: Dict[str, Any]) -> None:
    """正規化されたデータを挿入する"""
    params = {
        'block_number': data['block_number'],
        'log_index': data['log_index'],
        'tx_hash': data['tx_hash'],
        'timestamp': data['timestamp'],
        'from_address': data['from_address'],
        'to_address': data['to_address'],
        'token_id': data['token_id'],
        'method': data['method'],
        'type': data['type']
    }
    insert_transfer_detail_query = """
    INSERT INTO nft_transactions (block_number, log_index, tx_hash, timestamp, from_address, to_address, token_id, method, type)
    VALUES (%(block_number)s, %(log_index)s, %(tx_hash)s, %(timestamp)s, %(from_address)s, %(to_address)s, %(token_id)s, %(method)s, %(type)s)
    ON CONFLICT (block_number, log_index) DO NOTHING
    """
    db_client.execute(insert_transfer_detail_query, params)

def get_letest_transaction():
    db_client = DatabaseClient()
    query = """
    SELECT block_number, log_index
    FROM nft_transactions
    ORDER BY block_number DESC, log_index DESC
    limit 1
    """
    return db_client.fetch_one(query)


def get_nft_data():
    requests_count = 0
    url = f"https://explorer.geekout-pte.com/api/v2/tokens/0x22f8208AB7AC444A76a93547C7800411dB8Ec0F1/transfers"
    params = {}
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
                    'token_id': item['total']['token_id'],
                    'method': item['method'],
                    'type': item['type']
                }
                insert_normalized_data(db_client, transaction)
                record_count += 1

            if data['next_page_params'] is not None and data['next_page_params']['block_number'] > 1800000:
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
    get_nft_data()
    


    ##第1回目NFTsell 11/12 22:00:00 jst
    ##第1回NFTsellの返金対応完了 11/13 17:00:00 jst
    ##第2回目NFTsell 11/19 22:00:00 jst
    ##第3回目NFTsell 11/25 19:00:00 jst
    ##第3回のNFT配布12/3 19:45:00 jstから20:45:00 jst
    ##0x79dfACcE43E901a5f64C292BF62ba2AE0d25CEF8からsafeTransferFromにて送る
    ##全てのメソッド['mint' '0xc0c30933' 'exportNftToken' 'transferFrom' '0xe3456fbb''safeTransferFrom']
    
    ##exportNftToken:ストレージから出すメソッド
    ##0x79dfACcE43E901a5f64C292BF62ba2AE0d25CEF8から

    ##ストレージに入れる時transferFrom

    ##safeTransferFrom:2241件:NFTセールで運営から配布
    
    ##0xc0c30933:32464件
    ##     28               100  2024-12-03T05:05:18.000000Z
    ## 29              1000  2024-12-03T05:06:13.000000Z
    ## 30              1000  2024-12-03T05:07:08.000000Z
    ## 31              1000  2024-12-03T05:07:53.000000Z
    ## 32              1000  2024-12-03T05:08:43.000000Z
    ## 33               900  2024-12-03T05:09:38.000000Z



    ##mint:16167件
    ##        count(timestamp)                    timestamp
    ## 0             11167  2024-08-06T13:36:58.000000Z
    ## 1              5000  2024-12-03T04:52:48.000000Z

    ##0xe3456fbb: NFTsell mintメソッド
  
    

