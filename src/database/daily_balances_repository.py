from src.data_access.database_client import DatabaseClient


def create_daily_balances(db_client: DatabaseClient) -> None:
    create_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_balances AS
    WITH transactions AS (
    SELECT
        DATE(timestamp + INTERVAL '5 hours') AS date,
        from_address AS address,
        -value AS balance_change
    FROM geek_transactions
    WHERE from_address IS NOT NULL

    UNION ALL

    SELECT
        DATE(timestamp + INTERVAL '5 hours') AS date,
        to_address AS address,
        value AS balance_change
    FROM geek_transactions
    WHERE to_address IS NOT NULL
    ),

    daily_changes as (
    SELECT
        date,
        address,
        SUM(balance_change) AS daily_change
    FROM transactions
    GROUP BY date, address),

    date_series AS (
    SELECT DISTINCT date
    from daily_changes
    ),

    address_dates AS (
    SELECT DISTINCT
        d.date,
        a.address
        FROM date_series d
        CROSS JOIN (SELECT DISTINCT address FROM daily_changes) a
    ),

    filled_balances AS (
    SELECT
        ad.date,
        ad.address,
        COALESCE(dc.daily_change, 0) AS daily_change
    FROM address_dates ad
    LEFT JOIN daily_changes dc
        ON ad.date = dc.date
        AND ad.address = dc.address
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
    """
    db_client.execute(create_query)

    create_index_query = """
    CREATE UNIQUE INDEX idx_daily_balances_address_date 
    ON daily_balances(address, date);
    """
    db_client.execute(create_index_query)

def refresh_daily_balances(db_client: DatabaseClient) -> None:
    refresh_query = """
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_balances;
    """
    db_client.execute(refresh_query) 
