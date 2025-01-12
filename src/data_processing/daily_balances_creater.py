from src.data_access.client import DatabaseClient
from datetime import datetime
def create_daily_balances_table() -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_daily_balances_tableが開始されました")
    """日次残高テーブルを作成する"""
    create_table_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_balances AS

    WITH date_series AS (
    SELECT DISTINCT date
    FROM daily_changes
    ORDER BY date
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
        COALESCE(dc.change, 0) AS daily_change
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
    db_client = DatabaseClient()
    result = db_client.execute(create_table_query)
    if result > 0:
        print("daily_balancesが作成されました")

def refresh_daily_balances() -> None:
    """日次残高テーブルを更新する"""
    refresh_query = """
    REFRESH MATERIALIZED VIEW daily_balances;
    """
    db_client = DatabaseClient()
    db_client.execute(refresh_query)
    print("日次残高テーブルを更新しました")

