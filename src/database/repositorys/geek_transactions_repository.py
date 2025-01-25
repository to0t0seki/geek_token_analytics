from src.database.data_access.database_client import DatabaseClient

def create_geek_transactions(db_client: DatabaseClient) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS geek_transactions (
        block_number INTEGER NOT NULL,
        log_index INTEGER NOT NULL,
        tx_hash VARCHAR(66),
        timestamp TIMESTAMP(6),
        from_address VARCHAR(42),
        to_address VARCHAR(42),
        value NUMERIC(65,0),
        method VARCHAR(20),
        type VARCHAR(20),
        PRIMARY KEY (block_number, log_index)
    );
    """
    db_client.execute(create_table_query)

    create_index_timestamp_query = """
    CREATE INDEX IF NOT EXISTS idx_gt_timestamp ON geek_transactions(timestamp);
    """
    db_client.execute(create_index_timestamp_query)
        
    create_index_from_address_query = """
    CREATE INDEX IF NOT EXISTS idx_gt_from_address ON geek_transactions(from_address);
    """
    db_client.execute(create_index_from_address_query)

    
    create_index_to_address_query = """
    CREATE INDEX IF NOT EXISTS idx_gt_to_address ON geek_transactions(to_address);
    """
    db_client.execute(create_index_to_address_query)


    create_trigger_query = """
        DROP TRIGGER IF EXISTS trg_insert_geek_transactions ON geek_transactions;


        CREATE OR REPLACE FUNCTION insert_daily_changes() RETURNS TRIGGER AS $$
        BEGIN
            BEGIN   
                RAISE NOTICE 'トリガーが発火しました: block_number=%, log_index=%', 
                NEW.block_number, 
                NEW.log_index;
           
                -- from_addressの処理（マイナス値）
                INSERT INTO daily_changes (date, address, change)
                VALUES (
                    (NEW.timestamp + interval '5 hours')::date,  -- timestampを+5時間してdate型に変換
                    NEW.from_address,
                    -NEW.value  -- マイナス値として設定
                )
                ON CONFLICT (date, address) 
                DO UPDATE SET change = daily_changes.change + EXCLUDED.change;

                -- to_addressの処理（プラス値）
                INSERT INTO daily_changes (date, address, change)
                VALUES (
                    (NEW.timestamp + interval '5 hours')::date,  -- timestampを+5時間してdate型に変換
                    NEW.to_address,
                    NEW.value  -- プラス値として設定
                )
                ON CONFLICT (date, address) 
                DO UPDATE SET change = daily_changes.change + EXCLUDED.change;

                RETURN NEW;

            EXCEPTION WHEN OTHERS THEN
                RAISE EXCEPTION 'トリガー内でエラーが発生しました: block_number=%, log_index=%, error: %', 
                    NEW.block_number, 
                    NEW.log_index,
                    SQLERRM;
            END;
        END;
        $$
        LANGUAGE plpgsql;

        CREATE TRIGGER trg_insert_geek_transactions
        AFTER INSERT ON geek_transactions
        FOR EACH ROW
        EXECUTE FUNCTION insert_daily_changes();
    """
    db_client.execute(create_trigger_query)

def insert_geek_transactions(db_client: DatabaseClient, transactions: list) -> int:
    insert_transactions_query = """
    INSERT INTO geek_transactions (block_number, log_index, tx_hash, timestamp, from_address, to_address, value, method, type)
    VALUES (%(block_number)s, %(log_index)s, %(tx_hash)s, %(timestamp)s, %(from_address)s, %(to_address)s, %(value)s, %(method)s, %(type)s)
    """
    return db_client.executemany(insert_transactions_query, transactions)

def fetch_letest_transaction(db_client: DatabaseClient):
    fetch_letest_transaction_query = """
    SELECT block_number, log_index
    FROM geek_transactions
    ORDER BY block_number DESC, log_index DESC
    limit 1
    """
    return db_client.fetch_one(fetch_letest_transaction_query)