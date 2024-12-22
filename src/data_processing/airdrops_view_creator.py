from src.data_access.client import DatabaseClient

def create_airdrops_view() -> None:
    """airdropsビューを作成する"""
    client = DatabaseClient()
    try:
        # 既存のビューが存在する場合は削除
        client.execute("DROP VIEW IF EXISTS airdrops")
        
        # ビューの作成
        create_view = """
        CREATE VIEW airdrops AS
        SELECT * 
        FROM geek_transactions 
        WHERE method IN ('exportAdp', '0xf423abe6')
        """
        client.execute(create_view)
        print("airdropsビューを作成しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    create_airdrops_view()