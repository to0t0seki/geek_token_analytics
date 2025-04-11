from src.database.data_access.database_client import DatabaseClient

def create_vw_withdrawals(client: DatabaseClient) -> None:
    """withdrawalsビューを作成する"""
  
    # 既存のテーブルまたはビューが存在する場合は削除
    client.execute("DROP VIEW IF EXISTS vw_withdrawals")
    
    # ビューの作成
    create_view = """
    CREATE VIEW vw_withdrawals AS
    SELECT *
    FROM geek_transactions 
    WHERE method IN ('exportToken', '0x23f60921')
    """
    client.execute(create_view)
    print("vw_withdrawalsを作成しました。")
        

if __name__ == "__main__":
    create_vw_withdrawals(DatabaseClient())