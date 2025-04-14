import requests
import time
from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger

logger = setup_logger(__name__)


def get_reorg_blocks_from_api(params: dict = {}):
    logger.debug("リオーガニゼーションを取得します")
    reorg_blocks = []
    requests_count = 0
    url = f"https://explorer.geekout-pte.com/api/v2/blocks?type=reorg"
    record_count = 0
    try:
        while True: 
            data = requests.get(url, params=params, timeout=10).json()
            requests_count += 1

            logger.debug(f"APIリクエスト {requests_count} 回目: {len(data['items'])} 件のデータを取得")
            for item in data['items']:
                reorg_blocks.append(item['height'])
                record_count += 1

            if data['next_page_params'] is not None:
                params.update(data['next_page_params'])
                logger.debug(f"次のページのデータを取得します: {params}")
                time.sleep(1)  # APIレート制限を考慮
            else:
                logger.debug("すべてのデータを取得しました")
                break
        logger.info(f"合計 {len(reorg_blocks)} 件のリオーグブロックがありました")
        return reorg_blocks
    except Exception as e:
        logger.error(f"APIリクエスト中にエラーが発生しました: {e}")
    finally:
        logger.debug(f"合計 {requests_count} 回のAPIリクエストを送信しました")
        logger.debug(f"合計 {record_count} 件のデータを取得しました")



def find_reorg_records_from_db(db_client: DatabaseClient, reorg_blocks: list):
    try:
        logger.debug("リオーグの可能性があるブロックがあるか、データベースを確認します")
        params = {"block_numbers": reorg_blocks}
        query = "SELECT * FROM geek_transactions where block_number = ANY(:block_numbers)"
        df = db_client.query_to_df(query, params)
        logger.debug(f"{len(df)} 件のリオーグブロックの可能性があります")
        return df
    except Exception as e:
        logger.error(f"find_reorg_records_from_db中にエラーが発生しました: {e}")
        return None



def check_transaction_from_api(tx_hash_list: list):
    logger.debug("リオーグの可能性があるトランザクションをチェックします")
    reorg_tx_hash_list = []
    try:
        for tx_hash in tx_hash_list:
            logger.debug(f"{tx_hash} をチェックします")
            url = f"https://explorer.geekout-pte.com/api/v2/transactions/{tx_hash}"
            data = requests.get(url, timeout=10).json()
            message = data.get('message')
            if message is not None:
                logger.info(f"{tx_hash} はリオーガブロックです")
                reorg_tx_hash_list.append(tx_hash)
        logger.info(f"{len(reorg_tx_hash_list)} 件のリオーグブロックがあります")
        return reorg_tx_hash_list
            
    except Exception as e:
        logger.error(f"check_transaction_from_api中にエラーが発生しました: {e}")
        return None

def check_record_count_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            db_client = DatabaseClient()
            query = "SELECT COUNT(*) FROM geek_transactions"
            count, = db_client.fetch_one(query)
            logger.info(f"削除前のレコード数: {count}")
            result = func(*args, **kwargs)
            query = "SELECT COUNT(*) FROM geek_transactions"
            count, = db_client.fetch_one(query)
            logger.info(f"削除後のレコード数: {count}")
        except Exception as e:
            logger.error(f"check_record_count_decorator中にエラーが発生しました: {e}")
            return None
    return wrapper

@check_record_count_decorator
def delete_reorg_records_from_db(db_client: DatabaseClient, tx_hash: list):
    try:
        logger.error(f"{len(tx_hash)}件のリオーグブロックを削除します")
        query = "DELETE FROM geek_transactions WHERE tx_hash = ANY(:tx_hashes)"
        params = {"tx_hashes": tx_hash}
        db_client.execute(query, params)
        logger.error("リオーグブロックを削除しました")
    except Exception as e:
        logger.error(f"delete_reorg_records_from_db中にエラーが発生しました: {e}")


def cleanup_reorg_records(client: DatabaseClient):
    logger.info("リオーガニゼーションを開始します")
    reorg_blocks = get_reorg_blocks_from_api()
    if not reorg_blocks:
        logger.info("リオーグブロックがありませんでした")
        return
    
    df = find_reorg_records_from_db(client, reorg_blocks)
    if df.empty:
        logger.info("リオーグの可能性があるブロックがありませんでした")
        return
    
    tx_hash_list = df['tx_hash'].to_list()
    reorg_tx_hash_list = check_transaction_from_api(tx_hash_list)
    if len(reorg_tx_hash_list) > 0:
        delete_reorg_records_from_db(client, reorg_tx_hash_list)
    else:
        logger.info("リオーグブロックはありませんでした")
    
    logger.info("リオーガニゼーションを終了します")



if __name__ == "__main__":
    client = DatabaseClient()
    cleanup_reorg_records(client)

