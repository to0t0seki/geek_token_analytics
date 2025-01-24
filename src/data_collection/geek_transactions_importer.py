import requests
import time
from src.logger import setup_logger
from src.database.geek_transactions_repository import (
    insert_geek_transactions as insert_geek_transactions_db,
    fetch_letest_transaction as fetch_letest_transaction_db
)
from src.database.geek_transactions_repository import DatabaseClient

logger = setup_logger(__name__)

def _fetch_geek_transactions(params: dict={}) -> tuple[list, dict]:
    url = "https://explorer.geekout-pte.com/api/v2/tokens/0x3741FcB5792673eF220cCc0b95B5B8C38c5f2723/transfers"
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
    logger.info(f"fetch_geek_transactions: start_block_number: {start_block_number}, start_index: {start_index}, end_block_number: {end_block_number}, end_index: {end_index}")
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
    latest_block_number = geek_transactions[0]['block_number']
    latest_index = geek_transactions[0]['log_index']
    oldest_block_number = geek_transactions[total_transactions - 1]['block_number']
    oldest_index = geek_transactions[total_transactions - 1]['log_index']

    logger.info(f"fetch_geek_transactions: total_transactions: {total_transactions}, latest_block_number: {latest_block_number}, latest_index: {latest_index}, oldest_block_number: {oldest_block_number}, oldest_index: {oldest_index}")
    return geek_transactions


def insert_geek_transactions(db_client: DatabaseClient, transactions: list) -> int:
    logger.info(f" insert_geek_transactions: insert_count: {len(transactions)}")
    inserted_count = insert_geek_transactions_db(db_client, transactions)
    logger.info(f" insert_geek_transactions: inserted_count: {inserted_count}")
    return inserted_count

def fetch_letest_transaction(db_client: DatabaseClient) -> tuple[int, int]:
    latest_block_number, latest_log_index = fetch_letest_transaction_db(db_client)
    logger.info(f"fetch_letest_transaction: latest_block_number: {latest_block_number}, latest_log_index: {latest_log_index}")
    return latest_block_number, latest_log_index
    
   
def update_geek_transactions(db_client: DatabaseClient):
    latest_block_number, latest_log_index = fetch_letest_transaction(db_client)
    geek_transactions = fetch_geek_transactions(end_block_number=latest_block_number,end_index=latest_log_index)
    insert_geek_transactions(db_client, geek_transactions)
    fetch_letest_transaction(db_client)

    
    





