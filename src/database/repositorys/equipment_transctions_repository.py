from src.database.data_access.database_client import DatabaseClient

def create_equipment_transactions(db_client: DatabaseClient) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS equipment_transactions (
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
    CREATE INDEX IF NOT EXISTS idx_et_timestamp ON equipment_transactions(timestamp);
    """
    db_client.execute(create_index_timestamp_query)

        

    create_index_from_address_query = """
    CREATE INDEX IF NOT EXISTS idx_et_from_address ON equipment_transactions(from_address);
    """
    db_client.execute(create_index_from_address_query)


    
    create_index_to_address_query = """
    CREATE INDEX IF NOT EXISTS idx_et_to_address ON equipment_transactions(to_address);
    """
    db_client.execute(create_index_to_address_query)





def insert_equipment_transactions(db_client: DatabaseClient, transactions: list) -> int:
    insert_transactions_query = """
    INSERT INTO equipment_transactions (block_number, log_index, tx_hash, timestamp, from_address, to_address, token_id, method, type)
    VALUES (%(block_number)s, %(log_index)s, %(tx_hash)s, %(timestamp)s, %(from_address)s, %(to_address)s, %(token_id)s, %(method)s, %(type)s)
    """

    return db_client.executemany(insert_transactions_query, transactions)

def fetch_letest_transaction(db_client: DatabaseClient):
    fetch_letest_transaction_query = """
    SELECT block_number, log_index
    FROM equipment_transactions
    ORDER BY block_number DESC, log_index DESC
    limit 1
    """
    result = db_client.fetch_one(fetch_letest_transaction_query)
    if result is None:
        result = (0, 0)
    return result

def migrate_equipment_transactions_from_nft(db_client: DatabaseClient) -> int:
    insert_transactions_query = """
    INSERT INTO equipment_transactions (
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
        FROM equipment_nft_transactions;
    """

    return db_client.execute(insert_transactions_query)

create_equipment_transactions(DatabaseClient())
migrate_equipment_transactions_from_nft(DatabaseClient())


