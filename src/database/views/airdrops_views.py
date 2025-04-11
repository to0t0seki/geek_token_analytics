from src.database.data_access.database_client import DatabaseClient

def create_vw_airdrops(client: DatabaseClient) -> None:
    """airdropsビューを作成する"""
    # 既存のビューが存在する場合は削除
    client.execute("DROP VIEW IF EXISTS vw_airdrops")
        
    # ビューの作成
    create_view = """
    CREATE VIEW vw_airdrops AS
    SELECT * 
    FROM geek_transactions 
    WHERE method IN ('exportAdp', '0xf423abe6')
    """
    client.execute(create_view)
    print("vw_airdropsを作成しました。")
        

if __name__ == "__main__":
    client = DatabaseClient()
    create_vw_airdrops(client)