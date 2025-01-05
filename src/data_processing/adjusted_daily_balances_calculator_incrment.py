from src.data_access.client import DatabaseClient

def create_daily_players_balance_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS daily_players_balance (
        date DATE PRIMARY KEY,
        balance DECIMAL(65,0)
    );
    """
    db_client = DatabaseClient()
    db_client.execute(create_table_query)

def calculate_daily_players_balance():
    query = """
    INSERT INTO daily_players_balance (date, address, balance)
    WITH adjusted_transactions AS (
    SELECT
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) AS date,
        from_address AS address,
        -value AS balance_change
    FROM geek_transactions
    WHERE from_address IS NOT NULL

    UNION ALL

    SELECT
        DATE(DATE_ADD(timestamp, INTERVAL 5 HOUR)) AS date,
        to_address AS address,
        value AS balance_change
    FROM geek_transactions
    WHERE to_address IS NOT NULL
    ),
    aggregated_balances AS (
    SELECT
        date,
        address,
        SUM(balance_change) AS daily_change
    FROM adjusted_transactions
    GROUP BY date, address
    ),
    date_series AS (
    SELECT DISTINCT date
    FROM aggregated_balances
    ORDER BY date
    ),
    address_dates AS (
    SELECT DISTINCT
        d.date,
        a.address
        FROM date_series d
        CROSS JOIN (SELECT DISTINCT address FROM aggregated_balances) a
    ),
    filled_balances AS (
    SELECT
        ad.date,
        ad.address,
        COALESCE(ab.daily_change, 0) AS daily_change
    FROM address_dates ad
    LEFT JOIN aggregated_balances ab
        ON ad.date = ab.date
        AND ad.address = ab.address
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
    ORDER BY date, address
    ON DUPLICATE KEY UPDATE balance = VALUES(balance);
    """
    db_client = DatabaseClient()
    db_client.execute(query)
    