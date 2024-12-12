from src.data_access.client import DatabaseClient

def create_daily_balances_table() -> None:
    """日次残高テーブルを作成する"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS adjusted_daily_balances (
        date TEXT,
        address TEXT,
        balance REAL,
        PRIMARY KEY (date, address)
    )
    """
    client = DatabaseClient()
    client.execute_ddl(create_table_query)

    create_index_query = """
    CREATE INDEX IF NOT EXISTS idx_daily_balances_address 
    ON adjusted_daily_balances(address);
    """
    client.execute_ddl(create_index_query)


def calculate_daily_balances() -> None:
    query = """
    WITH adjusted_transactions AS (
    SELECT
        DATE(datetime(timestamp, '+5 hours')) AS date,
        from_address AS address,
        -CAST(value AS REAL) / 1000000000000000000.0 AS balance_change
    FROM geek_transactions
    WHERE from_address IS NOT NULL

    UNION ALL

    SELECT
        DATE(datetime(timestamp, '+5 hours')) AS date,
        to_address AS address,
        CAST(value AS REAL) / 1000000000000000000.0 AS balance_change
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
INSERT OR REPLACE INTO adjusted_daily_balances (date, address, balance)
SELECT
    date,
    address,
    SUM(daily_change) OVER (
        PARTITION BY address
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS balance
FROM filled_balances
ORDER BY date, address;
    """
    client = DatabaseClient()
    client.execute(query)

def calculate_todays_balances() -> None:
    query = """
    WITH today_transactions AS (
    SELECT
        DATE(datetime(timestamp, '+5 hours')) AS date,
        from_address AS address,
        -CAST(value AS REAL) / 1000000000000000000.0 AS balance_change
    FROM geek_transactions
    WHERE DATE(datetime(timestamp, '+5 hours')) = DATE(DATETIME('now', '+5 hours'))
    AND from_address IS NOT NULL

    UNION ALL

    SELECT
        DATE(datetime(timestamp, '+5 hours')) AS date,
        to_address AS address,
        CAST(value AS REAL) / 1000000000000000000.0 AS balance_change
    FROM geek_transactions
    WHERE DATE(datetime(timestamp, '+5 hours')) = DATE(DATETIME('now', '+5 hours'))
    AND to_address IS NOT NULL
    ),
    today_aggregated_balances AS (
    SELECT
        date,
        address,
        SUM(balance_change) AS daily_change
    FROM today_transactions
    GROUP BY date, address
    ),
    previous_balances AS (
    SELECT address, balance
    FROM adjusted_daily_balances
    WHERE date = DATE(DATETIME('now', '+5 hours', '-1 day'))
    )
    INSERT OR REPLACE INTO adjusted_daily_balances (date, address, balance)
    SELECT 
        DATE(DATETIME('now', '+5 hours')) as date,
        COALESCE(tab.address, pb.address) as address,
        COALESCE(pb.balance, 0) + COALESCE(tab.daily_change, 0) as balance
    FROM today_aggregated_balances tab
    FULL OUTER JOIN previous_balances pb ON tab.address = pb.address
    WHERE COALESCE(tab.address, pb.address) IS NOT NULL;
    """
    client = DatabaseClient()
    client.execute(query)

def calculate_yesterday_balances() -> None:
    query = """
    WITH yesterday_transactions AS (
    SELECT
        DATE(datetime(timestamp, '+5 hours')) AS date,
        from_address AS address,
        -CAST(value AS REAL) / 1000000000000000000.0 AS balance_change
    FROM geek_transactions
    WHERE DATE(datetime(timestamp, '+5 hours')) = DATE(DATETIME('now', '+5 hours', '-1 day'))
    AND from_address IS NOT NULL

    UNION ALL

    SELECT
        DATE(datetime(timestamp, '+5 hours')) AS date,
        to_address AS address,
        CAST(value AS REAL) / 1000000000000000000.0 AS balance_change
    FROM geek_transactions
    WHERE DATE(datetime(timestamp, '+5 hours')) = DATE(DATETIME('now', '+5 hours', '-1 day'))
    AND to_address IS NOT NULL
    ),
    yesterday_aggregated_balances AS (
    SELECT
        date,
        address,
        SUM(balance_change) AS daily_change
    FROM yesterday_transactions
    GROUP BY date, address
    ),
    previous_balances AS (
    SELECT address, balance
    FROM adjusted_daily_balances
    WHERE date = DATE(DATETIME('now', '+5 hours', '-2 day'))
    )
    INSERT OR REPLACE INTO adjusted_daily_balances (date, address, balance)
    SELECT 
        DATE(DATETIME('now', '+5 hours', '-1 day')) as date,
        COALESCE(tab.address, pb.address) as address,
        COALESCE(pb.balance, 0) + COALESCE(tab.daily_change, 0) as balance
    FROM yesterday_aggregated_balances tab
    FULL OUTER JOIN previous_balances pb ON tab.address = pb.address
    WHERE COALESCE(tab.address, pb.address) IS NOT NULL;
    """
    client = DatabaseClient()
    client.execute(query)


def test():
    query = """
    SELECT datetime('now', '+5 hours', '-1 day')
    """
    client = DatabaseClient()
    result = client.fetch_one(query)
    print(result)

if __name__ == "__main__":
    # create_daily_balances_table()
    # calculate_daily_balances()
    # calculate_yesterday_balances()
    calculate_todays_balances()
    # test()
