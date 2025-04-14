from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger

logger = setup_logger(__name__)

def create_latest_balances(db_client: DatabaseClient) -> None:
    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS latest_balances AS
    SELECT
        db.date,
        db.address,
        db.balance,
        COALESCE(a.main_type, 'others') AS main_type,
        a.sub_type
    FROM daily_balances db
    LEFT JOIN addresses a ON db.address = a.address
    WHERE date = CURRENT_DATE
    """
    db_client.execute(create_query)
    

    create_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_latest_balances_address 
    ON latest_balances(address);
    """
    db_client.execute(create_index_query)
    logger.info("latest_balancesを作成しました。")
 

def refresh_latest_balances(db_client: DatabaseClient) -> None:
    logger.info("latest_balancesを更新します")
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY latest_balances;
    """
    db_client.execute(refresh_query)
    logger.info("latest_balancesを更新しました")

if __name__ == "__main__":
    db_client = DatabaseClient()
    create_latest_balances(db_client)
