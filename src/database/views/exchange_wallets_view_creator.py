from src.database.data_access.database_client import DatabaseClient

def create_exchange_wallets_view() -> None:
    """exchange_walletsビューを作成する"""
    client = DatabaseClient()
    try:


        # 既存のビューが存在する場合は削除
        client.execute("DROP VIEW IF EXISTS bitget_wallets")
        

        # ビューの作成
        create_view = """
        CREATE VIEW exchange_wallets AS
        with exchange_wallets as (
        SELECT distinct from_address as address,
        CASE 
            WHEN to_address = '0x0D0707963952f2fBA59dD06f2b425ace40b492Fe' THEN 'gate.io'
            WHEN to_address = '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23' THEN 'bitget'
        END as exchange
        FROM geek_transactions 
        WHERE to_address IN ('0x0D0707963952f2fBA59dD06f2b425ace40b492Fe', '0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23')
        )
        SELECT ew.address, ew.exchange, gt.amount
        FROM geek_transactions as gt left join exchange_wallets as ew on gt.to_address = ew.address
        """
        client.execute(create_view)






        print("exchange_walletsビューを作成しました。")
        


    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    create_exchange_wallets_view()

    