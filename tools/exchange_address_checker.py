from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger

logger = setup_logger(__name__)

def check_exchange_address(db_client: DatabaseClient) -> list:
    logger.info("取引所アドレスをチェックします")
    """
    取引所アドレスを取得する
    """
    query = """
    with exchange_addresses as (SELECT address
    FROM addresses
    WHERE main_type = 'exchange'
    and sub_type not in ('gate_pool','bitget_pool'))

    SELECT gt.*
    FROM geek_transactions gt
    JOIN exchange_addresses ea ON gt.to_address = ea.address OR gt.from_address = ea.address
    where gt.method not in ('transfer');
    """
    result = db_client.fetch_all(query)
    if len(result) > 0:
        logger.error(f"取引所アドレスをチェックしました。{len(result)}件の取引所アドレスが疑われるトランザクションがあります")
        return result
    else:
        logger.info("取引所アドレスが疑われるトランザクションはありませんでした")
        return []


if __name__ == "__main__":
    result = check_exchange_address(DatabaseClient())
    print(result)
