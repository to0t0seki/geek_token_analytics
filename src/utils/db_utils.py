import sqlite3
from typing import List, Dict, Any, Tuple

def get_db_connection(db_file: str) -> sqlite3.Connection:
    """データベース接続を取得する"""
    return sqlite3.connect(db_file)

def execute_query(conn: sqlite3.Connection, query: str) -> None:
    """SQLクエリを実行する"""
    cursor = conn.cursor()
    # 複数のSQL文を分割して実行
    for statement in query.split(';'):
        if statement.strip():  # 空の文を除外
            cursor.execute(statement)
    conn.commit()

def insert_many(conn: sqlite3.Connection, table: str, data: List[Dict[str, Any]]) -> None:
    """複数のレコードを一度に挿入する"""
    cursor = conn.cursor()
    columns = ', '.join(data[0].keys())
    placeholders = ', '.join(['?' for _ in data[0]])
    query = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.executemany(query, [tuple(item.values()) for item in data])
    conn.commit()

def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """指定されたテーブルが存在するかチェックする"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None


def fetch_query(conn: sqlite3.Connection, query: str, params: Tuple = ()) -> List[Tuple]:
    """SQLクエリを実行し、結果を取得する"""
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()

def list_tables(conn: sqlite3.Connection) -> List[str]:
    """データベース内のすべてのテーブルを一覧表示する"""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor = conn.cursor()
    cursor.execute(query)
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def describe_table(conn: sqlite3.Connection, table_name: str) -> List[Tuple[str, str]]:
    """指定されたテーブルの構造を表示する"""
    query = f"PRAGMA table_info({table_name});"
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def run_all_db_updates():
    from src.data_collection.transfer_data_collector_db import run_update as transfer_data_collector_update
    from src.data_processing.daily_balances_calculator import run_update as daily_balances_calculator_update

    requests_count, new_records_count = transfer_data_collector_update()
    daily_balances_calculator_update()  
    return requests_count, new_records_count

if __name__ == "__main__":
    requests_count, new_records_count = run_all_db_updates()
    print(f"処理完了: {requests_count} 回のリクエスト, {new_records_count} 件の新規トランザクション")

    

