import mysql.connector
import pandas as pd
    
class DatabaseClient:
    """データベースアクセスを管理するクライアント"""
    
    def __init__(self):
        self.config = {
           
        }
  

    def get_connection(self):
        return mysql.connector.connect(**self.config)


    def execute(self, query: str) -> None:
        """DDLを実行"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()

    def execute_params(self, query: str, params: tuple = ()) -> None:
        """更新系クエリを実行"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor

    def query_to_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す"""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
        
    def query_to_df_with_address_date_index(self, query: str, params: tuple = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す"""
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index(['address', 'date'])
            return df
    
   
    
    def fetch_one(self, query: str) -> tuple:
        """1行だけ取得"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchone()

        
    def fetch_all(self, query: str) -> list:
        """全ての行を取得"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
            


