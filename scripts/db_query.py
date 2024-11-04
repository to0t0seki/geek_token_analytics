import json
from decimal import Decimal
from collections import defaultdict
import pandas as pd
from datetime import timedelta,datetime
import sqlite3


conn = sqlite3.connect('data/processed/geek_transfers.db')
cursor = conn.cursor()



# print(result[0])
def record_query():
    record_query = "SELECT count(*) FROM xgeek_to_geek"
    cursor.execute(record_query)
    result = cursor.fetchone()
    print(result[0])

def table_query():
    table_query = "SELECT name FROM sqlite_master WHERE type='table'"
    cursor.execute(table_query)
    result = cursor.fetchall()
    for table in result:
        print(f"{result.index(table)}: {table[0]}")
    return result

def drop_table():
    drop_query =  "DROP TABLE IF EXISTS airdrops"
    cursor.execute(drop_query)

def describe_table(table_name):
    describe_query = f"PRAGMA table_info({table_name})"
    cursor.execute(describe_query)
    result = cursor.fetchall()
    for column in result:
        print(column)

def check_views(db_file: str):
    """データベース内の全てのビューを表示"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type = 'view'
    """)
    
    views = cursor.fetchall()
    for view in views:
        print(view[0])
    conn.close()

# drop_table()
# table_query()
# record_query()
# describe_table()

def get_table_info():
    tables = table_query()
    talbe_num = input("Press Enter to continue...")
    describe_table(tables[int(talbe_num)][0])

def test(db_file: str):
    latest_record_query = """
        SELECT *
        FROM airdrops
        ORDER BY timestamp DESC
        LIMIT 1
        """
    cursor.execute(latest_record_query)
    
    result = cursor.fetchone()
    print(result)
    conn.close()

# check_views('data/processed/geek_transfers.db')
get_table_info()
# test('data/processed/geek_transfers.db')




