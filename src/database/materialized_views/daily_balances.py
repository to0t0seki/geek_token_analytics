from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger

logger = setup_logger(__name__)

def create_daily_balances(db_client: DatabaseClient) -> None:
    create_query = """
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_balances AS
WITH transactions AS (
    SELECT
        DATE(timestamp + INTERVAL '5 hours') AS date,
        address,
        balance_change
    FROM (
        SELECT 
            timestamp,
            from_address AS address,
            -value AS balance_change
        FROM geek_transactions

        UNION ALL

        SELECT 
            timestamp,
            to_address AS address,
            value AS balance_change
        FROM geek_transactions
    ) t
),

daily_changes AS (
    SELECT
        date,
        address,
        SUM(balance_change) AS daily_change
    FROM transactions
    GROUP BY date, address
),

filled_balances AS (
    SELECT
        t.date,
        a.address,
        COALESCE(dc.daily_change, 0) AS daily_change
    FROM (
        SELECT DISTINCT date FROM transactions
    ) t
    CROSS JOIN (
        SELECT DISTINCT address FROM transactions
    ) a
    LEFT JOIN daily_changes dc
        ON t.date = dc.date
        AND a.address = dc.address
)
SELECT
    date,
    address,
    SUM(daily_change) OVER (
        PARTITION BY address
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS balance
FROM filled_balances
    """
    db_client.execute(create_query)

    create_index_query = """
    CREATE UNIQUE INDEX idx_daily_balances_address_date 
    ON daily_balances(address, date);
    """
    db_client.execute(create_index_query)


def refresh_daily_balances(db_client: DatabaseClient) -> None:
    logger.info("daily_balancesを更新します")
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_balances;
    """
    db_client.execute(refresh_query) 
    logger.info("daily_balancesを更新しました")

if __name__ == "__main__":
    db_client = DatabaseClient()
    create_daily_balances(db_client)

