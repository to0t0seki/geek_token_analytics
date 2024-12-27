from src.data_access.client import DatabaseClient

def create_player_balance_view() -> None:
    """player_balanceビューを作成する"""
    client = DatabaseClient()
    query = """
    CREATE VIEW player_balance AS
    WITH airdrop_addresses AS (
        SELECT DISTINCT to_address as address
        FROM airdrops
    )
    
    SELECT db.address, db.date, db.balance / 1000000000000000000.0 as balance
    FROM adjusted_daily_balances db
    INNER JOIN airdrop_addresses aa ON db.address = aa.address
    """
    client.execute(query)

if __name__ == "__main__":
    create_player_balance_view()