import sqlite3
import pandas as pd

def test_query(db_file: str):
    conn = sqlite3.connect(db_file)
    query = """
    SELECT * FROM transactions t join transfer_details td on t.tx_hash = td.tx_hash 
    WHERE td.from_address = '0x811987119d475b542fc67805aa716c533FD7Ec77' or
        td.to_address = '0x811987119d475b542fc67805aa716c533FD7Ec77'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = test_query('data/processed/geek_transfers.db')
reserve = df[df['to_address'] == '0x811987119d475b542fc67805aa716c533FD7Ec77']['value'].sum()
submit = df[df['from_address'] == '0x811987119d475b542fc67805aa716c533FD7Ec77']['value'].sum()
print(reserve, submit)
