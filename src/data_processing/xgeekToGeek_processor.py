import sqlite3

def create_xgeek_to_geek_view(db_file: str) -> None:
    """xgeek_to_geekビューを作成する"""
    conn = sqlite3.connect(db_file)
    try:
        # 既存のテーブルまたはビューが存在する場合は削除
        conn.execute("DROP TABLE IF EXISTS xgeek_to_geek")
        conn.execute("DROP VIEW IF EXISTS xgeek_to_geek")
        
        # ビューの作成
        create_view = """
        CREATE VIEW xgeek_to_geek AS
        SELECT 
            td.id as transfer_detail_id,
            td.tx_hash,
            td.from_address,
            td.to_address,
            td.value,
            t.timestamp
        FROM transfer_details td
        JOIN transactions t ON td.tx_hash = t.tx_hash
        WHERE td.method = 'xgeekToGeek'
        """
        conn.execute(create_view)
        conn.commit()
        print("xgeek_to_geekビューを作成しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    db_file_path = 'data/processed/geek_transfers.db'
    create_xgeek_to_geek_view(db_file_path)