from src.database.data_access.database_client import DatabaseClient

def create_vw_deposits(client: DatabaseClient) -> None:
    # 既存のテーブルまたはビューが存在する場合は削除
    client.execute("DROP VIEW IF EXISTS vw_deposits")
    
    # ビューの作成
    create_view = """
    CREATE VIEW vw_deposits AS
    SELECT *
    FROM geek_transactions 
    WHERE method IN ('xgeekToGeek', '0x1a682064')
    """
    client.execute(create_view)
    print("vw_depositsを作成しました。")

if __name__ == "__main__":
    client = DatabaseClient()
    create_vw_deposits(client)