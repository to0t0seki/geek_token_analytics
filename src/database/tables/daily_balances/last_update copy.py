from src.database.data_access.database_client import DatabaseClient
from src.logger import setup_logger

logger = setup_logger(__name__)

def create_daily_balances_table(db_client: DatabaseClient) -> None:
    create_daily_balances_table_query = """
    CREATE TABLE IF NOT EXISTS daily_balances_table (
        date DATE NOT NULL,
        address VARCHAR(42) NOT NULL,
        balance NUMERIC(65,0) NOT NULL,
        PRIMARY KEY (date, address)
    );
    """
    db_client.execute(create_daily_balances_table_query)


    create_last_update_table_query = """
    CREATE TABLE IF NOT EXISTS daily_balances_last_update (
        last_update TIMESTAMP(6) NOT NULL,
        PRIMARY KEY (last_update)
    );
    """
    db_client.execute(create_last_update_table_query)

    create_daily_balances_incremental_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_balances_incremental AS
    WITH latest_update AS (
    SELECT COALESCE(MAX(last_update), '1970-01-01'::timestamp) as last_update
    FROM daily_balances_last_update
    ),
    transactions AS (
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
        WHERE DATE(timestamp + INTERVAL '5 hours') >= (
        SELECT DATE(last_update + INTERVAL '5 hours') 
        FROM latest_update
        )

        UNION ALL

        SELECT 
            timestamp,
            to_address AS address,
            value AS balance_change
        FROM geek_transactions
        WHERE DATE(timestamp + INTERVAL '5 hours') >= (
        SELECT DATE(last_update + INTERVAL '5 hours') 
        FROM latest_update
    )
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
    db_client.execute(create_daily_balances_incremental_query)

    # daily_balances_incrementalマテリアライズドビューにユニークインデックスを追加
    create_unique_index_query = """
    CREATE UNIQUE INDEX idx_daily_balances_incremental_address_date 
    ON daily_balances_incremental(address, date);
    """
    db_client.execute(create_unique_index_query)

def refresh_daily_balances_table(db_client: DatabaseClient) -> None:
    logger.info("daily_balancesの差分更新を開始します")
    
    # 差分更新用のビューを更新
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_balances_incremental;
    """
    db_client.execute(refresh_query)
    
    # メインのビューを更新
    update_query = """
    INSERT INTO daily_balances_table (date, address, balance)
    SELECT date, address, balance
    FROM daily_balances_incremental
    ON CONFLICT (address, date) 
    DO UPDATE SET balance = EXCLUDED.balance;
    """
    db_client.execute(update_query)
    
    # 最終更新日時を記録
    update_timestamp_query = """
    INSERT INTO daily_balances_last_update (last_update)
    SELECT MAX(timestamp)
    FROM geek_transactions
    WHERE DATE(timestamp + INTERVAL '5 hours') <= (
        SELECT MAX(date) 
        FROM daily_balances_table
    )
    ON CONFLICT (last_update) 
    DO UPDATE SET last_update = (
        SELECT MAX(timestamp)
        FROM geek_transactions
        WHERE DATE(timestamp + INTERVAL '5 hours') <= (
            SELECT MAX(date) 
            FROM daily_balances_table
        )
    );
    """
    db_client.execute(update_timestamp_query)
    
    logger.info("daily_balancesの差分更新が完了しました")

if __name__ == "__main__":
    db_client = DatabaseClient()
    # create_daily_balances_table(db_client)
    refresh_daily_balances_table(db_client)

