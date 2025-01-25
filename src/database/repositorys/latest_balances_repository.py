from src.database.data_access.database_client import DatabaseClient


def create_latest_balances(db_client: DatabaseClient) -> None:
    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS latest_balances AS
    SELECT date, address, balance
    FROM daily_balances
    WHERE date = CURRENT_DATE
    """
    db_client.execute(create_query)

    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_latest_balances_address 
    ON latest_balances(address);
    """
    db_client.execute(create_index_query)
 

def refresh_latest_balances(db_client: DatabaseClient) -> None:
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY latest_balances;
    """
    db_client.execute(refresh_query)
