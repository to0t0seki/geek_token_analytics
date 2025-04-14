import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
from dotenv import load_dotenv
    
class Psycopg2DatabaseClient:
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
            with self.get_connection() as conn:
                return pd.read_sql_query(query, conn, params=params)
        
    
    def fetch_one(self, query: str) -> tuple:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchone()

        
    def fetch_all(self, query: str, params = None) -> list:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if params is None:
                        cursor.execute(query)
                    else:
                        cursor.execute(query, params)
                    return cursor.fetchall()
                
    def executemany(self, query: str, params_list: list) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                if cursor.rowcount == len(params_list):
                    return cursor.rowcount
                raise ValueError(f"データを挿入できませんでした: {cursor.rowcount}")
            

class SqlAlchemyDatabaseClient:
    """SQLAlchemyを使用したデータベースアクセスを管理するクライアント"""
    
    def __init__(self):
        load_dotenv()
        
        # データベース接続情報の設定
        db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DATABASE')}"
        
        # SQLAlchemyエンジンの作成
        self.engine = create_engine(db_url)
        
        # セッションファクトリの作成
        self.Session = sessionmaker(bind=self.engine)
    
    def execute(self, query: str, params: tuple = None) -> int:
        """SQLクエリを実行し、影響を受けた行数を返す"""
        with self.Session() as session:
            if params is None:
                result = session.execute(text(query))
            else:
                result = session.execute(text(query), params)
            session.commit()
            return result.rowcount
    
    def query_to_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """SQLクエリを実行し、結果をPandasのDataFrameとして返す"""
        with self.Session() as session:
            if params is None:
                result = session.execute(text(query))
            else:
                result = session.execute(text(query), params)
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    
    def fetch_one(self, query: str) -> tuple:
        """SQLクエリを実行し、最初の行を返す"""
        with self.Session() as session:
            result = session.execute(text(query))
            return result.fetchone()
    
    def fetch_all(self, query: str, params: tuple = None) -> list:
        """SQLクエリを実行し、すべての行を返す"""
        with self.Session() as session:
            if params is None:
                result = session.execute(text(query))
            else:
                result = session.execute(text(query), params)
            return result.fetchall()
    
    def executemany(self, query: str, params_list: list) -> int:
        """複数のパラメータセットでSQLクエリを実行する"""
        with self.Session() as session:
            result = session.execute(text(query), params_list)
            session.commit()
            rowcount = result.rowcount
            if rowcount == len(params_list):
                return rowcount
            raise ValueError(f"データを挿入できませんでした: {rowcount}")
        

# アダプタークラス（インターフェースを維持）
class DatabaseClient:
    def __init__(self, use_sqlalchemy=True):
        if use_sqlalchemy:
            self._client = SqlAlchemyDatabaseClient()
        else:
            self._client = Psycopg2DatabaseClient()
    
    # 既存のメソッドを委譲
    def execute(self, query, params=None):
        return self._client.execute(query, params)
    
    def query_to_df(self, query, params=None):
        return self._client.query_to_df(query, params)
    
    def fetch_one(self, query):
        return self._client.fetch_one(query)
    
    def fetch_all(self, query, params=None):
        return self._client.fetch_all(query, params)
    
    def executemany(self, query, params_list):
        return self._client.executemany(query, params_list)


