import sqlite3
import pandas as pd
    
class DatabaseClient:
    """データベースアクセスを管理するクライアント"""
    
    def __init__(self, db_file: str = 'data/processed/geek_transfers.db'):
        self.db_file = db_file
    
    def query_to_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す"""
        with sqlite3.connect(self.db_file) as conn:
            return pd.read_sql_query(query, conn, params=params)
        
    def query_to_df_with_address_date_index(self, query: str) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す"""
        with sqlite3.connect(self.db_file) as conn:
            df = pd.read_sql_query(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index(['address', 'date'])
        return df
    
    def execute(self, query: str) -> None:
        """更新系クエリを実行"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(query)
            conn.commit()
    
    def fetch_one(self, query: str) -> tuple:
        """1行だけ取得"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            return cursor.execute(query).fetchone()