from src.data_access.client import DatabaseClient

def create_deposits_view() -> None:
    """depositsビューを作成する"""
    client = DatabaseClient()
    try:
        # 既存のテーブルまたはビューが存在する場合は削除
        client.execute("DROP VIEW IF EXISTS deposits")
        
        # ビューの作成
        create_view = """
        CREATE VIEW deposits AS
        SELECT *
        FROM geek_transactions 
        WHERE method IN ('xgeekToGeek', '0x1a682064')
        """
        client.execute_ddl(create_view)
        print("depositsビューを作成しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    create_deposits_view()