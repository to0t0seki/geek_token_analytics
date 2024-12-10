import requests
import time
import sqlite3
from decimal import Decimal
from src.utils.db_utils import get_db_connection, execute_query
from typing import Dict, Any
from src.data_processing import adjusted_daily_balances_calculator_old

def create_normalized_tables(conn: sqlite3.Connection) -> None:
    """正規化されたテーブルを作成する"""
    create_transactions_table = """
    CREATE TABLE IF NOT EXISTS transactions (
        tx_hash TEXT PRIMARY KEY,
        timestamp TEXT
    )
    """
    execute_query(conn, create_transactions_table)

    create_index_query = """
    CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
    """
    execute_query(conn, create_index_query) 

    create_transfer_details_table = """
    CREATE TABLE IF NOT EXISTS transfer_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tx_hash TEXT,
        from_address TEXT,
        to_address TEXT,
        value REAL,
        method TEXT,
        log_index INTEGER,
        FOREIGN KEY (tx_hash) REFERENCES transactions(tx_hash)
    )
    """
    execute_query(conn, create_transfer_details_table)

    create_index_query = """
    CREATE INDEX IF NOT EXISTS idx_transfer_details_tx_hash ON transfer_details(tx_hash);
    """
    execute_query(conn, create_index_query)

    create_unique_index_query = """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_transfer_details_unique 
    ON transfer_details(tx_hash, from_address, to_address, value, method, log_index);
    """
    execute_query(conn, create_unique_index_query)



def insert_normalized_data(conn: sqlite3.Connection, data: Dict[str, Any]) -> None:
    """正規化されたデータを挿入する"""
    insert_transaction_query = """
    INSERT OR IGNORE INTO transactions (tx_hash, timestamp) VALUES (?, ?)
    """
    insert_transfer_detail_query = """
    INSERT OR IGNORE INTO transfer_details (tx_hash, from_address, to_address, value, method, log_index)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    cursor = conn.cursor()
    
    cursor.execute(insert_transaction_query, (data['tx_hash'], data['timestamp']))
    
    cursor.execute(insert_transfer_detail_query, (
        data['tx_hash'],
        data['from_address'],
        data['to_address'],
        data['value'],
        data['method'],
        data['log_index']
    ))

    inserted = cursor.rowcount > 0
    conn.commit()
    return inserted

def get_latest_transaction(conn: sqlite3.Connection) -> tuple:
    """データベースから最新のトランザクション情報を取得する"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tx_hash, timestamp 
        FROM transactions 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    result = cursor.fetchone()
    return result if result else (None, None)

def update_db_from_api(db_file: str):
    base_url = "https://explorer.geekout-pte.com/api/v2/tokens/0x3741FcB5792673eF220cCc0b95B5B8C38c5f2723/transfers"
    params = {}
    requests_count = 0
    new_records_count = 0

    conn = get_db_connection(db_file)
    create_normalized_tables(conn)
    latest_tx_hash, latest_timestamp = get_latest_transaction(conn)

    try:
        while True:
            response = requests.get(base_url, params=params, timeout=10)
            data = response.json()
            requests_count += 1
            print(f"APIリクエスト {requests_count} 回目: {len(data['items'])} 件のデータを取得")

            new_transactions = []
            for item in data['items']:
                if latest_timestamp and item['timestamp'] <= latest_timestamp:
                    print(f"既存のデータに到達しました: {item['timestamp']}")
                    break
                
                transfer = {
                    'tx_hash': item['tx_hash'],
                    'timestamp': item['timestamp'],
                    'from_address': item['from']['hash'],
                    'to_address': item['to']['hash'],
                    'value': float(Decimal(item['total']['value']) / Decimal('1e18')),
                    'method': item.get('method', ''),
                    'log_index': item.get('log_index', '0')
                }
                new_transactions.append(transfer)

            print(f"{len(new_transactions)} 件の新しいトランザクションを処理します")
            # 新しいトランザクションを逆順（古い順）にしてデータベースに挿入
            for transfer in reversed(new_transactions):
                if insert_normalized_data(conn, transfer):
                    new_records_count += 1

            if new_transactions:  # 新しいトランザクションがある場合のみ検証
                verification_result = verify_data_update(conn, new_transactions)
                if not verification_result['success']:
                    print("\n警告: データ更新の検証で問題が検出されました")
                    print(verification_result['verification_details'])
                    if verification_result['missing_transactions']:
                        print("失敗したトランザクション:")
                        for tx_hash in verification_result['missing_transactions']:
                            print(f"- {tx_hash}")
                    print()  # 空行を追加して見やすく

            if not new_transactions:
                # 新しいトランザクションがない場合はループを終了
                break

            if 'next_page_params' in data and data['next_page_params'] is not None:
                params.update(data['next_page_params'])
                print("次のページのデータを取得します")
                time.sleep(1)  # APIレート制限を考慮
            else:
                print("すべてのデータを取得しました")
                break

    except requests.exceptions.RequestException as e:
        print(f"APIリクエスト中にエラーが発生しました: {e}")
    finally:
        conn.close()

    print(f"合計 {requests_count} 回のAPIリクエストを送信しました")
    print(f"{new_records_count} 件の新しいトランザクションをデータベースに追加しました")

    return requests_count, new_records_count

