from src.data_access.client import DatabaseClient
from datetime import datetime
import sys


def create_latest_balances() -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_latest_balancesが開始されました")
    """最新残高テーブルを作成する"""
    try:
        query = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS latest_balances AS
        SELECT date, address, balance
        FROM daily_balances
        WHERE date = CURRENT_DATE
        """
        db_client = DatabaseClient()
        db_client.execute(query)
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_latest_balances中にエラーが発生しました: {e}")
    else:
        print("latest_balancesが作成されました")

def refresh_latest_balances() -> None:
    """日次残高テーブルを更新する"""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} refresh_latest_balancesが開始されました")
        refresh_query = """
        REFRESH MATERIALIZED VIEW latest_balances;
        """
        db_client = DatabaseClient()
        db_client.execute(refresh_query)
        print("latest_balancesを更新しました")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} refresh_latest_balances中にエラーが発生しました: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        create_latest_balances()
        refresh_latest_balances()
    elif len(sys.argv) >= 2:
        if sys.argv[1] == "refresh":
            refresh_latest_balances()
    else:
        print("引数が不正です")
