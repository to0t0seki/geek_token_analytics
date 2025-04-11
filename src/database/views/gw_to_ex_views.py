from src.database.data_access.database_client import DatabaseClient


def create_vw_gw_to_ex(client: DatabaseClient) -> None:
    """GeekWalletからExchangeへのデータを取得するビューを作成する"""
    # 既存のビューが存在する場合は削除
    client.execute("DROP VIEW IF EXISTS vw_gw_to_ex")
        
    # ビューの作成
    create_view = """
    CREATE VIEW vw_gw_to_ex AS
    SELECT * 
    FROM geek_transactions  gt
    join exchange_addresses ea on gt.to_address = ea.address
    """
    client.execute(create_view)
    print("vw_gw_to_exを作成しました。")
        

if __name__ == "__main__":
    client = DatabaseClient()
    create_vw_gw_to_ex(client)