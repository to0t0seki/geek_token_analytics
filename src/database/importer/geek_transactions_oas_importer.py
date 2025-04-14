import requests
import time
from src.logger import setup_logger
from src.database.tables.geek_transactions_oas import (
    insert_geek_transactions as insert_geek_transactions_db,
    fetch_letest_transaction as fetch_letest_transaction_db,
    create_geek_transactions as create_geek_transactions_db
)
from src.database.data_access.database_client import DatabaseClient

logger = setup_logger(__name__)

def _fetch_geek_transactions(params: dict={}) -> tuple[list, dict]:
    url = "https://explorer.oasys.games/api/v2/tokens/0x7CF763C9Ff650BF9e2EEbEE43bBC539c799d4566/transfers"
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    result = response.json()
    transactions = result['items']
    next_page_params = result['next_page_params']
    return transactions, next_page_params

def _transform_transaction(raw_transaction: dict) -> dict:
    """APIレスポンスをDB形式に変換する"""
    return {
        'block_number': raw_transaction['block_number'],
        'log_index': raw_transaction['log_index'],
        'tx_hash': raw_transaction['tx_hash'],
        'timestamp': raw_transaction['timestamp'].replace('T', ' ').replace('Z', ''),
        'from_address': raw_transaction['from']['hash'],
        'to_address': raw_transaction['to']['hash'],
        'value': raw_transaction['total']['value'],
        'method': raw_transaction['method'],
        'type': raw_transaction['type']
    }


def fetch_geek_transactions(start_block_number: int = None, start_index: int = None,  end_block_number: int = 0, end_index: int = 0) -> list:
    logger.debug(f"APIからトランザクションを取得します:終了予定ブロック番号: {end_block_number}, 終了予定インデックス: {end_index}")
    logger.debug(f"取得開始ブロック番号: {start_block_number}, 取得開始インデックス: {start_index}")
    geek_transactions = []

    if (start_block_number is None) != (start_index is None):
        raise ValueError("start_block_numberとstart_indexは両方とも指定するか、両方とも指定しないでください")
   
    
    params = {
        "block_number": start_block_number,
        "index": start_index,
    }

    while True:
        new_transactions = []
        raw_transactions, next_page_params = _fetch_geek_transactions(params)
        

        for raw_transaction in raw_transactions:
            new_transaction = _transform_transaction(raw_transaction)
            new_transactions.append(new_transaction)

        if next_page_params is None:
            geek_transactions.extend(new_transactions)
            break

        next_page_block_number = next_page_params['block_number']
        next_page_index = next_page_params['index']

        # 以下の場合にループを終了:
        # 1. 目標のブロック番号を下回った
        # 2. 同じブロック番号で目標のインデックス以下になった
        should_stop = (next_page_block_number < end_block_number or
                    (next_page_block_number == end_block_number and next_page_index <= end_index))
        if should_stop:
            for transaction in new_transactions:
                current_block_number = transaction['block_number']
                current_index = transaction['log_index']

                if (current_block_number > end_block_number or
                    (current_block_number == end_block_number and current_index > end_index)):
                    geek_transactions.append(transaction)
            break

        geek_transactions.extend(new_transactions)

        params = next_page_params
        time.sleep(1)
    total_transactions = len(geek_transactions)
    if total_transactions == 0:
        logger.info("APIからトランザクションを取得しました: 0件")
        return []
    latest_block_number = geek_transactions[0]['block_number']
    latest_index = geek_transactions[0]['log_index']
    oldest_block_number = geek_transactions[total_transactions - 1]['block_number']
    oldest_index = geek_transactions[total_transactions - 1]['log_index']

    logger.debug(f"APIからトランザクションを取得しました: {total_transactions}件, 取得した最新のブロック番号: {latest_block_number}, 取得した最新のインデックス: {latest_index}, 取得した最古のブロック番号: {oldest_block_number}, 取得した最古のインデックス: {oldest_index}")
    return geek_transactions


def insert_geek_transactions(db_client: DatabaseClient, transactions: list) -> int:
    logger.debug(f" トランザクションを挿入します")
    inserted_count = insert_geek_transactions_db(db_client, transactions)
    logger.info(f" トランザクションを挿入しました: {inserted_count}件")
    return inserted_count

def fetch_letest_transaction(db_client: DatabaseClient) -> tuple[int, int]:
    logger.debug("データベースから最新のトランザクションを取得します")
    latest_block_number, latest_log_index = fetch_letest_transaction_db(db_client)
    logger.debug(f"データベースから最新のトランザクションを取得しました: 最新のブロック番号: {latest_block_number}, 最新のインデックス: {latest_log_index}")
    return latest_block_number, latest_log_index
    
   
def update_geek_transactions(db_client: DatabaseClient):
    logger.info("geek_transactions_oasを開始します")
    create_geek_transactions_db(db_client)
    latest_block_number, latest_log_index = fetch_letest_transaction(db_client)
    geek_transactions = fetch_geek_transactions(end_block_number=latest_block_number,end_index=latest_log_index)
    if len(geek_transactions) == 0:
        logger.info("新しいトランザクションがありません")
        return
    insert_geek_transactions(db_client, geek_transactions)
    fetch_letest_transaction(db_client)
    logger.info("geek_transactions_oasを終了します")


   
    





