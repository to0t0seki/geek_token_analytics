from src.database.data_access.database_client import DatabaseClient

def create_doll_transactions(db_client: DatabaseClient) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS doll_transactions (
        block_number INTEGER NOT NULL,
        log_index INTEGER NOT NULL,
        tx_hash VARCHAR(66),
        timestamp TIMESTAMP(6),
        from_address VARCHAR(42),
        to_address VARCHAR(42),
        token_id NUMERIC(10,0),
        method VARCHAR(20),
        type VARCHAR(20),
        PRIMARY KEY (block_number, log_index)

    );
    """
    db_client.execute(create_table_query)

    create_index_timestamp_query = """
    CREATE INDEX IF NOT EXISTS idx_dt_timestamp ON doll_transactions(timestamp);
    """
    db_client.execute(create_index_timestamp_query)
        

    create_index_from_address_query = """
    CREATE INDEX IF NOT EXISTS idx_dt_from_address ON doll_transactions(from_address);
    """
    db_client.execute(create_index_from_address_query)



    
    create_index_to_address_query = """
    CREATE INDEX IF NOT EXISTS idx_dt_to_address ON doll_transactions(to_address);
    """
    db_client.execute(create_index_to_address_query)




def insert_doll_transactions(db_client: DatabaseClient, transactions: list) -> int:
    insert_transactions_query = """
    INSERT INTO doll_transactions (block_number, log_index, tx_hash, timestamp, from_address, to_address, token_id, method, type)
    VALUES (:block_number, :log_index, :tx_hash, :timestamp, :from_address, :to_address, :token_id, :method, :type)
    """

    return db_client.executemany(insert_transactions_query, transactions)

def fetch_letest_transaction(db_client: DatabaseClient):
    fetch_letest_transaction_query = """
    SELECT block_number, log_index
    FROM doll_transactions
    ORDER BY block_number DESC, log_index DESC
    limit 1
    """
    result = db_client.fetch_one(fetch_letest_transaction_query)
    if result is None:
        result = (0, 0)
    return result

def migrate_doll_transactions_from_nft(db_client: DatabaseClient) -> int:
    insert_transactions_query = """
    INSERT INTO doll_transactions (
        block_number,
        log_index,
        tx_hash,
        timestamp,
        from_address,
        to_address,
        token_id,
        method,
        type
    )
    SELECT 
        block_number,
        log_index,
        tx_hash,
        timestamp,
        from_address,
        to_address,
        CAST(token_id AS NUMERIC(10,0)) AS token_id,
        method,
        type
        FROM doll_nft_transactions;
    """

    return db_client.execute(insert_transactions_query)


# create_doll_transactions(DatabaseClient())
# migrate_doll_transactions_from_nft(DatabaseClient())
