from src.data_access.client import DatabaseClient
from datetime import datetime

def create_daily_changes_table() -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_daily_changes_tableが開始されました")
    try:
        client = DatabaseClient()
        query = """
        CREATE TABLE IF NOT EXISTS daily_changes (
            date DATE NOT NULL,
            address VARCHAR(42) NOT NULL,
            change NUMERIC(65,0),
            PRIMARY KEY (date, address)
        );
        """
        result = client.execute(query)
        if result > 0:
            print("daily_changesテーブルが作成されました")

        query = """
        CREATE INDEX IF NOT EXISTS idx_daily_changes_address ON daily_changes(address);
        """
        result = client.execute(query)
        if result > 0:
            print("addressインデックスが作成されました")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_daily_changes_table中にエラーが発生しました: {e}")

def insert_daily_changes() -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} insert_daily_changesが開始されました")
    try:
        client = DatabaseClient()
        query = """
        INSERT INTO daily_changes (date, address, change)
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
        )
        SELECT
            date,
            address,
            SUM(balance_change) AS daily_change
        FROM transactions
        GROUP BY date, address
        ON CONFLICT (date, address) 
        DO UPDATE SET change = EXCLUDED.change;
        """
        result = client.execute(query)
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} insert_daily_changes中にエラーが発生しました: {e}")
    else:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} insert_daily_changesが正常に実行されました")
        print(result)

if __name__ == "__main__":
    create_daily_changes_table()
    insert_daily_changes()

