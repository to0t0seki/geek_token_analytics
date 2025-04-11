from src.database.data_access.database_client import DatabaseClient

def create_vw_all_transactions(client: DatabaseClient) -> None:
    """all_transactionsビューを作成する"""
   
    client.execute("DROP VIEW IF EXISTS vw_all_transactions")
    
    # ビューの作成
    create_view = """
    CREATE VIEW vw_all_transactions AS
    SELECT 
        block_number,
        log_index,
        tx_hash,
        timestamp,
        from_address,
        to_address,
        value AS unified_amount,
        method,
        type,
        'geek' AS source
    FROM geek_transactions
    UNION ALL
    SELECT 
        block_number,
        log_index,
        tx_hash,
        timestamp,
        from_address,
        to_address,
        token_id AS unified_amount,
        method,
        type,
        'doll' AS source
    FROM doll_transactions
    UNION ALL
    SELECT 
        block_number,
        log_index,
        tx_hash,
        timestamp,
        from_address,
        to_address,
        token_id AS unified_amount,
        method,
        type,
        'equipment' AS source
    FROM equipment_transactions;
    """
    client.execute(create_view)
    print("vw_all_transactionsを作成しました。")

if __name__ == "__main__":
    create_vw_all_transactions(DatabaseClient())