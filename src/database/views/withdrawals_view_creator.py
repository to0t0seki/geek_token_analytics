from src.database.data_access.database_client import DatabaseClient

def create_withdrawals_view() -> None:
    """withdrawalsビューを作成する"""
    client = DatabaseClient()
    try:
        # 既存のテーブルまたはビューが存在する場合は削除
        client.execute("DROP VIEW IF EXISTS withdrawals")
        
        # ビューの作成
        create_view = """
        CREATE VIEW withdrawals AS
        SELECT *
        FROM geek_transactions 
        WHERE method IN ('exportToken', '0x23f60921')
        """
        client.execute(create_view)
        print("withdrawalsビューを作成しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    create_withdrawals_view()