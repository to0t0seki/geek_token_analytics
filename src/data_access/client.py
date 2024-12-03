import sqlite3
import pandas as pd
    
class DatabaseClient:
    """データベースアクセスを管理するクライアント"""
    
    def __init__(self, db_file: str = 'data/processed/geek_transfers.db'):
        self.db_file = db_file

    def execute_ddl(self, query: str) -> None:
        """DDLを実行"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(query)
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
    
    def execute(self, query: str, params: tuple = None) -> None:
        """更新系クエリを実行"""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(query, params)
            conn.commit()
    
    def fetch_one(self, query: str) -> tuple:
        """1行だけ取得"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            return cursor.execute(query).fetchone()
        
    def execute_many(self, query: str, params_list: list) -> None:
        """更新系クエリを実行"""

        if not params_list:
            raise ValueError("params_list is required")
        
        for i,params in enumerate(params_list):
            if None in params:
                raise ValueError(f"params_list[{i}] is None")
            if any(param == '' for param in params):
                raise ValueError(f"params_list[{i}] contains empty string")

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            inserted_rows = cursor.rowcount
            conn.commit()
            return inserted_rows
