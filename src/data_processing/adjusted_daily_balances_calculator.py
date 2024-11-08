import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Tuple, List

def create_daily_balances_table(conn: sqlite3.Connection) -> None:
    """日次残高テーブルを作成する"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS adjusted_daily_balances (
        date TEXT,
        address TEXT,
        balance REAL,
        PRIMARY KEY (date, address)
    )
    """
    conn.execute(create_table_query)
    conn.commit()

def get_all_transactions(conn: sqlite3.Connection) -> list:
    """全てのトランザクションを日付順に取得する"""
    query = """
    SELECT t.timestamp, td.from_address, td.to_address, td.value
    FROM transactions t
    JOIN transfer_details td ON t.tx_hash = td.tx_hash
    ORDER BY t.timestamp
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def update_balances(balances: Dict[str, float], from_addr: str, to_addr: str, value: float) -> None:
    """残高を更新する"""
    balances[from_addr] = balances.get(from_addr, 0) - value
    balances[to_addr] = balances.get(to_addr, 0) + value

def insert_daily_balances(conn: sqlite3.Connection, date: str, balances: Dict[str, float]) -> None:
    """日次残高をデータベースに挿入する"""
    insert_query = """
    INSERT OR REPLACE INTO adjusted_daily_balances (date, address, balance)
    VALUES (?, ?, ?)
    """
    cursor = conn.cursor()
    for address, balance in balances.items():
        cursor.execute(insert_query, (date, address, balance))
    conn.commit()

def get_adjusted_date(timestamp: str) -> datetime.date:
    """タイムスタンプに5時間を加算して日付を取得する"""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    adjusted_dt = dt + timedelta(hours=5)
    return adjusted_dt.date()

def calculate_daily_balances(db_file: str) -> None:
    """日次残高を計算してデータベースに保存する"""
    conn = sqlite3.connect(db_file)
    create_daily_balances_table(conn)
    
    transactions = get_all_transactions(conn)
    balances = {}
    current_date = None
    
    for timestamp, from_addr, to_addr, value in transactions:
        # タイムスタンプに5時間を加算して日付を判定
        transaction_date = get_adjusted_date(timestamp)
        
        if current_date is None:
            current_date = transaction_date
        
        while current_date < transaction_date:
            insert_daily_balances(conn, str(current_date), balances)
            current_date += timedelta(days=1)
        
        update_balances(balances, from_addr, to_addr, value)
    
    # 最後の日の残高を挿入
    if current_date:
        insert_daily_balances(conn, str(current_date), balances)
    
    conn.close()
    print("日次残高の計算が完了しました。")

def get_daily_balances_for_address(db_file: str, address: str) -> List[Tuple[str, float]]:
    """指定されたアドレスの日次残高を取得する"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    query = """
    SELECT date, balance
    FROM adjusted_daily_balances
    WHERE address = ?
    ORDER BY date
    """
    
    cursor.execute(query, (address,))
    results = cursor.fetchall()
    
    conn.close()
    return results

def print_daily_balances(balances: List[Tuple[str, float]]):
    """日次残高を表示する"""
    print("日付\t\t残高")
    print("-" * 30)
    for date, balance in balances:
        print(f"{date}\t{balance:.6f}")

def run_update():
    db_file = "data/processed/geek_transfers.db"
    calculate_daily_balances(db_file)
    print("日次残高の更新が完了しました。")

if __name__ == "__main__":
    run_update()