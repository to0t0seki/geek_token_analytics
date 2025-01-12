from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

class DatabaseClient:
    """データベースアクセスを管理するクライアント"""
    
    def __init__(self):
        load_dotenv()
        
        # 接続文字列の作成
        self.db_url = (
            f"postgresql://{os.getenv('POSTGRES_USER')}:"
            f"{os.getenv('POSTGRES_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:"
            f"{os.getenv('POSTGRES_PORT', 5432)}/"
            f"{os.getenv('POSTGRES_DATABASE')}"
        )
        
        # エンジンの作成
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        """セッションを取得するコンテキストマネージャー"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def execute(self, query: str, params: dict | None = None) -> int:
        """クエリを実行して影響を受けた行数を返す"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.rowcount

    def query_to_df(self, query: str, params: dict = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す"""
        return pd.read_sql_query(
            text(query), 
            self.engine, 
            params=params
        )
        
    def query_to_df_with_address_date_index(self, query: str, params: dict = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す（アドレスと日付でインデックス化）"""
        df = pd.read_sql_query(
            text(query), 
            self.engine, 
            params=params
        )
        df['date'] = pd.to_datetime(df['date'])
        return df.set_index(['address', 'date'])
    
    def fetch_one(self, query: str, params: dict = None) -> tuple:
        """1行だけ取得"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchone()
        
    def fetch_all(self, query: str, params: dict = None) -> list:
        """全ての行を取得"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return result.fetchall()