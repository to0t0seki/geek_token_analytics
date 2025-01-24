from src.data_access.database_client import DatabaseClient

def create_ohlcv_1h(db_client: DatabaseClient) -> None:
    create_ohlcv_1h_table = """
    CREATE TABLE IF NOT EXISTS ohlcv_1h (
        timestamp timestamp PRIMARY KEY,
        open NUMERIC(20,8),
        high NUMERIC(20,8),
        low NUMERIC(20,8),
        close NUMERIC(20,8),
        volume NUMERIC(20,8),
        usdt_volume NUMERIC(20,8)
    );
    """
    db_client.execute(create_ohlcv_1h_table)

    create_index_timestamp = """
    CREATE INDEX IF NOT EXISTS idx_ohlcv_1h_timestamp ON ohlcv_1h(timestamp);
    """
    db_client.execute(create_index_timestamp)

def insert_ohlcv_1h_db(db_client: DatabaseClient, params: dict) -> int:
    insert_ohlcv_1h_query = """
    INSERT INTO ohlcv_1h (timestamp, open, high, low, close, volume, usdt_volume) 
    VALUES (timestamp 'epoch' + %(timestamp)s * interval '1 second', %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(usdt_volume)s)
    ON CONFLICT (timestamp) DO NOTHING
    """
 
    row_count = db_client.executemany(insert_ohlcv_1h_query, params)
    return row_count