def verify_data_update(conn: sqlite3.Connection, new_transactions: list) -> dict:
    """
    データベースの更新を検証する
    
    Returns:
        dict: 検証結果を含む辞書
        {
            'success': bool,
            'total_expected': int,
            'total_inserted': int,
            'missing_transactions': list,
            'verification_details': str
        }
    """
    verification_result = {
        'success': False,
        'total_expected': len(new_transactions),
        'total_inserted': 0,
        'missing_transactions': [],
        'verification_details': ''
    }
    
    try:
        cursor = conn.cursor()
        
        # 新しく追加されたトランザクションの検証
        for transfer in new_transactions:
            # トランザクションテーブルの確認
            cursor.execute("""
                SELECT COUNT(*) 
                FROM transactions 
                WHERE tx_hash = ? AND timestamp = ?
            """, (transfer['tx_hash'], transfer['timestamp']))
            tx_exists = cursor.fetchone()[0]
            
            # transfer_detailsテーブルの確認
            cursor.execute("""
                SELECT COUNT(*) 
                FROM transfer_details 
                WHERE tx_hash = ? 
                AND from_address = ? 
                AND to_address = ? 
                AND value = ?
                AND method = ?
                AND log_index = ?
            """, (
                transfer['tx_hash'],
                transfer['from_address'],
                transfer['to_address'],
                transfer['value'],
                transfer['method'],
                transfer['log_index']
            ))
            details_exist = cursor.fetchone()[0]
            
            if not (tx_exists and details_exist):
                verification_result['missing_transactions'].append(transfer['tx_hash'])
            else:
                verification_result['total_inserted'] += 1
        
        # 結果の集計
        verification_result['success'] = (
            verification_result['total_expected'] == 
            verification_result['total_inserted']
        )
        
        verification_result['verification_details'] = (
            f"期待された更新数: {verification_result['total_expected']}\n"
            f"実際の更新数: {verification_result['total_inserted']}\n"
            f"失敗した更新: {len(verification_result['missing_transactions'])}"
        )
        
    except Exception as e:
        verification_result['verification_details'] = f"検証中にエラーが発生: {str(e)}"
        verification_result['success'] = False
    
    return verification_result

def check_database_integrity(db_file: str) -> dict:
    """データベース全体の整合性をチェックする"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    integrity_result = {
        'success': True,
        'issues_found': [],
        'summary': {}
    }
    
    try:
        # 1. トランザクションとtransfer_detailsの整合性チェック
        cursor.execute("""
            SELECT t.tx_hash
            FROM transactions t
            LEFT JOIN transfer_details td ON t.tx_hash = td.tx_hash
            WHERE td.tx_hash IS NULL
        """)
        orphaned_transactions = cursor.fetchall()
        
        # 2. 重複チェック
        cursor.execute("""
            SELECT tx_hash, COUNT(*)
            FROM transfer_details
            GROUP BY tx_hash, from_address, to_address, value, method, log_index
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        # 結果の集計
        integrity_result['summary'] = {
            'total_transactions': cursor.execute("SELECT COUNT(*) FROM transactions").fetchone()[0],
            'total_transfer_details': cursor.execute("SELECT COUNT(*) FROM transfer_details").fetchone()[0],
            'orphaned_transactions': len(orphaned_transactions),
            'duplicate_records': len(duplicates)
        }
        
        if orphaned_transactions or duplicates:
            integrity_result['success'] = False
            integrity_result['issues_found'].extend([
                f"孤立したトランザクション: {len(orphaned_transactions)}件",
                f"重複レコード: {len(duplicates)}件"
            ])
    
    except Exception as e:
        integrity_result['success'] = False
        integrity_result['issues_found'].append(f"チェック中にエラー: {str(e)}")
    
    finally:
        conn.close()
    
    # 結果を表示
    print("\nデータベース整合性チェック結果:")
    print("-" * 40)
    print(f"チェック成功: {'✓' if integrity_result['success'] else '✗'}")
    print("\n集計:")
    print(f"総トランザクション数: {integrity_result['summary']['total_transactions']:,}")
    print(f"総転送詳細レコード数: {integrity_result['summary']['total_transfer_details']:,}")
    print(f"孤立トランザクション: {integrity_result['summary']['orphaned_transactions']:,}")
    print(f"重複レコード: {integrity_result['summary']['duplicate_records']:,}")
    
    if integrity_result['issues_found']:
        print("\n検出された問題:")
        for issue in integrity_result['issues_found']:
            print(f"- {issue}")
    else:
        print("\n問題は検出されませんでした。")
    
    return integrity_result

def run_update():
    requests_count, new_records_count = update_db_from_api("data/processed/geek_transfers.db")
    print(f"処理完了: {requests_count} 回のリクエスト, {new_records_count} 件の新規トランザクション")
    # adjusted_daily_balances_calculator_old.run_update()

    return requests_count, new_records_count

if __name__ == "__main__":
    run_update()
    check_database_integrity("data/processed/geek_transfers.db")
    # conn = get_db_connection("data/processed/geek_transfers.db")    
    # create_normalized_tables(conn)
    # conn.close()
