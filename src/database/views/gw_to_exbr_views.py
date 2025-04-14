from src.database.data_access.database_client import DatabaseClient


def create_ge(client: DatabaseClient) -> None:
    """GeekWalletからExchange,Bridgeへのデータを取得するビューを作成する"""
    # 既存のビューが存在する場合は削除
    client.execute("DROP VIEW IF EXISTS ge")
        
    # ビューの作成
    create_view = """
    CREATE VIEW ge AS
    SELECT gt.timestamp + interval '9 hours' as timestamp,
    gt.from_address,
        CASE 
            WHEN a.main_type = 'exchange' THEN a.sub_type
            ELSE 'bridge'
        END AS to_name,
    round(gt.value/1e24,2) as value
    FROM geek_transactions gt
    left JOIN addresses a ON gt.to_address = a.address
    where (gt.to_address = '0x0000000000000000000000000000000000000000' or
    a.main_type = 'exchange')
    and a.sub_type not in ('bitget_pool','gate_pool')
    
    """
    client.execute(create_view)
    print("geを作成しました。")
        

if __name__ == "__main__":
    client = DatabaseClient()
    create_ge(client)