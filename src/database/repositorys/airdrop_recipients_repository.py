from src.database.data_access.database_client import DatabaseClient


def create_airdrop_recipients(db_client: DatabaseClient) -> None:
    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS airdrop_recipients AS
    SELECT DISTINCT to_address as address
    FROM airdrops
    """
    db_client.execute(create_query)

    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_airdrop_recipients_address 
    ON airdrop_recipients(address);
    """
    db_client.execute(create_index_query)

def refresh_airdrop_recipients(db_client: DatabaseClient) -> None:
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY airdrop_recipients;
    """
    db_client.execute(refresh_query)


