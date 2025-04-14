from src.database.data_access.database_client import DatabaseClient
import json
from src.logger import setup_logger

logger = setup_logger(__name__)


def create_addresses(db_client: DatabaseClient) -> None:
    query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS addresses AS
    SELECT DISTINCT
        from_address AS address,
        'exchange' as main_type,
        CASE 
            WHEN to_address = '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe' THEN 'gate'
            WHEN to_address = '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23' THEN 'bitget'
        END AS sub_type
    FROM geek_transactions
    WHERE to_address IN (
        '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe', 
        '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23')

    UNION ALL
    SELECT DISTINCT
        CASE 
            WHEN method in ('exportToken','exportAdp') THEN to_address
            WHEN method in ('xgeekToGeek','transferForBuy') THEN from_address
        END AS address,
        'game_wallet' AS main_type,
        'game_wallet' AS sub_type
    FROM geek_transactions
    WHERE method IN ('exportAdp','xgeekToGeek','transferForBuy') 
    or (method = 'exportToken'and to_address != '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62')
    
    """
    # JSONファイルを読み込む
    with open('addresses.json', 'r',encoding='utf-8') as f:
        data = json.load(f)
    # 各アドレスをUNION ALLで結合
    for addr in data:
        query += f"UNION ALL SELECT '{addr['address']}' as address, '{addr['main_type']}' AS main_type, '{addr['sub_type']}' AS sub_type "
    

    db_client.execute(query)


    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_addresses_address 
    ON addresses(address);
    """
    db_client.execute(create_index_query)
    logger.info("addressesを作成しました。")


def refresh_addresses(db_client: DatabaseClient) -> None:
    logger.info("addressesを更新します")
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY addresses;
    """
    db_client.execute(refresh_query)
    logger.info("addressesを更新しました")

if __name__ == "__main__":
    db_client = DatabaseClient()
    create_addresses(db_client)





