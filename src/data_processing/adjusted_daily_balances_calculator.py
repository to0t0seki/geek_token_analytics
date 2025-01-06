import sys
from src.data_access.client import DatabaseClient

def create_daily_balances_table() -> None:
    """日次残高テーブルを作成する"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS adjusted_daily_balances (
        date DATE NOT NULL,
        address VARCHAR(42) NOT NULL,
        balance NUMERIC(65,0),
        PRIMARY KEY (date, address)
    )
    """
    db_client = DatabaseClient()
    db_client.execute(create_table_query)

   
    create_index_address = """
    CREATE INDEX IF NOT EXISTS idx_daily_balances_address ON adjusted_daily_balances(address);
    """
    result = db_client.execute(create_index_address)
    if result:
        print("addressインデックスが作成されました")


def calculate_daily_balances() -> None:
    query = """
    INSERT INTO adjusted_daily_balances (date, address, balance)
    WITH adjusted_transactions AS (
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
    ON CONFLICT (date, address) DO UPDATE SET balance = EXCLUDED.balance;
    """
    client = DatabaseClient()
    client.execute(query)
    print("日次残高を計算しました")

def calculate_today_balances() -> None:
    query = """
    INSERT INTO adjusted_daily_balances (date, address, balance)
    WITH today_transactions AS (
    SELECT
        DATE(timestamp + INTERVAL '5 hours') AS date,
        from_address AS address,
        -value AS balance_change
    FROM geek_transactions
    WHERE DATE(timestamp + INTERVAL '5 hours') = DATE(CURRENT_TIMESTAMP + INTERVAL '5 hours')
    AND from_address IS NOT NULL

    UNION ALL

    SELECT
        DATE(timestamp + INTERVAL '5 hours') AS date,
        to_address AS address,
        value AS balance_change
    FROM geek_transactions
    WHERE DATE(timestamp + INTERVAL '5 hours') = DATE(CURRENT_TIMESTAMP + INTERVAL '5 hours')
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
    WHERE date = DATE(CURRENT_TIMESTAMP + INTERVAL '5 hours' - INTERVAL '1 day')
    )
    SELECT 
        DATE(CURRENT_TIMESTAMP + INTERVAL '5 hours') AS date,
        COALESCE(tab.address, pb.address) AS address,
        COALESCE(pb.balance, 0) + COALESCE(tab.daily_change, 0) AS balance
    FROM today_aggregated_balances tab
    FULL OUTER JOIN previous_balances pb ON tab.address = pb.address
    ON CONFLICT (date, address) DO UPDATE 
    SET balance = EXCLUDED.balance;
     
    """
    client = DatabaseClient()
    client.execute(query)
    print("今日の残高を計算しました")

def calculate_yesterday_balances() -> None:
    query = """
    INSERT INTO adjusted_daily_balances (date, address, balance)
    WITH yesterday_transactions AS (
    SELECT
        DATE(timestamp + INTERVAL '5 hours') AS date,
        from_address AS address,
        -value AS balance_change
    FROM geek_transactions
    WHERE DATE(timestamp + INTERVAL '5 hours') = DATE(CURRENT_TIMESTAMP + INTERVAL '5 hours' - INTERVAL '1 day')
    AND from_address IS NOT NULL

    UNION ALL

    SELECT
        DATE(timestamp + INTERVAL '5 hours') AS date,
        to_address AS address,
        value AS balance_change
    FROM geek_transactions
    WHERE DATE(timestamp + INTERVAL '5 hours') = DATE(CURRENT_TIMESTAMP + INTERVAL '5 hours' - INTERVAL '1 day')
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
    WHERE date = DATE(DATE_SUB(DATE_ADD(NOW(), INTERVAL 5 HOUR), INTERVAL 2 DAY))
    )
    SELECT 
        DATE(CURRENT_TIMESTAMP + INTERVAL '5 hours' - INTERVAL '1 day') AS date,
        COALESCE(tab.address, pb.address) AS address,
        COALESCE(pb.balance, 0) + COALESCE(tab.daily_change, 0) AS balance
    FROM yesterday_aggregated_balances tab
    FULL OUTER JOIN previous_balances pb ON tab.address = pb.address
    ON CONFLICT (date, address) DO UPDATE 
    SET balance = EXCLUDED.balance;
    """
    client = DatabaseClient()
    client.execute(query)
    print("昨日の残高を計算しました")


if __name__ == "__main__":
    create_daily_balances_table()
    calculate_daily_balances()

    if len(sys.argv) == 2:
        if sys.argv[1] == "yesterday":  
            calculate_yesterday_balances()
        elif sys.argv[1] == "today":
            calculate_today_balances()
        else:
            print("引数が不正です。")
