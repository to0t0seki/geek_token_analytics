import json
from decimal import Decimal
import pandas as pd
import sqlite3

# pandas の表示オプションを設定
pd.set_option('display.max_columns', None)  # すべての列を表示
pd.set_option('display.width', None)        # 表示幅の制限を解除
pd.set_option('display.max_colwidth', None) # 列の幅の制限を解除

def get_daily_export_token(db_file: str) -> pd.DataFrame:
    conn = sqlite3.connect(db_file)
    query = """
    SELECT 
        *
    FROM 
        export_token
    WHERE
        to_address != '0x8ACEA4FEBB072dE21C0bc24E6303D19CCEa5fB62'
    ORDER BY 
        timestamp ASC
    LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = get_daily_export_token('data/processed/geek_transfers.db')

# 見やすく整形して表示
print("\n最古の10件のトランザクション:")
print("=" * 80)  # 区切り線
print(df.to_string(index=False))  # indexを非表示にして全データを表示

# または特定のカラムのみ表示する場合：
print("\n特定のカラムのみ表示:")
print("=" * 80)
columns_to_show = ['transfer_detail_id', 'from_address', 'to_address', 'value', 'timestamp']
print(df[columns_to_show].to_string(index=False))