from src.database.data_access.database_client import DatabaseClient

def create_vw_all_transactions() -> None:
    """all_transactionsビューを作成する"""
    client = DatabaseClient()
    try:
        # 既存のビューが存在する場合は削除
        client.execute("DROP VIEW IF EXISTS all_transactions")
        
        # ビューの作成
        create_view = """
        CREATE VIEW all_transactions AS
        SELECT * 
        FROM geek_transactions 
        UNION ALL
        SELECT *
        
        """
        client.execute(create_view)
        print("all_transactionsビューを作成しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    create_airdrops_view()