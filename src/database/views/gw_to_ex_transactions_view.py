from src.database.data_access.database_client import DatabaseClient

def create_gw_to_ex_transactions_view() -> None:
    client = DatabaseClient()
    client.execute("DROP VIEW IF EXISTS gw_to_ex_transactions")
    
    create_view = """
    CREATE VIEW gw_to_ex_transactions AS
    SELECT gt.*
    FROM geek_transactions gt
    INNER JOIN airdrop_recipients ar ON gt.from_address = ar.address
    INNER JOIN exchange_wallets ew ON gt.to_address = ew.address;
    """

    client.execute(create_view)
    print("gw_to_ex_transactionsビューを作成しました。")
        


if __name__ == "__main__":
    create_gw_to_ex_transactions_view()