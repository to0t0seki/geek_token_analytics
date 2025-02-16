from src.database.data_access.database_client import DatabaseClient

def create_gw_to_gw_geek_transactions_view() -> None:
    client = DatabaseClient()
    client.execute("DROP VIEW IF EXISTS gw_to_gw_geek_transactions")
    
    create_view = """
    CREATE VIEW gw_to_gw_geek_transactions AS
    SELECT gt.*
    FROM geek_transactions gt
    INNER JOIN airdrop_recipients ar ON gt.from_address = ar.address
    INNER JOIN airdrop_recipients ar2 ON gt.to_address = ar2.address;
    """

    client.execute(create_view)
    print("gw_to_gw_geek_transactionsビューを作成しました。")
        


if __name__ == "__main__":
    create_gw_to_gw_geek_transactions_view()

