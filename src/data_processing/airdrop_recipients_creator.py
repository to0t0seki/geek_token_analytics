from src.data_access.client import DatabaseClient
from datetime import datetime
import sys


def create_airdrop_recipients() -> None:
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_airdrop_recipientsが開始されました")
    """エアドロップを一度でも受け取ったことがあるアドレスのリストを作成する"""
    try:
        query = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS airdrop_recipients AS
        SELECT DISTINCT to_address as address
        FROM airdrops
        """
        db_client = DatabaseClient()
        db_client.execute(query)
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} create_airdrop_recipients中にエラーが発生しました: {e}")
    else:
        print("airdrop_recipientsが作成されました")

def refresh_airdrop_recipients() -> None:
    """日次残高テーブルを更新する"""
    try:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} refresh_airdrop_recipientsが開始されました")
        refresh_query = """
        REFRESH MATERIALIZED VIEW airdrop_recipients;
        """
        db_client = DatabaseClient()
        db_client.execute(refresh_query)
        print("airdrop_recipientsを更新しました")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} refresh_airdrop_recipients中にエラーが発生しました: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        create_airdrop_recipients()
        refresh_airdrop_recipients()
    elif len(sys.argv) >= 2:
        if sys.argv[1] == "refresh":
            refresh_airdrop_recipients()
    else:
        print("引数が不正です")
