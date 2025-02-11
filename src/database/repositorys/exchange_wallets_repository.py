from src.database.data_access.database_client import DatabaseClient


def create_exchange_wallets(db_client: DatabaseClient) -> None:
    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS exchange_wallets AS
    SELECT DISTINCT
        from_address AS address,
        CASE 
            WHEN to_address = '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe' THEN 'gate.io'
            WHEN to_address = '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23' THEN 'bitget'
        END AS exchange
    FROM geek_transactions
    WHERE to_address IN (
        '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe', 
        '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23')
    """
    db_client.execute(create_query)


    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_exchange_wallets_address 
    ON exchange_wallets(address);
    """
    db_client.execute(create_index_query)


def refresh_exchange_wallets(db_client: DatabaseClient) -> None:
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY exchange_wallets;
    """
    db_client.execute(refresh_query)




