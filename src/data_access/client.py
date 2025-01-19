import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
    
class DatabaseClient:
    """データベースアクセスを管理するクライアント"""
    
    def __init__(self):

        load_dotenv()
        self.config = {
           'host': os.getenv('POSTGRES_HOST'),
           'user': os.getenv('POSTGRES_USER'),
           'password': os.getenv('POSTGRES_PASSWORD'),
           'database': os.getenv('POSTGRES_DATABASE'),
           'port': int(os.getenv('POSTGRES_PORT', 5432))
        }
  

    def get_connection(self):
        return psycopg2.connect(**self.config)


    def execute(self, query: str, params: tuple| None = None) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if params is None:  
                    cursor.execute(query)
                else:
                    cursor.execute(query, params)
                return cursor.rowcount

    def query_to_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す"""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)
        
    
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
            


