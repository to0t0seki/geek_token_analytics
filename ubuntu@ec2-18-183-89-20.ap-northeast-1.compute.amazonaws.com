import sqlite3
import pandas as pd

def test_query(db_file: str):
    conn = sqlite3.connect(db_file)
    query = """
    SELECT t.timestamp, t.tx_hash, td.method
    from transactions t join transfer_details td on t.tx_hash = td.tx_hash
    order by t.timestamp desc
    limit 10
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = test_query('data/processed/geek_transfers.db')

print(df.head(10))
