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


    create_daily_incremental_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_incremental AS
    WITH latest_date_table AS (
        SELECT COALESCE(MAX(date), '1970-01-01'::date) as latest_date
        FROM daily_balances_table
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
                SELECT latest_date
                FROM latest_date_table)

            UNION ALL

            SELECT 
            timestamp,
            to_address AS address,
            value AS balance_change
            FROM geek_transactions
            WHERE DATE(timestamp + INTERVAL '5 hours') >= (
            SELECT latest_date
            FROM latest_date_table)
            )
    ),
    daily_changes AS (
        SELECT
        date,
        address,
        SUM(balance_change) AS daily_change
        FROM transactions
        GROUP BY date, address

        UNION ALL

        SELECT
        date,
        address,
        balance AS daily_change
        FROM daily_balances_table
        WHERE date = (SELECT latest_date - INTERVAL '1 day' FROM latest_date_table)
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
    SELECT DISTINCT address FROM addresses
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
    db_client.execute(create_daily_incremental_query)

    # daily_balances_incrementalマテリアライズドビューにユニークインデックスを追加
    create_unique_index_query = """
    CREATE UNIQUE INDEX idx_daily_incremental_address_date 
    ON daily_incremental(address, date);
    """
    db_client.execute(create_unique_index_query)

def refresh_daily_balances_table(db_client: DatabaseClient) -> None:
    logger.info("daily_balancesの差分更新を開始します")
    
    # 差分更新用のビューを更新
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_incremental;
    """
    db_client.execute(refresh_query)
    
    # メインのビューを更新
    update_query = """
    INSERT INTO daily_balances_table (date, address, balance)
    SELECT date, address, balance
    FROM daily_incremental
    ON CONFLICT (address, date) 
    DO UPDATE SET balance = EXCLUDED.balance;
    """
    db_client.execute(update_query)
    
    
    logger.info("daily_balancesの差分更新が完了しました")

def test(db_client: DatabaseClient) -> None:
    query = """
    -- 最新日付のトランザクションの確認
SELECT DATE(timestamp + INTERVAL '5 hours') as jst_date,
       COUNT(*) as tx_count,
       SUM(CASE WHEN from_address IS NOT NULL THEN -value ELSE 0 END) as from_sum,
       SUM(CASE WHEN to_address IS NOT NULL THEN value ELSE 0 END) as to_sum
FROM geek_transactions
GROUP BY DATE(timestamp + INTERVAL '5 hours')
ORDER BY jst_date DESC
LIMIT 5;
    """
    result = db_client.fetch_all(query)
    print(result)

def test2(db_client: DatabaseClient) -> None:
    query = """
    -- daily_balances_tableの最新日付のデータを確認
SELECT date, 
       COUNT(*) as address_count,
       SUM(balance) as total_balance
FROM daily_balances_table
GROUP BY date
ORDER BY date DESC
LIMIT 5;

-- 特定のアドレスの残高推移を確認
SELECT date, balance
FROM daily_balances_table
WHERE address = '特定のアドレス'
ORDER BY date DESC
LIMIT 10;
    """
    result = db_client.fetch_all(query)
    print(result)


if __name__ == "__main__":
    db_client = DatabaseClient()
    # create_daily_balances_table(db_client)
    # refresh_daily_balances_table(db_client)
    test2(db_client)
