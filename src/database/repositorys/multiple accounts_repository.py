from src.database.data_access.database_client import DatabaseClient


def create_multiple_accounts(db_client: DatabaseClient) -> None:
    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS multiple_accounts AS
    SELECT gt.*
    FROM geek_transactions gt
    INNER JOIN airdrop_recipients ar ON gt.from_address = ar.address
    INNER JOIN exchange_wallets ew ON gt.to_address = ew.address;
    """
    db_client.execute(create_query)
    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_multiple_accounts_address 
    ON multiple_accounts(address);
    """
    db_client.execute(create_index_query)


def refresh_multiple_accounts(db_client: DatabaseClient) -> None:
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY multiple_accounts;
    """
    db_client.execute(refresh_query)



