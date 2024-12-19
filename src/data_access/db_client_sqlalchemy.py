import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

class DatabaseClient:
    """データベースアクセスを管理するクライアント"""
    
    def __init__(self):
        # 接続情報を使用してSQLAlchemy engineを作成
        self.engine = create_engine(
            'mysql+mysqlconnector://root:taka4586@localhost:13306/geek-database',
            pool_recycle=3600  # コネクションプールの再利用時間を設定
        )

    def execute_ddl(self, query: str) -> None:
        """DDLを実行"""
        with Session(self.engine) as session:
            session.execute(text(query))
            session.commit()

    def execute(self, query: str, params: tuple = ()) -> None:
        """更新系クエリを実行"""
        with Session(self.engine) as session:
            session.execute(text(query), params)
            session.commit()

    def query_to_df(self, query: str, params: tuple = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す"""
        return pd.read_sql_query(text(query), self.engine, params=params)
        
    def query_to_df_with_address_date_index(self, query: str, params: tuple = None) -> pd.DataFrame:
        """クエリを実行しDataFrameを返す（address, dateをインデックスに設定）"""
        import psutil
        process = psutil.Process()
        print(f"Memory before query: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        df = pd.read_sql_query(text(query), self.engine, params=params)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index(['address', 'date'])
        print(f"Memory after query: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        print(f"DataFrame size: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        return df
    
    def fetch_one(self, query: str) -> tuple:
        """1行だけ取得"""
        with Session(self.engine) as session:
            result = session.execute(text(query)).fetchone()
            return result
        
    def fetch_all(self, query: str) -> list:
        """全ての行を取得"""
        with Session(self.engine) as session:
            result = session.execute(text(query)).fetchall()
            return result