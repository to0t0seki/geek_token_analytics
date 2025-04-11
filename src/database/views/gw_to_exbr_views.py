from src.database.data_access.database_client import DatabaseClient


def create_vw_gw_to_exbr(client: DatabaseClient) -> None:
    """GeekWalletからExchange,Bridgeへのデータを取得するビューを作成する"""
    # 既存のビューが存在する場合は削除
    client.execute("DROP VIEW IF EXISTS vw_gw_to_exbr")
        
    # ビューの作成
    create_view = """
    CREATE VIEW vw_gw_to_exbr AS
    SELECT gt.*,
        CASE 
            WHEN ea.address IS NOT NULL THEN ea.exchange
            ELSE 'bridge'
        END AS to_name
    FROM geek_transactions gt
    left JOIN exchange_addresses ea ON gt.to_address = ea.address
    where gt.to_address = '0x0000000000000000000000000000000000000000' or
    ea.address is not null
    """
    client.execute(create_view)
    print("vw_gw_to_exbrを作成しました。")
        

if __name__ == "__main__":
    client = DatabaseClient()
    create_vw_gw_to_exbr(client)